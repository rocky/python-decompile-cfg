#  Copyright (c) 2020-2022 Rocky Bernstein
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
Spark parser grammar for Python 3.8's Lambda's.

Lambda's encompass expressions but don't have statements.  This contains
grammar rules but not rules for the start symbol or a start symbol name. That is
elsewhere.


By leaving out the start symbol rules and name, this module and its classes can
be used as a superclass in other grammars, such as a full grammar for Python 3.10.
"""

from decompile_cfg.parsers.p38.lambda_custom import Python38LambdaCustom
from decompile_cfg.parsers.parse_heads import PythonParserLambda, PythonBaseParser
from spark_parser import DEFAULT_DEBUG as PARSER_DEFAULT_DEBUG


class Python38LambdaParser(Python38LambdaCustom, PythonParserLambda):
    def p_branch_ops(self, args):
        """
        # Note: reduction-rule checks are needed for many of the below;
        # the rules in of themselves are not sufficient.

        and        ::= expr_jifop
                       dom_start_opt
                       expr

        and_part   ::= expr_pjif
        and_parts  ::= and_part+

        and1       ::= and_parts expr

        or         ::= expr_jitop
                       dom_start_opt
                       expr

        or_part    ::= expr_pjit
        or_parts   ::= or_part+

        or1        ::= or_parts expr

        and_or     ::= and_parts
                       expr
                       jitop
                       expr

        or_and     ::= or_parts
                       expr
                       jifop
                       expr

        if_exp     ::= expr
                       POP_JUMP_IF_FALSE
                       expr
                       JUMP_FORWARD
                       bb_end_start
                       expr

        if_exp     ::= branch_op
                       POP_JUMP_IF_FALSE
                       expr
                       JUMP_FORWARD
                       bb_end_start
                       expr

        if_exp_not ::= expr
                       POP_JUMP_IF_TRUE
                       expr
                       JUMP_FORWARD
                       bb_end_start
                       expr

        # if_exp_true are are IfExp which always evaluate true, e.g.:
        #      x = a if 1 else b
        # There is dead or non-optional remnants of the condition code though,
        # and we use that to match on to reconstruct the source more accurately
        if_exp_true ::= expr
                        JUMP_FORWARD
                        expr

        """

    def p_chained(self, args):
        """
        # A compare_chained is two comparisions like x <= y <= z

        compare_chained     ::= expr
                                compare_chained1
                                bb_end_start
                                ROT_TWO POP_TOP
                                bb_doms_end_start_opt

        # FIXME: simplify the compare_chain1 recursion?
        compare_chained1    ::= expr DUP_TOP ROT_THREE COMPARE_OP jifop_opt
                                compare_chained1
        compare_chained1    ::= expr DUP_TOP ROT_THREE COMPARE_OP jifop_opt
                                compare_chained2 bb_doms_end_start_opt

        compare_chained2    ::= expr COMPARE_OP JUMP_FORWARD
        compare_chained2    ::= expr COMPARE_OP RETURN_VALUE
        """

    # Conditional jumps with dominator information included
    def p_conditional_jump(self, args):
        """
        jifop       ::= JUMP_IF_FALSE_OR_POP bb_end_start
        jifop_opt   ::= JUMP_IF_FALSE_OR_POP bb_end_start_opt
        jitop       ::= JUMP_IF_TRUE_OR_POP BB_END dom_start
        jifop_expr  ::= JUMP_IF_FALSE_OR_POP bb_doms_end dom_start expr
        jitop_expr  ::= JUMP_IF_TRUE_OR_POP bb_doms_end dom_start expr
        """

    # Dominator and basic block pseudo operations needed
    # to assist control flow
    def p_dom(self, args):
        """
        dom_start        ::= DOM_START BB_START
        dom_start_opt    ::= dom_start?
        dom_end          ::= BB_END DOM_END
        bb_end_start     ::= BB_END dom_start
        bb_end_start_opt ::= bb_end_start?
        dom_end_opt      ::= dom_end?
        bb_doms_end      ::= BB_END doms_end
        bb_doms_end_opt  ::= bb_doms_end?
        doms_end         ::= DOM_END+
        dom_end_opt      ::= dom_end?
        dom_end_start    ::= dom_end dom_start
        dom_end_start_opt ::= dom_end_start?


        bb_end_start          ::= BB_END dom_start
        bb_doms_end_start     ::= bb_doms_end dom_start
        bb_doms_end_start_opt ::= bb_doms_end_start?

        """

    def p_conditionals(self, args):
        """
        branch_op                  ::= and POP_JUMP_IF_TRUE expr

        expr_pjif                  ::= expr POP_JUMP_IF_FALSE
        expr_pjit                  ::= expr POP_JUMP_IF_TRUE
        expr_jifop                 ::= expr JUMP_IF_FALSE_OR_POP
        expr_jitop                 ::= expr JUMP_IF_TRUE_OR_POP
        expr_pjiff                 ::= expr pjump_iff
        """

    def p_comprehension(self, args):
        """
        # Python3 scanner adds LOAD_LISTCOMP. Python3 does list comprehension like
        # other comprehensions (set, dictionary).

        gen_comp_body   ::= expr
                            bb_doms_end_start_opt
                            YIELD_VALUE bb_doms_end_start
                            POP_TOP

        generator_exp   ::= LOAD_FAST
                            bb_end_start
                            FOR_ITER
                            bb_end_start
                            store
                             comp_iter
                            JUMP_BACK
                            bb_doms_end_start

        for_iter        ::= bb_end_start
                            FOR_ITER
                            bb_end_start

        # FIXME: go over:

        # comp_iter      ::= comp_for
        # comp_for       ::= expr gen_comp_body JUMP_BACK bb_doms_end_start

        # Our "continue" heuristic -  in two successive JUMP_BACKS, the first
        # one may be a continue - sometimes classifies a JUMP_BACK
        # as a CONTINUE. The two are kind of the same in a comprehension.

        # comp_for       ::= expr get_for_iter store comp_iter CONTINUE _come_froms
        # comp_for       ::= expr get_for_iter store comp_iter JUMP_BACK _come_froms

        # get_for_iter   ::= GET_ITER _come_froms FOR_ITER

        comp_body      ::= dict_comp_body
        comp_body      ::= set_comp_body
        comp_body      ::= gen_comp_body

        dict_comp_body ::= expr expr MAP_ADD
        set_comp_body  ::= expr SET_ADD

        set_comp_func ::= BUILD_SET_0
                          LOAD_FAST
                          bb_end_start_opt
                          for_iter store comp_iter
                          JUMP_BACK
                          dom_end_start_opt
        """

    def p_comprehension_dict(self, args):
        """ "
        comp_if       ::= expr_pjif comp_iter
        comp_if       ::= expr_pjiff comp_iter
        comp_if       ::= or_jump_if_false_cf comp_iter
        comp_if_not   ::= expr pjump_ift comp_iter

        comp_iter     ::= comp_body
        comp_iter     ::= comp_if
        comp_iter     ::= comp_if_not

        dict_comp_func ::= BUILD_MAP_0
                          LOAD_FAST
                          for_iter
                          store
                          comp_iter
                          JUMP_BACK
                          bb_doms_end_start
                          RETURN_VALUE
                          bb_doms_end
        """

    def p_comprehension_list(self, args):
        """
        list_iter ::= list_for
        list_iter ::= list_if
        list_iter ::= list_if_not
        list_iter ::= list_if_or_not
        list_iter ::= lc_body

        lc_body   ::= expr dom_end_start_opt LIST_APPEND

        jump_back ::= JUMP_BACK bb_doms_end_start

        list_for  ::= expr
                      for_iter
                      store list_iter
                      jump_back
                      bb_doms_end_start_opt

        list_comp ::= BUILD_LIST_0 list_iter

        list_if     ::= expr list_if_end list_iter
        list_if     ::= expr jump_if_false_cf   list_iter
        list_if     ::= expr pjump_iff list_iter

        list_if_end ::= pjump_iff BB_END dom_start

        # Need to fix or remove
        list_if_or_not ::= expr_pjit expr_pjit COME_FROM list_iter
        list_if_not_end ::= pjump_ift _come_froms
        list_if_not ::= expr list_if_not_end list_iter come_from_opt

        """

    def p_comprehension_set(self, args):
        """
        comp_iter     ::= comp_body
        comp_iter     ::= comp_for
        comp_body     ::= gen_comp_body


        gen_comp_body ::= expr
                          YIELD_VALUE
                          BB_END DOM_END BB_START POP_TOP
        gen_comp_body ::= branch_op
                          bb_end_start
                          YIELD_VALUE
                          bb_doms_end_start POP_TOP

        """

    def p_expr(self, args):
        """
        # expressions going to terminal symbols
        expr ::= LOAD_DEREF
        expr ::= LOAD_FAST
        expr ::= LOAD_GLOBAL
        expr ::= LOAD_NAME

        expr ::= attribute
        expr ::= bin_op
        expr ::= branch_op
        expr ::= branch_op_compound
        expr ::= call
        expr ::= compare
        expr ::= compare_in
        expr ::= compare_is

        # experimental. Matches AST better though
        expr ::= constant

        expr ::= list
        expr ::= list_comp

        expr ::= named_expr
        expr ::= not
        expr ::= subscript
        expr ::= subscript2
        expr ::= unary_not
        expr ::= unary_op
        expr ::= yield
        expr ::= yield_from

        # In calls, we use "arg" rather than "expr" so we can
        # bound expressions with conditional branches.
        # Arg also matches Python's AST in a Call beter.
        arg              ::= expr
        arg              ::= branch_op bb_doms_end_start
        arg              ::= branch_op bb_end_start

        attribute        ::= expr LOAD_METHOD

        # bin_op (formerly "binary_expr") is the Python AST BinOp
        bin_op            ::= left right binary_operator
        left              ::= arg
        right             ::= arg

        binary_operator   ::= BINARY_ADD
        binary_operator   ::= BINARY_AND
        binary_operator   ::= BINARY_FLOOR_DIVIDE
        binary_operator   ::= BINARY_LSHIFT
        binary_operator   ::= BINARY_MATRIX_MULTIPLY
        binary_operator   ::= BINARY_MODULO
        binary_operator   ::= BINARY_MULTIPLY
        binary_operator   ::= BINARY_OR
        binary_operator   ::= BINARY_POWER
        binary_operator   ::= BINARY_RSHIFT
        binary_operator   ::= BINARY_SUBTRACT
        binary_operator   ::= BINARY_TRUE_DIVIDE
        binary_operator   ::= BINARY_XOR

        # Note: we use "branch_op" in an implementation-specific way.
        #
        # What distinguishes these kinds of Boolean expressions from other kinds of expressions,
        # even from those that return True and False (like "is" and "in") is that
        # they have basic block and dominator pseudo instructions.

        branch_op ::= or bb_doms_end_opt
        branch_op ::= or1 bb_doms_end_opt
        branch_op ::= and bb_doms_end_opt
        branch_op ::= and1 bb_doms_end_opt
        branch_op ::= and_or bb_doms_end_opt
        branch_op ::= or_and bb_doms_end_opt

        branch_op ::= if_exp bb_doms_end_opt
        branch_op ::= if_exp_not bb_doms_end_opt
        branch_op ::= if_exp_true bb_doms_end_opt


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

        constant ::= LOAD_CONST
        constant ::= LOAD_STR
        constant ::= LOAD_CODE


        # named_expr is also known as the "walrus op" :=
        named_expr        ::= expr DUP_TOP store

        subscript         ::= expr expr BINARY_SUBSCR
        subscript2        ::= expr expr DUP_TOP_TWO BINARY_SUBSCR

        # unary_op (formerly "unary_expr") is the Python AST UnaryOp
        unary_op          ::= arg unary_operator

        unary_operator    ::= UNARY_POSITIVE
        unary_operator    ::= UNARY_NEGATIVE
        unary_operator    ::= UNARY_INVERT
        unary_operator    ::= UNARY_NOT

        unary_not         ::= expr UNARY_NOT

        yield             ::= expr YIELD_VALUE
        yield_from        ::= expr
                              GET_YIELD_FROM_ITER LOAD_CONST YIELD_FROM
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
        # return_expr_lambda is a return value used inside a lambda

        return_expr_lambda      ::= dom_start_opt
                                    expr
                                    dom_start_opt
                                    RETURN_VALUE
                                    bb_doms_end_opt

        return_expr_lambda      ::= dom_start_opt
                                    expr
                                    bb_end_start
                                    RETURN_VALUE
                                    bb_doms_end

        # FIXME: generalize this
        return_expr_lambda      ::= dom_start_opt
                                    generator_exp
                                    LOAD_CONST
                                    RETURN_VALUE
                                    bb_doms_end

        return_expr_lambda      ::= dom_start_opt
                                    set_comp_func
                                    RETURN_VALUE
                                    bb_doms_end

        return_expr_lambda      ::= dom_start_opt
                                    dict_comp_func
                                    RETURN_VALUE
                                    bb_doms_end

        return_expr_lambda      ::= dom_start_opt
                                    dict_comp_func

        return_expr_lambda      ::= if_exp_lambda
        return_expr_lambda      ::= if_exp_binop_lambda
        return_expr_lambda      ::= if_exp_not_lambda
        return_expr_lambda      ::= if_exp_dead_code

        # return_expr_lambda with a binary operator before the return
        return_expr_binop_lambda  ::= dom_start_opt
                                      expr
                                      binary_operator
                                      RETURN_VALUE
                                      bb_doms_end

        # Temporary until we have a rule generating this
        return_expr_lambda      ::= if_exp_call_lambda

        return_call_lambda      ::= dom_start_opt
                                    args
                                    CALL_FUNCTION_1
                                    RETURN_VALUE
                                    bb_doms_end

        if_exp_call_lambda      ::= expr expr
                                    POP_JUMP_IF_FALSE
                                    bb_end_start
                                    args CALL_FUNCTION_1
                                    RETURN_VALUE
                                    dom_end dom_start
                                    return_call_lambda

        # if_exp_lambda is an if_exp with a return value used
        # inside a lambda

        # Note these two if_exp_lambda are distinct and cannot be generalized combined
        # into once. Otherwise we would need to disabmiguate
        #    lambda n: True if n >= 95 and n & 1 else False
        # from:
        #    lambda n: (n & 1) and True if n >= 95 else False
        if_exp_lambda      ::= branch_op
                               POP_JUMP_IF_FALSE
                               bb_end_start_opt
                               expr
                               RETURN_VALUE
                               BB_END
                               return_expr_lambda

        if_exp_lambda      ::= expr
                               POP_JUMP_IF_FALSE
                               bb_end_start_opt
                               expr
                               RETURN_VALUE
                               bb_end_start
                               return_expr_lambda


        if_exp_lambda      ::= expr
                               POP_JUMP_IF_FALSE
                               bb_end_start_opt
                               expr
                               RETURN_VALUE
                               dom_end dom_start
                               return_expr_lambda



        # A binary operator with if_exp as the left operand.
        # Here that value is duplicated before both return
        # branches
        if_exp_binop_lambda ::= expr expr
                               POP_JUMP_IF_FALSE
                               bb_end_start
                               expr
                               binary_operator
                               RETURN_VALUE
                               dom_end dom_start
                               return_expr_binop_lambda

        if_exp_not_lambda ::= expr
                              POP_JUMP_IF_TRUE
                              expr
                              RETURN_VALUE
                              bb_end_start
                              return_expr_lambda
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

    def __init__(
        self,
        start_symbol: str = "lambda_start",
        debug_parser: dict = PARSER_DEFAULT_DEBUG,
    ):
        PythonParserLambda.__init__(
            self, debug_parser=debug_parser, start_symbol=start_symbol
        )
        PythonBaseParser.__init__(
            self, start_symbol=start_symbol, debug_parser=debug_parser
        )
        Python38LambdaCustom.__init__(self)

    def customize_grammar_rules(self, tokens, customize):
        self.customize_grammar_rules_lambda38(tokens, customize)


if __name__ == "__main__":
    # Check grammar
    from decompile_cfg.parsers.dump import dump_and_check

    # The start_symbol here is something from this file to check.
    # Note that the start_symbol from parse_heads is "lambda_start"
    # which is the same thing surrounded by dominator information.
    # But that doesn't appear here.
    p = Python38LambdaParser(start_symbol="lambda_start")
    modified_tokens = set(
        """JUMP_BACK CONTINUE BB_END BB_START DOM_END DOM_START""".split()
    )

    dump_and_check(p, (3, 8), modified_tokens, set(["lambda_start"]))
