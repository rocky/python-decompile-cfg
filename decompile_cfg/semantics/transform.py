#  Copyright (c) 2019-2023 by Rocky Bernstein

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

from decompile_cfg.show import maybe_show_tree
from copy import copy
from typing import Callable, Optional

from spark_parser import GenericASTTraversal, GenericASTTraversalPruningException

from decompile_cfg.semantics.helper import find_code_node
from decompile_cfg.parsers.treenode import SyntaxTree
from decompile_cfg.scanners.tok import NoneToken, Token
from decompile_cfg.semantics.consts import RETURN_NONE, ASSIGN_DOC_STRING


STRIPPED_NODES = (
    "and_or_expr1",
    "and_part",
    "bb_end_start",
    "block_join_end_final",
    "block_start",
    "branch_op",
    "comp_iter_outer",
    "expr_jitop",
    "expr_pjif",
    "expr_pjit",
    "for_loop",
    "or",
    "or_parts_pjit",
    "set_comp_func",
)


def is_docstring(node, version: str, co_consts) -> bool:
    """
    Build what would look like a docstring for this code and check to see
    if `node` matches that. Note that in the '==' comparision,
    line number checking is disabled.
    """
    return node == ASSIGN_DOC_STRING(co_consts[0], "LOAD_STR")


def is_not_docstring(call_stmt_node) -> bool:
    try:
        return (
            call_stmt_node == "call_stmt"
            and call_stmt_node[0][0] == "LOAD_STR"
            and call_stmt_node[1] == "POP_TOP"
        )
    except Exception:
        return False


