#  Copyright (c) 2015-2022 by Rocky Bernstein
#  Copyright (c) 2005 by Dan Pascu <dan@windowmaker.org>
#  Copyright (c) 2000-2002 by hartmut Goebel <h.goebel@crazy-compilers.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Python 3.10 bytecode scanner/deparser base.

Also we *modify* the instruction sequence to assist deparsing code.
For example:
 -  we add "COME_FROM" instructions to help in figuring out
    conditional branching and looping.
 -  LOAD_CONSTs are classified further into the type of thing
    they load:
      lambda's, genexpr's, {dict,set,list} comprehension's,
 -  PARAMETER counts appended  {CALL,MAKE}_FUNCTION, BUILD_{TUPLE,SET,SLICE}

Finally we save token information.
"""

from typing import Any, Dict

from control_flow.augment_disasm import augment_instructions
from control_flow.bb import basic_blocks
from control_flow.cfg import ControlFlowGraph
from control_flow.dominators import DominatorTree, dfs_forest, build_dom_set

from xdis import iscode, instruction_size
from xdis.bytecode import _get_const_info

from decompile_ng.scanner import Token, Scanner
import xdis

# Get all the opcodes into globals
import xdis.opcodes.opcode_310 as op3

import sys

globals().update(op3.opmap)

def get_jump_val(jump_arg: int, version: tuple) -> int:
    return jump_arg * 2 if version[:2] >= (3, 10)  else jump_arg

class Scanner310Base(Scanner):
    def __init__(self, version: float, show_asm=None, debug=False, is_pypy=False):
        super(Scanner310Base, self).__init__(version, show_asm, is_pypy)
        self.debug = debug
        self.is_pypy = is_pypy
        self.version = version

        # Create opcode classification sets
        # Note: super initilization above initializes self.opc

        # Ops that start SETUP_ ... We will COME_FROM with these names
        # Some blocks and END_ statements. And they can start
        # a new statement
        setup_ops = [self.opc.SETUP_FINALLY]
        self.setup_ops_no_loop = frozenset(setup_ops)

        # Add back these opcodes which help us detect "break" and
        # "continue" statements via parsing.
        self.opc.BREAK_LOOP = 80
        self.opc.CONTINUE_LOOP = 119
        pass

        setup_ops.append(self.opc.SETUP_WITH)
        self.setup_ops = frozenset(setup_ops)

        self.pop_jump_tf = frozenset([self.opc.PJIF, self.opc.PJIT])
        self.not_continue_follow = ("END_FINALLY", "POP_BLOCK")

        # Opcodes that can start a statement.
        statement_opcodes = [
            self.opc.POP_BLOCK,
            self.opc.STORE_FAST,
            self.opc.DELETE_FAST,
            self.opc.STORE_DEREF,
            self.opc.STORE_GLOBAL,
            self.opc.DELETE_GLOBAL,
            self.opc.STORE_NAME,
            self.opc.DELETE_NAME,
            self.opc.STORE_ATTR,
            self.opc.DELETE_ATTR,
            self.opc.STORE_SUBSCR,
            self.opc.POP_TOP,
            self.opc.DELETE_SUBSCR,
            self.opc.RETURN_VALUE,
            self.opc.RAISE_VARARGS,
            self.opc.PRINT_EXPR,
            self.opc.JUMP_ABSOLUTE,
            # These are phony for 3.8+
            self.opc.BREAK_LOOP,
            self.opc.CONTINUE_LOOP,
        ]

        self.statement_opcodes = frozenset(statement_opcodes) | self.setup_ops_no_loop

        # Opcodes that can start a "store" non-terminal.
        # FIXME: JUMP_ABSOLUTE is weird. What's up with that?
        self.designator_ops = frozenset(
            [
                self.opc.STORE_FAST,
                self.opc.STORE_NAME,
                self.opc.STORE_GLOBAL,
                self.opc.STORE_DEREF,
                self.opc.STORE_ATTR,
                self.opc.STORE_SUBSCR,
                self.opc.UNPACK_SEQUENCE,
                self.opc.JUMP_ABSOLUTE,
                self.opc.UNPACK_EX,
            ]
        )

        self.jump_if_pop = frozenset(
            [self.opc.JUMP_IF_FALSE_OR_POP, self.opc.JUMP_IF_TRUE_OR_POP]
        )

        self.pop_jump_if_pop = frozenset(
            [
                self.opc.JUMP_IF_FALSE_OR_POP,
                self.opc.JUMP_IF_TRUE_OR_POP,
                self.opc.POP_JUMP_IF_TRUE,
                self.opc.POP_JUMP_IF_FALSE,
            ]
        )
        # Not really a set, but still clasification-like
        self.statement_opcode_sequences = [
            (self.opc.POP_JUMP_IF_FALSE, self.opc.JUMP_FORWARD),
            (self.opc.POP_JUMP_IF_FALSE, self.opc.JUMP_ABSOLUTE),
            (self.opc.POP_JUMP_IF_TRUE, self.opc.JUMP_FORWARD),
            (self.opc.POP_JUMP_IF_TRUE, self.opc.JUMP_ABSOLUTE),
        ]

        # FIXME: remove this and use instead info from xdis.
        # Opcodes that take a variable number of arguments
        # (expr's)
        varargs_ops = set(
            [
                self.opc.BUILD_LIST,
                self.opc.BUILD_TUPLE,
                self.opc.BUILD_SET,
                self.opc.BUILD_SLICE,
                self.opc.BUILD_MAP,
                self.opc.UNPACK_SEQUENCE,
                self.opc.RAISE_VARARGS,
            ]
        )

        varargs_ops.add(self.opc.CALL_METHOD)
        varargs_ops.add(self.opc.BUILD_CONST_KEY_MAP)
        # Below is in bit order, "default = bit 0, closure = bit 3
        self.MAKE_FUNCTION_FLAGS = tuple(
            """
            default keyword-only annotation closure""".split()
        )

        self.varargs_ops = frozenset(varargs_ops)
        # FIXME: remove the above in favor of:
        # self.varargs_ops = frozenset(self.opc.hasvargs)
        return

    def ingest(self, co, classname=None, code_objects={}, show_asm=None):
        """
        Pick out tokens from an decompile_ng code object, and transform them,
        returning a list of decompyle-ng Token's.

        The transformations are made to assist the deparsing grammar.
        Specificially:
           -  various types of LOAD_CONST's are categorized in terms of what they load
           -  COME_FROM instructions are added to assist parsing control structures
           -  MAKE_FUNCTION and FUNCTION_CALLS append the number of positional arguments
           -  some EXTENDED_ARGS instructions are removed

        Also, when we encounter certain tokens, we add them to a set which will cause custom
        grammar rules. Specifically, variable arg tokens like MAKE_FUNCTION or BUILD_LIST
        cause specific rules for the specific number of arguments they take.

        """
        def tokens_append(j, token):
            tokens.append(token)
            self.offset2tok_index[token.offset] = j
            j += 1
            assert j == len(tokens)
            return j


        bb_mgr = basic_blocks(co)
        if show_asm in ("both", "before"):
            for bb in bb_mgr.bb_list:
                print("\t", bb)
        cfg = ControlFlowGraph(bb_mgr)
        name = co.co_name
        if co.co_name.startswith("<"):
            name = name[1:]
        if co.co_name.endswith(">"):
            name = name[:-1]
        try:
            if show_asm in ("both", "before", "after"):
                dot_path = '/tmp/flow-%s.dot' % name
                png_path = '/tmp/flow-%s.png' % name
                open(dot_path, 'w').write(cfg.graph.to_dot(False))
                print("%s written" % dot_path)
                import os
                os.system("dot -Tpng %s > %s" % (dot_path, png_path))
            dt = DominatorTree(cfg)
            cfg.dom_tree = dt.tree(False)
            dfs_forest(cfg.dom_tree, False)
            build_dom_set(cfg.dom_tree, False)
            if show_asm in ("both", "before", "after"):
                dot_path = '/tmp/flow-dom-%s.dot' % name
                png_path = '/tmp/flow-dom-%s.png' % name
                open(dot_path, 'w').write(cfg.dom_tree.to_dot())
                print("%s written" % dot_path)
                os.system("dot -Tpng %s > %s" % (dot_path, png_path))

            # FIXME? Do we need reverse dominators?
            cfg.pdom_tree = dt.tree(True)
            dfs_forest(cfg.pdom_tree, True)
            build_dom_set(cfg.pdom_tree, True)
            if show_asm in ("both", "before"):
                dot_path = '/tmp/flow-pdom-%s.dot' % name
                png_path = '/tmp/flow-pdom-%s.png' % name
                open(dot_path, 'w').write(cfg.pdom_tree.to_dot())
                print("%s written" % dot_path)
                os.system("dot -Tpng %s > %s" % (dot_path, png_path))

            self.insts = augment_instructions(co, cfg, self.opc.version_tuple)
            if show_asm in ("both", "before"):
                print('=' * 30)
                for inst in self.insts:
                    print(inst.disassemble(self.opc))

        except:
            import traceback
            traceback.print_exc()
            print("Unexpected error:", sys.exc_info()[0])
            print("%s had an error" % name)
            return ""

        if not show_asm:
            show_asm = self.show_asm

        bytecode = self.build_instructions(co)

        # show_asm = 'both'
        if show_asm in ("both", "before"):
            for instr in bytecode.get_instructions(co):
                print(instr.disassemble(self.opc))

        # "customize" is in the process of going away here
        customize = {}

        if self.is_pypy:
            customize["PyPy"] = 0

        # Scan for assertions. Later we will
        # turn 'LOAD_GLOBAL' to 'LOAD_ASSERT'.
        # 'LOAD_ASSERT' is used in assert statements.
        self.load_asserts = set()

        # list of tokens/instructions
        tokens = []
        self.offset2tok_index = {}

        n = len(self.insts)
        for i, inst in enumerate(self.insts):

            # We need to detect the difference between:
            #   raise AssertionError
            #  and
            #   assert ...
            # If we have a JUMP_FORWARD after the
            # RAISE_VARARGS then we have a "raise" statement
            # else we have an "assert" statement.
            assert_can_follow = inst.opname == "POP_JUMP_IF_TRUE" and i + 1 < n
            if assert_can_follow:
                next_inst = self.insts[i + 1]
                if (
                    next_inst.opname == "LOAD_GLOBAL"
                    and next_inst.argval == "AssertionError"
                ):
                    jump_val = get_jump_val(inst.argval, self.version)
                    raise_idx = self.offset2inst_index[self.prev_op[jump_val]]
                    raise_inst = self.insts[raise_idx]
                    if raise_inst.opname.startswith("RAISE_VARARGS"):
                        self.load_asserts.add(next_inst.offset)
                    pass
                pass

        # Operand values in Python wordcode are small. As a result,
        # there are these EXTENDED_ARG instructions - way more than
        # before 3.6. These parsing a lot of pain.

        # # To simplify things we want to untangle this. We also
        # # do this loop before we compute jump targets.
        # for i, inst in enumerate(self.insts):

        #     # One artifact of the "too-small" operand problem, is that
        #     # some backward jumps, are turned into forward jumps to another
        #     # "extended arg" backward jump to the same location.
        #     if inst.opname == "JUMP_FORWARD":
        #         from trepan.api import debug; debug()
        #         jump_val = get_jump_val(inst.argval, self.version)
        #         jump_inst = self.insts[self.offset2inst_index[jump_val]]
        #         if jump_inst.has_extended_arg and jump_inst.opname.startswith("JUMP"):
        #             # Create comination of the jump-to instruction and
        #             # this one. Keep the position information of this instruction,
        #             # but the operator and operand properties come from the other
        #             # instruction
        #             self.insts[i] = Instruction(
        #                 jump_inst.opname,
        #                 jump_inst.opcode,
        #                 jump_inst.optype,
        #                 jump_inst.inst_size,
        #                 jump_inst.arg,
        #                 jump_inst.argval,
        #                 jump_inst.argrepr,
        #                 jump_inst.has_arg,
        #                 inst.offset,
        #                 inst.starts_line,
        #                 inst.is_jump_target,
        #                 inst.has_extended_arg,
        #             )

        # Get jump targets
        # Format: {target offset: [jump offsets]}
        # jump_targets = self.find_jump_targets(show_asm)
        # print("XXX2", jump_targets)

        last_op_was_break = False

        j = 0
        for i, inst in enumerate(self.insts):

            argval = inst.argval
            op = inst.opcode

            if inst.opname == "EXTENDED_ARG":
                # FIXME: The EXTENDED_ARG is used to signal annotation
                # parameters
                if i + 1 < n and self.insts[i + 1].opcode != self.opc.MAKE_FUNCTION:
                    continue

            pattr = inst.argrepr
            opname = inst.opname

            if op in self.opc.CONST_OPS:
                const = argval
                if iscode(const):
                    if const.co_name == "<lambda>":
                        assert opname == "LOAD_CONST"
                        opname = "LOAD_LAMBDA"
                    elif const.co_name == "<genexpr>":
                        opname = "LOAD_GENEXPR"
                    elif const.co_name == "<dictcomp>":
                        opname = "LOAD_DICTCOMP"
                    elif const.co_name == "<setcomp>":
                        opname = "LOAD_SETCOMP"
                    elif const.co_name == "<listcomp>":
                        opname = "LOAD_LISTCOMP"
                    else:
                        opname = "LOAD_CODE"
                    # verify() uses 'pattr' for comparison, since 'attr'
                    # now holds Code(const) and thus can not be used
                    # for comparison (todo: think about changing this)
                    # pattr = 'code_object @ 0x%x %s->%s' %\
                    # (id(const), const.co_filename, const.co_name)
                    pattr = "<code_object " + const.co_name + ">"
                elif isinstance(const, str):
                    opname = "LOAD_STR"
                else:
                    if isinstance(inst.arg, int) and inst.arg < len(co.co_consts):
                        argval, _ = _get_const_info(inst.arg, co.co_consts)
                    # Why don't we use _ above for "pattr" rather than "const"?
                    # This *is* a little hoaky, but we have to coordinate with
                    # other parts like n_LOAD_CONST in pysource.py for example.
                    pattr = const
                    pass
            elif opname == "IMPORT_NAME":
                if "." in inst.argval:
                    opname = "IMPORT_NAME_ATTR"
                    pass
            elif opname in ("MAKE_FUNCTION", "MAKE_CLOSURE"):
                flags = argval
                opname = "MAKE_FUNCTION_%d" % (flags)
                attr = []
                for flag in self.MAKE_FUNCTION_FLAGS:
                    bit = flags & 1
                    attr.append(bit)
                    flags >>= 1
                attr = attr[:4]  # remove last value: attr[5] == False
                j = tokens_append(
                    j,
                    Token(
                        opname=opname,
                        attr=attr,
                        pattr=pattr,
                        offset=inst.offset,
                        linestart=inst.starts_line,
                        op=op,
                        has_arg=inst.has_arg,
                        opc=self.opc,
                        has_extended_arg=inst.has_extended_arg,
                    ),
                )
                continue
            elif op in self.varargs_ops:
                pos_args = argval
                if self.is_pypy and not pos_args and opname == "BUILD_MAP":
                    opname = "BUILD_MAP_n"
                else:
                    opname = "%s_%d" % (opname, pos_args)

            elif self.is_pypy and opname == "JUMP_IF_NOT_DEBUG":
                # The value in the dict is in special cases in semantic actions, such
                # as JUMP_IF_NOT_DEBUG. The value is not used in these cases, so we put
                # in arbitrary value 0.
                customize[opname] = 0
            elif opname == "UNPACK_EX":
                # FIXME: try with scanner and parser by
                # changing argval
                before_args = argval & 0xFF
                after_args = (argval >> 8) & 0xFF
                pattr = "%d before vararg, %d after" % (before_args, after_args)
                argval = (before_args, after_args)
                opname = "%s_%d+%d" % (opname, before_args, after_args)

            elif op == self.opc.JUMP_ABSOLUTE:
                #  Refine JUMP_ABSOLUTE further in into:
                #
                # * "JUMP_BACK"    - which are are used in loops. This is sometimes
                #                   found at the end of a looping construct
                # * "BREAK_LOOP"  - which are are used to break loops.
                # * "CONTINUE"    - jumps which may appear in a "continue" statement.
                #                   It is okay to confuse this with JUMP_BACK. The
                #                   grammar should tolerate this.
                # * "JUMP_FORWARD - forward jumps that are not BREAK_LOOP jumps.
                #
                # The loop-type and continue-type jumps will help us
                # classify loop boundaries The continue-type jumps
                # help us get "continue" statements with would
                # otherwise be turned into a "pass" statement because
                # JUMPs are sometimes ignored in rules as just
                # boundary overhead. Again, in comprehensions we might
                # sometimes classify JUMP_BACK as CONTINUE, but that's
                # okay since grammar rules should tolerate that.
                pattr = argval
                target = inst.argval
                if target <= inst.offset:
                    next_opname = self.insts[i + 1].opname

                    # 'Continue's include jumps to loops that are not
                    # and the end of a block which follow with POP_BLOCK and COME_FROM_LOOP.
                    # If the JUMP_ABSOLUTE is to a FOR_ITER and it is followed by another JUMP_FORWARD
                    # then we'll take it as a "continue".
                    is_continue = (
                        self.insts[self.offset2inst_index[target]].opname == "FOR_ITER"
                        and self.insts[i + 1].opname == "JUMP_FORWARD"
                    )

                    if self.version < (3, 8) and (
                        is_continue
                        or (
                            inst.offset in self.stmts
                            and (
                                inst.starts_line
                                and next_opname not in self.not_continue_follow
                            )
                        )
                    ):
                        opname = "CONTINUE"
                    else:
                        opname = "JUMP_BACK"
                        # FIXME: this is a hack to catch stuff like:
                        #   if x: continue
                        # the "continue" is not on a new line.
                        # There are other situations where we don't catch
                        # CONTINUE as well.
                        if tokens[-1].kind == "JUMP_BACK" and tokens[-1].attr <= argval:
                            if tokens[-2].kind == "BREAK_LOOP":
                                del tokens[-1]
                            else:
                                # intern is used because we are changing the *previous* token.
                                # A POP_TOP suggests a "break" rather than a "continue"?
                                if tokens[-2] == "POP_TOP":
                                    tokens[-1].kind = sys.intern("BREAK_LOOP")
                                else:
                                    tokens[-1].kind = sys.intern("CONTINUE")
                                    pass
                                pass
                            pass
                    if last_op_was_break and opname == "CONTINUE":
                        last_op_was_break = False
                        continue
                    pass
                else:
                    opname = "JUMP_FORWARD"

            elif opname.startswith("POP_JUMP_IF_") and not inst.jumps_forward():
                opname += "_BACK"
            elif inst.offset in self.load_asserts:
                opname = "LOAD_ASSERT"

            last_op_was_break = opname == "BREAK_LOOP"
            j = tokens_append(
                j,
                Token(
                    opname=opname,
                    optype = inst.optype,
                    attr=argval,
                    pattr=pattr,
                    offset=inst.offset,
                    linestart=inst.starts_line,
                    op=op,
                    has_arg=inst.has_arg,
                    opc=self.opc,
                    has_extended_arg=inst.has_extended_arg,
                    basic_block=inst.basic_block,
                    dominator=inst.dominator,
                ),
            )
            pass

        if show_asm in ("both", "after"):
            for t in tokens:
                print(t.format(line_prefix=""))
            print()
        return tokens, customize

    def build_statement_indices(self):
        code = self.code
        start = 0
        end = codelen = len(code)

        # Compose preliminary list of indices with statements,
        # using plain statement opcodes
        prelim = self.inst_matches(start, end, self.statement_opcodes)

        # Initialize final container with statements with
        # preliminary data
        stmts = self.stmts = set(prelim)

        # Same for opcode sequences
        pass_stmts = set()
        for sequence in self.statement_opcode_sequences:
            for i in self.op_range(start, end - (len(sequence) + 1)):
                match = True
                for elem in sequence:
                    if elem != code[i]:
                        match = False
                        break
                    i += instruction_size(code[i], self.opc)

                if match is True:
                    i = self.prev_op[i]
                    stmts.add(i)
                    pass_stmts.add(i)

        # Initialize statement list with the full data we've gathered so far
        if pass_stmts:
            stmt_offset_list = list(stmts)
            stmt_offset_list.sort()
        else:
            stmt_offset_list = prelim
        # 'List-map' which contains offset of start of
        # next statement, when op offset is passed as index
        self.next_stmt = slist = []
        last_stmt_offset = -1
        i = 0
        # Go through all statement offsets
        for stmt_offset in stmt_offset_list:
            # Process absolute jumps, but do not remove 'pass' statements
            # from the set
            if (
                code[stmt_offset] == self.opc.JUMP_ABSOLUTE
                and stmt_offset not in pass_stmts
            ):
                # If absolute jump occurs in forward direction or it takes off from the
                # same line as previous statement, this is not a statement
                # FIXME: 0 isn't always correct
                target = self.get_target(stmt_offset)
                if (
                    target > stmt_offset
                    or self.lines[last_stmt_offset].l_no == self.lines[stmt_offset].l_no
                ):
                    stmts.remove(stmt_offset)
                    continue
                # Rewing ops till we encounter non-JUMP_ABSOLUTE one
                j = self.prev_op[stmt_offset]
                while code[j] == self.opc.JUMP_ABSOLUTE:
                    j = self.prev_op[j]
                # If we got here, then it's list comprehension which
                # is not a statement too
                if code[j] == self.opc.LIST_APPEND:
                    stmts.remove(stmt_offset)
                    continue
            # Exclude ROT_TWO + POP_TOP
            elif (
                code[stmt_offset] == self.opc.POP_TOP
                and code[self.prev_op[stmt_offset]] == self.opc.ROT_TWO
            ):
                stmts.remove(stmt_offset)
                continue
            # Exclude FOR_ITER + designators
            elif code[stmt_offset] in self.designator_ops:
                j = self.prev_op[stmt_offset]
                while code[j] in self.designator_ops:
                    j = self.prev_op[j]
                if code[j] == self.opc.FOR_ITER:
                    stmts.remove(stmt_offset)
                    continue
            # Add to list another list with offset of current statement,
            # equal to length of previous statement
            slist += [stmt_offset] * (stmt_offset - i)
            last_stmt_offset = stmt_offset
            i = stmt_offset
        # Finish filling the list for last statement
        slist += [codelen] * (codelen - len(slist))

if __name__ == "__main__":
    from xdis.version_info import PYTHON_VERSION_TRIPLE, version_tuple_to_str

    unsupported_version = False
    if len(sys.argv) > 1:
        from xdis.load import load_module
        version_tuple, ts, maghic_int, co, is_pypy, source_size, sip_hash = load_module(sys.argv[1])
        if version_tuple[:2] not in ((3, 10),):
            unsupported_version = True

    else:
        import inspect

        co = inspect.currentframe().f_code  # type: ignore

    if PYTHON_VERSION_TRIPLE[:2] < (3, 10):
        unsupported_version = True
    else:
        tokens, customize = Scanner310Base(PYTHON_VERSION_TRIPLE).ingest(co, show_asm="both")

    if unsupported_version:
        print(
            f"Need to be Python 3.10 to demo; I am version {version_tuple_to_str()}."
        )
    pass
