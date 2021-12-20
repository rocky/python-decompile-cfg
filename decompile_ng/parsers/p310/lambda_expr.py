#  Copyright (c) 2020-2021 Rocky Bernstein
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
Spark parser grammar for Python 3.10's Lambda's.

Lambda's encompass expressions but don't have statements.  This contains
grammar rules but not rules for the start symbol or a start symbol name. That is
elsewhere.


By leaving out the start symbol rules and name, this module and its classes can
be used as a superclass in other grammars, such as a full grammar for Python 3.10.
"""

from decompile_ng.parsers.p310.base import Python310BaseParser
from decompile_ng.parsers.parse_heads import PythonParserLambda, PythonBaseParser
from spark_parser import DEFAULT_DEBUG as PARSER_DEFAULT_DEBUG

class Python310LambdaParser(Python310BaseParser, PythonParserLambda):
    def p_branch_ops(self, args):
        """
        # Note: reduction-rule checks are needed for many of the below;
        # the rules in of themselves are not sufficient.

        or  ::= expr_jitop
                dom_start
                expr

        and ::= expr_jifop
                dom_start
                expr

        and_part   ::= expr_pjif dom_start
        and_parts  ::= and_part+

        and_or ::= and_parts expr jitop_expr

        or_part    ::= expr_pjit dom_start
        or_parts   ::= or_part+

        or_and     ::= or_parts expr jifop_expr
        """

    def p_chained(self, args):
        """
        # A compare_chained is two comparisions like x <= y <= z

        compare_chained     ::= expr compare_chained1 ROT_TWO POP_TOP bb_doms_end_start_opt

        # FIXME: simplify the compare_chain1 recursion?
        compare_chained1    ::= expr DUP_TOP ROT_THREE COMPARE_OP jifop
                                compare_chained1 bb_doms_end_start_opt
        compare_chained1    ::= expr DUP_TOP ROT_THREE COMPARE_OP jifop
                                compare_chained2 bb_doms_end_start_opt

        compare_chained2    ::= expr COMPARE_OP JUMP_FORWARD
        compare_chained2    ::= expr COMPARE_OP RETURN_VALUE
        """

    # Conditional jumps with dominator information included
    def p_conditional_jump(self, args):
        """
        jifop       ::= JUMP_IF_FALSE_OR_POP BB_END dom_start
        # jitop       ::= JUMP_IF_TRUE_OR_POP BB_END dom_start
        jifop_expr  ::= JUMP_IF_FALSE_OR_POP bb_doms_end dom_start expr
        jitop_expr  ::= JUMP_IF_TRUE_OR_POP bb_doms_end dom_start expr
        """

    # Dominator and basic block pseudo operations needed
    # to assist control flow
    def p_dom(self, args):
        """
        dom_start       ::= DOM_START BB_START
        dom_start_opt   ::= dom_start?
        dom_end         ::= BB_END DOM_END
        dom_end_opt     ::= dom_end?
        bb_doms_end     ::= BB_END doms_end
        bb_doms_end_opt ::= bb_doms_end?
        doms_end        ::= DOM_END+
        dom_end_opt     ::= dom_end?

        bb_end_start          ::= BB_END dom_start
        bb_doms_end_start     ::= bb_doms_end dom_start
        bb_doms_end_start_opt ::= bb_doms_end_start?

        """

    def p_conditionals(self, args):
        """
        expr                       ::= if_exp37
        branch_op                    ::= and POP_JUMP_IF_TRUE expr

        expr_pjif                  ::= expr POP_JUMP_IF_FALSE BB_END
        expr_pjit                  ::= expr POP_JUMP_IF_TRUE BB_END
        expr_jifop                 ::= expr JUMP_IF_FALSE_OR_POP BB_END
        expr_jitop                 ::= expr JUMP_IF_TRUE_OR_POP BB_END
        expr_pjiff                 ::= expr pjump_iff
        expr_pjift                 ::= expr pjump_ift

        list_iter                  ::= list_if37
        list_iter                  ::= list_if37_not
        list_if37                  ::= c_compare_chained37_false list_iter
        list_if37_not              ::= compare_chained37 list_iter

        # A reduction check distinguishes between "and" and "and_not"
        # based on whether the POP_IF_JUMP location matches the location of the
        # POP_JUMP_IF_FALSE.

        # Do we need these?
        # and_not                    ::= expr_pjif expr_pjit
        # or_and_not                 ::= expr_pjit and_not COME_FROM
        # not_and_not                ::= not expr_pjif COME_FROM
        #
        # expr                       ::= if_exp_37a
        # if_exp_37a                 ::= and_not expr JUMP_FORWARD come_froms expr COME_FROM
        """

    def p_comprehension(self, args):
        """
        # Python3 scanner adds LOAD_LISTCOMP. Python3 does list comprehension like
        # other comprehensions (set, dictionary).

        # comp_iter      ::= comp_for
        for_iter       ::= bb_end_start FOR_ITER

        # Our "continue" heuristic -  in two successive JUMP_BACKS, the first
        # one may be a continue - sometimes classifies a JUMP_BACK
        # as a CONTINUE. The two are kind of the same in a comprehension.

        # FIXME: go over:
        # comp_for       ::= expr get_for_iter store comp_iter CONTINUE _come_froms
        # comp_for       ::= expr get_for_iter store comp_iter JUMP_BACK _come_froms

        get_for_iter   ::= GET_ITER _come_froms FOR_ITER

        comp_body      ::= dict_comp_body
        comp_body      ::= set_comp_body
        comp_body      ::= gen_comp_body

        dict_comp_body ::= expr expr MAP_ADD
        gen_comp_body  ::= expr YIELD_VALUE POP_TOP
        set_comp_body  ::= expr SET_ADD
        """

    def p_comprehension_dict(self, args):
        """"
        c_or       ::= or
        c_or       ::= c_or_parts expr
        c_or_parts ::= expr_pjift+

        comp_if       ::= expr_pjif comp_iter
        comp_if       ::= expr_pjiff comp_iter
        comp_if       ::= or_jump_if_false_cf comp_iter
        comp_if       ::= c_or_jump_if_false_cf comp_iter
        comp_if_not   ::= expr pjump_ift comp_iter

        comp_iter     ::= comp_body
        comp_iter     ::= comp_if
        comp_iter     ::= comp_if_not

        # or_jump_if_false_cf    ::= or POP_JUMP_IF_FALSE COME_FROM
        # c_or_jump_if_false_cf  ::= c_or POP_JUMP_IF_FALSE_BACK COME_FROM
        """

    def p_comprehension_list(self, args):
        """
        expr ::= list_comp

        list_iter ::= list_for
        list_iter ::= list_if
        list_iter ::= list_if_not
        list_iter ::= list_if_or_not
        list_iter ::= lc_body

        lc_body   ::= expr LIST_APPEND

        jump_back ::= JUMP_BACK bb_doms_end_start

        list_for  ::= expr
                      for_iter
                      bb_end_start
                      store list_iter
                      jump_back
                      bb_doms_end_start_opt

        list_comp ::= BUILD_LIST_0 list_iter

        list_if     ::= expr list_if_end list_iter
        list_if     ::= expr jump_if_false_cf   list_iter

        list_if_end ::= pjump_iff BB_END dom_start

        # Need to fix or remove
        list_if     ::= expr pjump_iff list_iter come_from_opt
        list_if_or_not ::= expr_pjit expr_pjit COME_FROM list_iter
        list_if_not_end ::= pjump_ift _come_froms
        list_if_not ::= expr list_if_not_end list_iter come_from_opt

        """

    def p_expr(self, args):
        """
        # expressions going to terminal symbols
        expr ::= LOAD_CODE
        expr ::= LOAD_CONST
        expr ::= LOAD_DEREF
        expr ::= LOAD_FAST
        expr ::= LOAD_GLOBAL
        expr ::= LOAD_NAME
        expr ::= LOAD_STR

        expr ::= and
        expr ::= attribute
        expr ::= bin_op
        expr ::= branch_op
        expr ::= branch_op_compound
        expr ::= call
        expr ::= compare
        expr ::= compare_in
        expr ::= compare_is
        # expr ::= if_exp
        # expr ::= if_exp_not
        expr ::= if_exp_true
        expr ::= named_expr
        expr ::= not
        expr ::= subscript
        expr ::= subscript2
        expr ::= unary_not
        expr ::= unary_op
        expr ::= yield
        expr ::= yield_from

        attribute        ::= expr LOAD_METHOD

        # bin_op (formerly "binary_expr") is the Python AST BinOp
        bin_op            ::= expr expr binary_operator

        binary_operator   ::= BINARY_ADD
        binary_operator   ::= BINARY_MULTIPLY
        binary_operator   ::= BINARY_AND
        binary_operator   ::= BINARY_OR
        binary_operator   ::= BINARY_XOR
        binary_operator   ::= BINARY_SUBTRACT
        binary_operator   ::= BINARY_TRUE_DIVIDE
        binary_operator   ::= BINARY_FLOOR_DIVIDE
        binary_operator   ::= BINARY_MODULO
        binary_operator   ::= BINARY_LSHIFT
        binary_operator   ::= BINARY_RSHIFT
        binary_operator   ::= BINARY_POWER

        # Note: we use "branch_op" in an implementation-specific way.
        #
        # What distinguishes these kinds of Boolean expressions from other kinds of expressions,
        # even from those that return True and False (like "is" and "in") is that
        # they have basic block and dominator pseudo instructions.

        branch_op ::= or bb_doms_end_opt
        branch_op ::= and bb_doms_end_opt
        branch_op ::= and_or bb_doms_end
        branch_op ::= or_and bb_doms_end

        # A "branch_op_compound" is a branch_op with a non-branching unary or binary operator at the end.
        # For example, in: "not a and b", the "not" is at the end after "a and b" and is non-branching.
        # But it appears at the beginning in source code.
        # In contrast, in  "(a and b) + 1": the plus is at the end and it is non-branching. And
        # it appears at the the end in source code

        branch_op_compound ::= branch_op_compound_prefix
        branch_op_compound ::= branch_op_compound_suffix

        branch_op_compound_prefix ::= branch_op DOM_START BB_START unary_operator
        branch_op_compound_suffix ::= branch_op DOM_START BB_START expr binary_operator

        # FIXME: the below is to work around test_grammar expecting a "call" to be
        # on the LHS because it is also somewhere on in a rule.
        call              ::= expr CALL_METHOD_0

        compare           ::= compare_chained
        compare           ::= compare_single
        compare_in        ::= expr expr CONTAINS_OP
        compare_is        ::= expr expr IS_OP
        compare_single    ::= expr expr COMPARE_OP

        # if_exp_true are are IfExp which always evaluate true, e.g.:
        #      x = a if 1 else b
        # There is dead or non-optional remnants of the condition code though,
        # and we use that to match on to reconstruct the source more accurately
        if_exp_true    ::= expr JUMP_FORWARD expr COME_FROM

        # named_expr is also known as the "walrus op" :=
        named_expr        ::= expr DUP_TOP store

        subscript         ::= expr expr BINARY_SUBSCR
        subscript2        ::= expr expr DUP_TOP_TWO BINARY_SUBSCR

        # unary_op (formerly "unary_expr") is the Python AST UnaryOp
        unary_op          ::= expr unary_operator

        unary_operator    ::= UNARY_POSITIVE
        unary_operator    ::= UNARY_NEGATIVE
        unary_operator    ::= UNARY_INVERT
        unary_operator    ::= UNARY_NOT

        unary_not         ::= expr UNARY_NOT

        yield             ::= expr YIELD_VALUE
        yield_from        ::= expr GET_YIELD_FROM_ITER LOAD_CONST YIELD_FROM
        """

    def p_jump(self, args):
        """
        pjump_ift          ::= POP_JUMP_IF_TRUE
        pjump_ift          ::= POP_JUMP_IF_TRUE_BACK

        pjump_iff          ::= POP_JUMP_IF_FALSE
        pjump_iff          ::= POP_JUMP_IF_FALSE_BACK

        # pjump              ::= pjump_iff
        # pjump              ::= pjump_ift
        """

    def p_lambda(self, args):
        """
        return_lambda      ::= dom_start_opt
                               expr
                               dom_start_opt
                               RETURN_VALUE
                               bb_doms_end

        return_lambda      ::= if_exp_lambda
        return_lambda      ::= if_exp_lambda2
        return_lambda      ::= if_exp_not_lambda
        return_lambda      ::= if_exp_not_lambda2
        return_lambda      ::= if_exp_dead_code

        if_exp_lambda2     ::= and_parts return_lambda
                               return_lambda

        if_exp_not_lambda2 ::= expr_pjit dom_start expr
                               RETURN_VALUE bb_doms_end return_lambda
        """

    def p_store(self, args):
        """
        # Note. The below is right-recursive:
        designList ::= store store
        designList ::= store DUP_TOP designList

        ## Can we replace with left-recursive, and redo with:
        ##
        ##   designList  ::= designLists store store
        ##   designLists ::= designLists store DUP_TOP
        ##   designLists ::=
        ## Will need to redo semantic action

        store           ::= STORE_DEREF
        store           ::= STORE_FAST
        store           ::= STORE_GLOBAL
        store           ::= STORE_NAME

        store           ::= expr STORE_ATTR
        store           ::= store_subscript
        store_subscript ::= expr expr STORE_SUBSCR
        """

    def __init__(self, start_symbol: str, debug_parser: dict = PARSER_DEFAULT_DEBUG):
        PythonParserLambda.__init__(
            self, debug_parser=debug_parser, start_symbol=start_symbol
        )
        PythonBaseParser.__init__(
            self, start_symbol=start_symbol, debug_parser=debug_parser
        )
        self.new_rules = set()
        self.customized = {}

if __name__ == "__main__":
    # Check grammar
    from decompile_ng.parsers.dump import dump_and_check
    # The start_symbol here is something from this file to check.
    # Note that the start_symbol from parse_heads is "lambda_start"
    # which is the same thing surrounded by dominator information.
    # But that doesn't appear here.
    p = Python310LambdaParser(start_symbol="lambda_start")
    modified_tokens = set(
        """JUMP_BACK CONTINUE BB_END BB_START DOM_END DOM_START""".split()
        )

    dump_and_check(p, (3, 10), modified_tokens, set(["lambda_start"]))