class TreeTransform(GenericASTTraversal, object):
    def __init__(
        self,
        version: tuple,
        str_with_template: Callable,
        show_ast: Optional[dict] = None,
    ):
        self.showast = show_ast
        self.version = version
        self.str_with_template_for_later = str_with_template
        self.str_with_template = None
        return

    def maybe_show_tree(self, tree, phase: str, print_fn: Callable):
        if phase == "before":
            phase_name = "parse tree"
        else:
            phase_name = "transformed abstract tree"
            self.str_with_template = self.str_with_template_for_later
        if isinstance(self.showast, dict) and self.showast.get(phase, False):
            print_fn(f"""\n# ---- {phase_name}:\n """)
            maybe_show_tree(self, tree)

    def preorder(self, node=None):
        """Walk the tree in roughly 'preorder' (a bit of a lie explained below).
        For each node with typestring name *name* if the
        node has a method called n_*name*, call that before walking
        children.

        In typical use a node with children can call "preorder" in any
        order it wants which may skip children or order then in ways
        other than first to last.  In fact, this this happens.  So in
        this sense this function not strictly preorder.
        """
        if node is None:
            node = self.ast

        try:
            name = "n_" + self.typestring(node)
            if hasattr(self, name):
                func = getattr(self, name)
                node = func(node)
        except GenericASTTraversalPruningException:
            return

        if node.kind in STRIPPED_NODES:
            return self.strip_pseudo_ops(node)

        for i, kid in enumerate(node):
            node[i] = self.preorder(kid)
        return node

    def n_await_expr(self, node: SyntaxTree) -> SyntaxTree:
        """Here we check for await(await)"""

        expr = node[0]
        assert expr == "expr"
        if expr[0] == "await_expr":
            expr[0].transformed_by = "n_await_expr"
            return expr[0]
        return node

    def n_mkfunc(self, node: SyntaxTree) -> SyntaxTree:
        """If the function has a docstring (this is found in the code
        constants), pull that out and make it part of the syntax
        tree. When generating the source string that AST node rather
        than the code field is seen and used.
        """

        code = find_code_node(node, -3).attr

        mkfunc_pattr = node[-1].pattr
        if isinstance(mkfunc_pattr, tuple):
            assert isinstance(mkfunc_pattr, tuple)
            assert len(mkfunc_pattr, 4) and isinstance(mkfunc_pattr, int)
            is_closure = node[-1].pattr[3] != 0
        else:
            # FIXME: This is what we had before. It is hoaky and probably wrong.
            is_closure = mkfunc_pattr == "closure"

        if (
            (not is_closure)
            and len(code.co_consts) > 0
            and isinstance(code.co_consts[0], str)
        ):
            docstring_node = SyntaxTree(
                "docstring",
                [Token("LOAD_STR", has_arg=True, pattr=code.co_consts[0])],
                transformed_by="n_mkfunc",
            )
            node = SyntaxTree(
                "mkfunc",
                node[:-1] + [docstring_node, node[-1]],
                transformed_by="n_mkfunc",
            )

        return node

    # preprocess is used for handling chains of
    # if elif elif
    def n_if_and_elsestmt(self, node, preprocess=False):
        """
        Transformation involving if .. and ..: ..else statments.
        For example
          if ... and ...
          else
             if ...

        into:

          if ... and ...
          elif ...

          [else ...]

        where appropriate.
        """

        else_suite = node[4]
        assert else_suite == "else_suite"
        # See if we can DRY the rest with n_ifelsesmt

        n = else_suite[0]
        old_stmts = None
        else_suite_index = 1
        if len(n) and n[0] == "suite_stmts":
            n = n[0]

        while len(n) == 1 and n in ("_stmts", "stmt", "stmts"):
            n = n[0]

        if len(n) == 0:
            return node

        if n[0].kind in ("ifstmt",):
            n = n[0]
        else:
            if (
                len(n) > 1
                and isinstance(n[0], SyntaxTree)
                and 1 == len(n[0])
                and n[0] == "stmt"
                and n[1].kind == "stmt"
            ):
                else_suite_stmts = n[0]
            elif len(n) == 1:
                else_suite_stmts = n
            else:
                return node

            if else_suite_stmts[0].kind in (
                "ifstmt",
                "ifelsestmt",
            ):
                old_stmts = n
                n = else_suite_stmts[0]
            else:
                return node

        if n.kind == "last_stmt":
            n = n[0]
        if n.kind in ("ifstmt",):
            node.kind = "if_and_elifstmt"
            n.kind = "elifstmt"
            node.transformed_by = "n_if_and_elsestmt"
        elif n.kind in ("ifelsestmt", "ifelsestmtc", "ifelsestmtc"):
            node.kind = "if_and_elifstmt"
            self.n_ifelsestmt(n, preprocess=True)
            if n == "ifelifstmt":
                n.kind = "elifelifstmt"
                node.transformed_by = "n_if_and_elsestmt"
            elif n.kind in ("ifelsestmt", "ifelsestmtc"):
                n.kind = "elifelsestmt"
        if not preprocess:
            if old_stmts:
                if n.kind == "elifstmt":
                    trailing_else = SyntaxTree("stmts", old_stmts[1:])
                    if len(trailing_else):
                        # We use elifelsestmtr because it has 3 nodes
                        elifelse_stmt = SyntaxTree(
                            "elifelsestmtr", [n[0], n[else_suite_index], trailing_else]
                        )
                        node[3] = elifelse_stmt
                    else:
                        elif_stmt = SyntaxTree("elifstmt", [n[0], n[else_suite_index]])
                        node[3] = elif_stmt

                    node.transformed_by = "n_if_and_elsestmt"
                    pass
                else:
                    # Other cases for n.kind may happen here
                    pass
                pass
            return node

    def n_ifstmt(self, node: SyntaxTree) -> SyntaxTree:
        """Here we check if we can turn an `ifstmt` or 'iflaststmtc` into
        some kind of `assert` statement"""

        testexpr = node[0]

        if testexpr not in ("testexpr", "testexprc"):
            return node

        if node.kind in ("ifstmt", "ifstmtc"):
            ifstmts_jump = node[1]

            if ifstmts_jump == "ifstmts_jumpc" and ifstmts_jump[0] == "ifstmts_jump":
                ifstmts_jump = ifstmts_jump[0]
            elif ifstmts_jump not in ("ifstmts_jump", "ifstmts_jumpc"):
                return node
            stmts = ifstmts_jump[0]
        else:
            # iflaststmt{c,} works this way
            stmts = node[1]

        if stmts in ("c_stmts", "stmts", "stmts_opt") and len(stmts) == 1:
            raise_stmt = stmts[0]
            if raise_stmt != "raise_stmt1" and len(raise_stmt) > 0:
                raise_stmt = raise_stmt[0]

            testtrue_or_false = testexpr[0]
            if testtrue_or_false == "testexpr":
                testtrue_or_false = testtrue_or_false[0]

            if (
                raise_stmt == "raise_stmt1"
                and 1 <= len(testtrue_or_false) <= 2
                and raise_stmt.first_child().pattr == "AssertionError"
            ):
                if testtrue_or_false in ("testtrue", "testtruec"):
                    # Skip over the testtrue because because it would
                    # produce a "not" and we don't want that here.
                    assert_expr = testtrue_or_false[0]
                    jump_cond = NoneToken
                else:
                    assert testtrue_or_false in (
                        "testfalse",
                        "testfalsec",
                    ), testtrue_or_false
                    assert_expr = testtrue_or_false[0]
                    if assert_expr in ("and_not", "nand", "not_or", "and"):
                        # FIXME: come back to stuff like this
                        return node

                    if testtrue_or_false[0] == "expr_pjif":
                        jump_cond = testtrue_or_false[0][1]
                    else:
                        jump_cond = testtrue_or_false[1]
                    assert_expr.kind = "assert_expr"
                    pass

                expr = raise_stmt[0]
                RAISE_VARARGS_1 = raise_stmt[1]
                call = expr[0]
                if call == "call":
                    # ifstmt
                    #     0. testexpr
                    #         testtrue (2)
                    #             0. expr
                    #     1. _ifstmts_jump (2)
                    #         0. c_stmts
                    #             stmt
                    #                 raise_stmt1 (2)
                    #                     0. expr
                    #                         call (3)
                    #                     1. RAISE_VARARGS_1
                    # becomes:
                    # assert2 ::= assert_expr POP_JUMP_IF_TRUE LOAD_ASSERT expr RAISE_VARARGS_1 COME_FROM
                    if jump_cond in ("POP_JUMP_IF_TRUE", NoneToken):
                        kind = "assert2"
                    else:
                        # if jump_cond == "POP_JUMP_IF_FALSE":
                        #     # FIXME: We don't handle this kind of thing yet.
                        #     return node
                        kind = "assert2not"

                    LOAD_ASSERT = call[0].first_child()
                    if LOAD_ASSERT not in ("LOAD_ASSERT", "LOAD_GLOBAL"):
                        return node
                    if isinstance(call[1], SyntaxTree):
                        expr = call[1][0]
                        assert_expr.transformed_by = "n_ifstmt"
                        node = SyntaxTree(
                            kind,
                            [
                                assert_expr,
                                jump_cond,
                                LOAD_ASSERT,
                                expr,
                                RAISE_VARARGS_1,
                            ],
                            transformed_by="n_ifstmt",
                        )
                        pass
                    pass
                else:
                    # ifstmt
                    #   0. testexpr (2)
                    #      testtrue
                    #       0. expr
                    #   1. _ifstmts_jump (2)
                    #      0. c_stmts
                    #        stmts
                    #           raise_stmt1 (2)
                    #             0. expr
                    #                  LOAD_ASSERT
                    #             1.   RAISE_VARARGS_1
                    # becomes:
                    # assert ::= assert_expr POP_JUMP_IF_TRUE LOAD_ASSERT RAISE_VARARGS_1 COME_FROM
                    assert_expr.transformed_by = "n_ifstmt"
                    if jump_cond in (
                        "POP_JUMP_IF_TRUE",
                        "POP_JUMP_IF_TRUE_LOOP",
                        NoneToken,
                    ):
                        kind = "assert"
                    else:
                        assert jump_cond.kind.startswith("POP_JUMP_IF_")
                        kind = "assertnot"

                    LOAD_ASSERT = expr[0]
                    node = SyntaxTree(
                        kind,
                        [assert_expr, jump_cond, LOAD_ASSERT, RAISE_VARARGS_1],
                        transformed_by="n_ifstmt",
                    )
                pass
            pass
        return node

    n_ifstmtc = n_iflaststmtc = n_iflaststmt = n_ifstmt

    # preprocess is used for handling chains of
    # if elif elif
    def n_ifelsestmt(self, node, preprocess=False):
        """
        Transformation involving if..else statments.
        For example


          if ...
          else
             if ..

        into:

          if ..
          elif ...

          [else ...]

        where appropriate.
        """

        else_suite = node[3]
        assert else_suite == "else_suite"

        n = else_suite[0]
        old_stmts = None
        else_suite_index = 1
        if len(n) and n[0] == "suite_stmts":
            n = n[0]

        while len(n) == 1 and n in ("_stmts", "stmt", "stmts"):
            n = n[0]

        if len(n) == 0:
            return node

        if (
            len(n) > 1
            and isinstance(n[0], SyntaxTree)
            and 1 == len(n[0])
            and n[0] == "stmt"
            and n[1].kind == "stmt"
        ):
            else_suite_stmts = n[0]
        elif len(n) == 1:
            else_suite_stmts = n
        else:
            return node

        if else_suite_stmts[0].kind in (
            "ifstmt",
            "iflaststmt",
            "ifelsestmt",
        ):
            old_stmts = n
            n = else_suite_stmts[0]
        else:
            return node

        if n.kind == "last_stmt":
            n = n[0]
        if n.kind in ("ifstmt", "iflaststmt", "iflaststmtc", "ifpoplaststmtc"):
            node.kind = "ifelifstmt"
            n.kind = "elifstmt"
            node.transformed_by = "n_ifelsestmt"
        elif n.kind in ("ifelsestmt",):
            node.kind = "ifelifstmt"
            self.n_ifelsestmt(n, preprocess=True)
            if n == "ifelifstmt":
                n.kind = "elifelifstmt"
            elif n.kind in ("ifelsestmt", "ifelsestmtc"):
                n.kind = "elifelsestmt"
        if not preprocess:
            if old_stmts:
                if n.kind == "elifstmt":
                    trailing_else = SyntaxTree("stmts", old_stmts[1:])
                    if len(trailing_else):
                        # We use elifelsestmtr because it has 3 nodes
                        elifelse_stmt = SyntaxTree(
                            "elifelsestmtr", [n[0], n[else_suite_index], trailing_else]
                        )
                        node[3] = elifelse_stmt
                    else:
                        elif_stmt = SyntaxTree("elifstmt", [n[0], n[else_suite_index]])
                        node[3] = elif_stmt

                    node.transformed_by = "n_ifelsestmt"
                    pass
                else:
                    # Other cases for n.kind may happen here
                    pass
                pass
            return node

    def n_import_from37(self, node: SyntaxTree) -> SyntaxTree:
        importlist37 = node[3]
        if importlist37 != "importlist37":
            return node
        if len(importlist37) == 1 and importlist37 == "importlist37":
            alias37 = importlist37[0]
            store = alias37[1]
            assert store == "store"
            alias_name = store[0].attr
            import_name_attr = node[2]
            assert import_name_attr == "IMPORT_NAME_ATTR"
            dotted_names = import_name_attr.attr.split(".")
            if len(dotted_names) > 1 and dotted_names[-1] == alias_name:
                # Simulate:
                # Instead of
                # import_from37 ::= LOAD_CONST LOAD_CONST IMPORT_NAME_ATTR importlist37 POP_TOP
                # import_as37   ::= LOAD_CONST LOAD_CONST importlist37 store POP_TOP
                # 'import_as37':     ( '%|import %c as %c\n', 2, -2),
                node = SyntaxTree(
                    "import_as37",
                    [node[0], node[1], import_name_attr, store, node[-1]],
                    transformed_by="n_import_from37",
                )
                pass
            pass
        return node

    def n_lambda_start(self, node: SyntaxTree) -> SyntaxTree:
        """Here strip off extraneous nodes in lambda_start"""

        assert node[0] == "BB_START"
        assert node[-1] == "block_end"
        new_node = copy(node)
        del new_node[0]
        del new_node[-1]
        new_node.transofrmed_by = "n_lambda_start"
        del node
        return new_node

    # def n_list_if_or(self, list_if_node):
    #     # If we chain to another list_if, we should drop the "if"
    #     list_iter = list_if_node[2]
    #     if list_iter == "list_iter" and list_iter[0].kind.startswith("list_if"):
    #         list_iter[0].transformed_by = "n_import_from37"
    #         list_iter[0].kind = "lc_if_not"
    #     return list_if_node

    def n_list_for(self, list_for_node):
        expr = list_for_node[0]
        if expr == "expr" and expr[0] == "get_iter":
            # Remove extraneous get_iter() inside the "for" of a comprehension
            assert expr[0][0] == "expr"
            list_for_node[0] = expr[0][0]
            list_for_node.transformed_by = ("n_list_for",)
        return list_for_node

    def n_negated_testtrue(self, node: SyntaxTree) -> SyntaxTree:
        assert node[0] == "testtrue"
        test_node = node[0][0]
        test_node.transformed_by = "n_negated_testtrue"
        return test_node

    def n_stmts(self, node: SyntaxTree) -> SyntaxTree:
        if node.first_child() == "SETUP_ANNOTATIONS":
            prev = node[0]
            new_stmts = [node[0]]
            for i, sstmt in enumerate(node[1:]):
                ann_assign = sstmt
                if ann_assign == "ann_assign" and prev == "assign":
                    annotate_var = ann_assign[-2]
                    if annotate_var.attr == prev[-1][0].attr:
                        node[i].kind = "deleted " + node[i].kind
                        del new_stmts[-1]
                        sstmt = SyntaxTree(
                            "ann_assign_init",
                            [ann_assign[0], prev[0], annotate_var],
                            transformed_by="n_stmts",
                        )
                        pass
                    pass
                new_stmts.append(sstmt)
                prev = ann_assign
                pass
            node.data = new_stmts
        return node

    def traverse(self, node: SyntaxTree) -> SyntaxTree:
        node = self.preorder(node)
        return node

    def transform(
        self, ast: GenericASTTraversal, code, print_fn: Callable
    ) -> GenericASTTraversal:
        self.maybe_show_tree(ast, "before", print_fn)
        self.ast = copy(ast)
        del ast
        self.ast = self.traverse(self.ast)
        n = len(self.ast)

        try:
            # Disambiguate a string (expression) which appears as a "call_stmt" at
            # the beginning of a function versus a docstring. Seems pretty academic,
            # but this is Python.
            call_stmt = ast[0][0]
            if is_not_docstring(call_stmt):
                call_stmt.kind = "string_at_beginning"
                call_stmt.transformed_by = "transform"
                pass
        except:
            pass
        try:
            for i in range(n):
                if is_docstring(self.ast[i], code.co_consts):
                    load_const = self.ast[i].first_child()
                    docstring_ast = SyntaxTree(
                        "docstring",
                        [
                            Token(
                                "LOAD_STR",
                                has_arg=True,
                                offset=0,
                                attr=load_const.attr,
                                pattr=load_const.pattr,
                            )
                        ],
                        transformed_by="transform",
                    )
                    del self.ast[i]
                    self.ast.insert(0, docstring_ast)
                    break

            if self.ast[-1] == RETURN_NONE:
                self.ast.pop()  # remove last node
                # todo: if empty, add 'pass'
        except Exception:
            pass

        self.maybe_show_tree(self.ast, "after", print_fn)
        return self.ast

    # Write template_engine
    # def template_engine
    def strip_pseudo_ops(self, node: SyntaxTree) -> SyntaxTree:
        new_node = SyntaxTree(node.kind)
        for i, kid in enumerate(node):
            if hasattr(kid, "optype") and kid.optype == "pseudo":
                continue
            new_kid = self.preorder(kid)
            new_node.data.append(new_kid)

        del node
        return new_node
