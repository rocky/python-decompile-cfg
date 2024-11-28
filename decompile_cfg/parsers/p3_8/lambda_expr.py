#  Copyright (c) 2020-2024 Rocky Bernstein
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

from spark_parser import DEFAULT_DEBUG as PARSER_DEFAULT_DEBUG

from decompile_cfg.parsers.p3_8.lambda_custom import Python3_8LambdaCustom
from decompile_cfg.parsers.parse_heads import PythonBaseParser, PythonParserLambda


class Python3_8LambdaParser(Python3_8LambdaCustom, PythonParserLambda):
    """
    Python 3.8 lambda grammar rules
    """
    def p_branch_ops(self, _):
        """

        # "and" is the final reduction that hooks into the higher level
        # levels of the grammar.

        and               ::= and_parts
        and               ::= and_part

        expr_jifop_and    ::= expr_jifop BB_START and BLOCK_END_JOIN
        expr_jifop_and    ::= expr_jifop BB_START expr_jifop_and BLOCK_END_JOIN

        # This appears in chained "and"s
        and_part          ::= expr_jifop BB_START expr BB_END BLOCK_END_FALLTHROUGH_JOIN
        and_part          ::= expr_jifop BB_START expr
        and_part          ::= expr_jifop BB_START or_part BLOCK_END_JUMP_JOIN
        and_part          ::= or_part_oa BB_START expr BB_END
                              BLOCK_END_FALLTHROUGH_JOIN BLOCK_END_JUMP_JOIN

        and_parts         ::= expr_jifop BB_START and_part BLOCK_END_JUMP_JOIN
        and_parts         ::= expr_jifop BB_START and_parts BLOCK_END_JUMP_JOIN

        and_parts         ::= or_part_ao BB_START expr BB_END

        # This appears in "and .. or"
        and_part_ao       ::= expr_pjif BB_START expr
                              jitop
                              BLOCK_END_FALLTHROUGH_JOIN

        and_parts_ao      ::= expr_pjif BB_START and_part_ao
        and_parts_ao      ::= expr_pjif BB_START and_parts_ao BLOCK_END_JUMP_JOIN


        and_or            ::= and_part_ao
                              BB_START
                              expr
                              BB_END
                              BLOCK_END_FALLTHROUGH_JOIN
                              BLOCK_END_JUMP_JOIN

        and_or            ::= and_parts_ao
                              BLOCK_END_JUMP_JOIN
                              BB_START
                              expr
                              BB_END
                              BLOCK_END_FALLTHROUGH_JOIN
                              BLOCK_END_JUMP_JOIN


        and_or_parts    ::= and_or_part
        and_or_parts    ::= expr_pjif BB_START and_or_parts BLOCK_END_JOIN

        or                ::= or_parts
        or                ::= or_part

        or_part           ::= expr_jitop BB_START expr BB_END
                              BLOCK_END_FALLTHROUGH_JOIN

        or_parts          ::= expr_jitop BB_START or_part BLOCK_END_JUMP_JOIN
        or_parts          ::= expr_jitop BB_START or_parts BLOCK_END_JUMP_JOIN

        # and_or is (a and ...) or y

        # An and_or followed by an expr
        and_or_expr         ::= and_parts
                                BB_START
                                expr_jitop
                                BB_START expr BB_END



        ## In cases where we have some sort of logic optimization the
        ## "or" using "expr_jitop" can get converted to "or" using "expr_pjit"
        ## In such cases we have an exra JUMP_IF_FALSE_OR_POP at the end.
        #
        # or_pjit       ::= expr_pjit
        #                   dom_start_opt
        #                   expr
        # and_or_jifop  ::= and_pjit
        #                   expr_pjif
        #                   expr_pjit

        # "or" portion when combined with an "and" either as the left or right
        # operand

        or_part_ao     ::= expr_pjit BB_START expr_jifop BLOCK_END_JOIN
        or_part_oa     ::= expr_pjit BB_START expr_jifop BLOCK_END_FALLTHROUGH_JOIN

        or_and         ::= or_part_oa BB_START expr
                           BLOCK_END_FALLTHROUGH_JOIN BLOCK_JUMP_JOIN

        or_and         ::= expr_jitop BB_START and_part BLOCK_END_JUMP_JOIN

        if_exp_dead_code   ::= return_expr_lambda
                               bb_end_start
                               return_expr_lambda

        # Corresponds to AST IfExp; note this
        # must include an "else" part.
        # Don't confuse with comprehension if's
        if_exp        ::= if_exp_jump_false
        if_exp        ::= if_exp_jump_true

        if_exp_return            ::= if_exp_jump_false_return
        if_exp_jump_false_return ::= expr_pjif
                                     BB_START
                                     return_expr
                                     NOT_FALLEN_INTO_BLOCK
                                     BB_START
                                     return_expr

        and_part_expr            ::= expr_pjif
                                     BB_START
                                     expr
                                     pjif

        if_exp_jump_false_return ::= and_part_expr
                                     BB_START
                                     return_expr
                                     NOT_FALLEN_INTO_BLOCK
                                     BLOCK_END_JUMP_JOIN
                                     BB_START
                                     return_expr

        if_exp_jump_true  ::= expr
                              POP_JUMP_IF_TRUE
                              bb_end_start_opt
                              expr
                              jf_bb_end_start
                              expr

        if_exp_jump_false ::= expr
                              POP_JUMP_IF_FALSE
                              bb_end_start
                              expr
                              jf_doms_end_start
                              expr

        if_exp_compare ::= compare
                           SIBLING_BLOCK
                           expr
                           jf_doms_end_start
                           SIBLING_BLOCK
                           expr

        if_exp_and     ::= expr
                           POP_JUMP_IF_FALSE
                           branch_op_part
                           expr
                           block_end
                           JUMP_FORWARD
                           block_end
                           expr

        if_exp_and     ::= expr
                           POP_JUMP_IF_FALSE
                           branch_op_part
                           expr
                           block_end
                           return_value
                           block_end
                           expr

        if_exp_loop    ::= expr
                           POP_JUMP_IF_FALSE
                           expr
                           JUMP_FOR POP_JUMP_IF_FALSE_LOOP
                           jf_bb_end_start
                           expr

        if_exp_or      ::= expr
                           POP_JUMP_IF_TRUE
                           branch_op_part
                           expr
                           block_end
                           return_value
                           block_end
                           expr

        if_exp_or      ::= expr
                           POP_JUMP_IF_TRUE
                           branch_op_part
                           expr
                           block_end
                           JUMP_FORWARD
                           block_end
                           SIBLING_BLOCK
                           expr


        # FIXME:
        # Should go in full.py
        if_exp_or ::= expr POP_JUMP_IF_TRUE branch_op_part expr

        # FIXME: How is this not the same as if_exp above?
        # Distinguish in semantic action?
        if_exp_not ::= expr
                       POP_JUMP_IF_TRUE
                       expr
                       jf_bb_end_start
                       expr

        # if_exp_true are are IfExp which always evaluate true, e.g.:
        #      x = a if 1 else b
        # There is dead or non-optional remnants of the condition code though,
        # and we use that to match on to reconstruct the source more accurately
        if_exp_true ::= expr
                        JUMP_FORWARD
                        block_end
                        SIBLING_BLOCK
                        expr

        """

    def p_chained(self, _):
        """
        chained_parts        ::= chained_part+

        # A "compare_chained" is two comparisions like x <= y <= z
        # In the Python docs it says "Comparisons can be chained ..."
        # In the Python AST, this appears as: Compare(.. ops=)

        compare_chained        ::= expr
                                   compare_chained_middle
                                   SIBLING_BLOCK BB_START
                                   ROT_TWO POP_TOP
                                   BB_END BLOCK_END_FALLTHROUGH_JOIN

        compare_chained        ::= expr chained_parts
        compare_chained        ::= compare_chained37_false
        compare_chained        ::= expr compare_chained_middlea_37
        compare_chained        ::= expr compare_chained_middleb_false

        # "and" with a compare_chained_return
        and_compare_chained_return ::= and_parts
                                   compare_chained_middle_return
                                   BLOCK_END_JOIN BB_START NOT_FALLEN_INTO_BLOCK
                                   ROT_TWO POP_TOP
                                   BB_END BLOCK_END_JOIN


        compare_chained_return ::= expr
                                   compare_chained_middle_return
                                   BB_START NOT_FALLEN_INTO_BLOCK
                                   ROT_TWO POP_TOP
                                   RETURN_VALUE BB_END

        compare_chained_return ::= expr
                                   compare_chained_middle_return
                                   NOT_FALLEN_INTO_BLOCK
                                   BLOCK_END_JUMP_JOIN
                                   BB_START ROT_TWO POP_TOP
                                   BB_END BLOCK_END_FALLTHROUGH_JOIN
                                   BB_START RETURN_VALUE BB_END

        compare_chained_return ::= expr
                                   compare_chained_middle_return
                                   NOT_FALLEN_INTO_BLOCK
                                   BLOCK_END_JUMP_JOIN
                                   BB_START ROT_TWO POP_TOP
                                   BB_END BLOCK_END_FALLTHROUGH_JOIN
                                   BLOCK_END_JUMP_JOIN BB_START RETURN_VALUE BB_END

        compare_chained_return ::= expr
                                   compare_chained_middle_return
                                   NOT_FALLEN_INTO_BLOCK BB_START
                                   ROT_TWO POP_TOP
                                   RETURN_VALUE BB_END

        # FIXME: simplify the compare_chain1 recursion?
        compare_chained_middle ::= expr DUP_TOP ROT_THREE COMPARE_OP jifop
                                   BB_START compare_chained_middle BLOCK_END_JOIN


        compare_chained_middle       ::= expr DUP_TOP ROT_THREE COMPARE_OP jifop
                                   BB_START compare_chained_right BLOCK_END_JOIN

        compare_chained_middle       ::= expr DUP_TOP ROT_THREE COMPARE_OP jifop
                                   BB_START compare_chained_right

        compare_chained_middle_return ::= expr DUP_TOP ROT_THREE COMPARE_OP jifop
                                    BB_START compare_chained_right_return

        compare_chained_middle_return ::= expr DUP_TOP ROT_THREE COMPARE_OP jifop
                                    BB_START compare_chained_right_return BLOCK_END_JOIN

        compare_chained_middle       ::= expr DUP_TOP ROT_THREE COMPARE_OP jifop
                                   BB_START compare_chained_right BLOCK_END_JOIN

        compare_chained_middle       ::= expr DUP_TOP ROT_THREE COMPARE_OP jifop
                                   BB_START compare_chained_right

        compare_chained_middlea_37   ::= chained_parts
                                   compare_chained_righta_37
                                   block_end
                                   POP_TOP block_end

        compare_chained_right     ::= expr COMPARE_OP JUMP_FORWARD BB_END

        compare_chained_right_return ::= expr COMPARE_OP RETURN_VALUE BB_END

        compare_chained_righta_37 ::= expr COMPARE_OP block_end POP_JUMP_IF_TRUE
                                      JUMP_FORWARD BB_END


        # We could propagate loop up through compare_chained and
        # then  to comp_if_xxx etc (e.g comp_if_or2) but this would be
        # too much work. The compromise here is to note the loop
        # in a nonterminal and if we need it, have a reduction check
        # test at the nonterminal symbol level.
        compare_chained37_false        ::= expr
                                           compare_chained_middleb_false_loop

        compare_chained37_false        ::= expr
                                           compare_chained
        """

    def p_conditionals(self, _):
        """
        pjif                       ::= POP_JUMP_IF_FALSE BB_END
        expr_pjif                  ::= expr pjif
        expr_pjif_loop             ::= expr for_jump_pop_iff
        expr_pjif_loop             ::= expr loop_jump_pop_iff
        expr_pjit                  ::= expr POP_JUMP_IF_TRUE BB_END
        expr_pjit_loop             ::= expr for_jump_pop_ift
        expr_pjit_loop             ::= expr loop_jump_pop_ift
        expr_jifop                 ::= expr jifop
        expr_jifop                 ::= branch_op BB_START jifop
        expr_jitop                 ::= expr jitop

        # FIXME: the below two names are horrible and can be confused with the above
        # "expr_pji{f,t} rules. The differences that here we don't care if we
        # loop or not whereas above the two are split out.

        expr_pjiff                 ::= expr pjump_iff
        expr_pjift                 ::= expr pjump_ift
        """

    def p_comprehension(self, _):
        """
        # comp_body is the body of some sort of list, dict, set, or generator
        # comprehension. The body is what adds to the accumulated collection
        # (or contains a "yield" in the case of a generator).

        comp_body      ::= dict_comp_body
        comp_body      ::= gen_comp_body
        comp_body      ::= list_comp_body
        comp_body      ::= set_comp_body

        comp_for       ::= expr get_for_iter BB_START store comp_iter
                           BB_START JUMP_FOR


        # "comp_if" is a comprehension iteration (comp_iter) with some sort of
        # "if" condition which preceeds the iteration.

        # Note: `comp_if_xxx`, we always start with an
        # `expr `and end with a `comp_iter`. Semantic actions
        # expect this.
        #
        # FIXME: Maybe we can refactor this grammar to
        # reduce redundancy?

        comp_if         ::= expr_pjif BB_START
                            comp_iter BLOCK_END_JOIN

        # handles "async for", as in:  {i async for i in (10, 20) if i > 10}
        comp_if         ::= expr_pjiff BB_START
                            comp_iter BLOCK_END_JOIN

        # There can be no BLOCK_END_JOIN in a genxpr_func.
        # Here the return is implicit via a StopIterationException
        comp_if         ::= expr_pjiff BB_START
                            comp_iter

        comp_if         ::= expr_pjif_loop BB_START
                            comp_iter BLOCK_END_JOIN

        comp_and_part   ::= expr for_jump_pop_iff BB_START
        comp_and_part   ::= comp_and_part comp_and_part
        comp_and        ::= comp_and_part expr

        comp_or_part    ::= expr_pjit BB_START
        comp_or         ::= comp_or_part expr_pjit
        comp_or         ::= comp_or BB_START expr

        comp_if_end     ::= JUMP_FOR JUMP_ABSOLUTE BB_END
                            BLOCK_END_JOIN
                            BLOCK_END_JOIN

        comp_if_or3     ::= comp_or
                            for_jump_pop_iff
                            BLOCK_END_JOIN
                            BLOCK_END_JOIN
                            BB_START comp_body
                            comp_if_end

        comp_if_and     ::= comp_and
                            JUMP_FOR
                            POP_JUMP_IF_FALSE_LOOP
                            BB_END
                            BB_START
                            comp_body
                            comp_if_end

        comp_if_or      ::= expr_pjit
                            BB_START
                            expr
                            JUMP_FOR
                            POP_JUMP_IF_FALSE_LOOP
                            BB_END BLOCK_END_JOIN
                            BB_START comp_body
                            comp_if_end

        # We have a bunch of these comp_if_<logic expression>
        # because the logic operation bleeds into the
        # "if" of the comprehension. Note thet specific position of
        # POP_JUMP_IF_xxx_LOOP stays the same.
        comp_if_or      ::= or_parts_pjit
                            expr JUMP_FOR POP_JUMP_IF_FALSE_LOOP
                            bb_end_start
                            comp_iter
        comp_if_or      ::= or_parts_pjit_true_loop
                            expr JUMP_FOR POP_JUMP_IF_FALSE_LOOP
                            bb_end_start
                            comp_iter

        comp_if_or      ::= or_parts_pjit_false_loop
                            expr JUMP_FOR POP_JUMP_IF_FALSE_LOOP
                            bb_end_start
                            comp_iter

        # Here, the "or" is melded a little into the "comp_if" test
        comp_if_or2     ::= compare compare_chained37_false comp_iter

        comp_if_or_not  ::= or_parts_pjit
                            expr JUMP_FOR POP_JUMP_IF_TRUE_LOOP
                            bb_end_start
                            comp_iter


        # We need to have a reduction rule to disambiguate
        # these "comp_if_not" and "comp_if". The difference is burried in the
        # sense of the jump in
        #     comp_iter -> comp_if_or -> or_parts_pjit_false_loop
        # vs.:
        #    comp_iter -> comp_if_or -> or_parts_pjit_true_loop
        #
        # If "true_loop then that goes with "comp_if_not"
        # if "false_loop"  then that goes with comp_if"
        #
        # We might be able to do this in the grammar but it is a bit
        # too pervasive and involved.

        comp_if_not     ::= expr_pjift comp_iter
        comp_if         ::= expr_pjift comp_iter

        # Note the similarity with above "comp_if_not"
        # the following was noticed with an "or True".
        # We probably need to reduc check "comp_if"
        # versus "comp_if_not".
        comp_if         ::= expr_pjift bb_end_start
                            comp_iter

        comp_if_not_and ::= expr_pjif
                            expr JUMP_FOR POP_JUMP_IF_TRUE_LOOP
                            block_end
                            comp_iter
        comp_if_not_or  ::= expr_pjif
                            expr JUMP_FOR POP_JUMP_IF_FALSE_LOOP
                            bb_end_start_opt
                            comp_iter

        # "comp_iter" is a comprehension iteration which
        # contains ultimately a comprehension body.
        # The body is the part that adds to the result
        # and is custom to the kind of comprehension we have.
        # comprehension interations may be comp_if's
        # which is a comprehension together with some condition.

        comp_iter     ::= comp_if BLOCK_END_JOIN
        comp_iter     ::= comp_if_chained
        comp_iter     ::= comp_if_or for_jump_unconditional
                          BLOCK_END_JOIN BLOCK_END_JOIN
        comp_iter     ::= comp_if_and
        comp_iter     ::= comp_if_or2
        comp_iter     ::= comp_if_or3
        comp_iter     ::= comp_if_or_not
        comp_iter     ::= comp_if_not
        comp_iter     ::= comp_if_not_and
        comp_iter     ::= comp_if_not_or

        comp_iter     ::= comp_body for_jump_unconditional BLOCK_END_JOIN
        comp_iter     ::= comp_if
        comp_iter     ::= comp_if_chained
        comp_iter     ::= comp_if_or
        comp_iter     ::= comp_if_or2
        comp_iter     ::= comp_if_or_not
        comp_iter     ::= comp_if_not
        comp_iter     ::= comp_if_not_and
        comp_iter     ::= comp_if_not_or

        comp_iter      ::= comp_for JUMP_ABSOLUTE BB_END BLOCK_END_JOIN
        comp_for       ::= expr gen_comp_body for_jump_unconditional block_end

        # Used in for loops (not async)
        for_loop        ::= BB_START BREAK_FOR LOOP FOR_ITER BB_END

        for_iter        ::= BB_END
                            for_loop

        # Can occur when no trailing "if"
        gen_comp_body   ::= expr
                            YIELD_VALUE
                            BB_END
                            BB_START
                            POP_TOP

        # Can occur when trailing "if"
        gen_comp_body   ::= expr
                            YIELD_VALUE
                            BB_END
                            BLOCK_END_JOIN
                            BB_START
                            POP_TOP

        gen_comp_body   ::= expr
                            YIELD_VALUE
                            BB_END
                            BLOCK_END_JOIN

        gen_comp_func   ::= LOAD_ARG
                            for_iter
                            BB_START
                            store
                            comp_iter

        get_for_iter   ::= GET_ITER for_iter

        # Our "continue" heuristic -  in two successive JUMP_LOOPS, the first
        # one may be a continue - sometimes classifies a JUMP_LOOP
        # as a CONTINUE. The two are kind of the same in a comprehension.

        set_comp_body  ::= expr SET_ADD

        list_comp_body ::= LOAD_FAST LIST_APPEND

        # We can rewrite this as BUILD_SET_0 gen_comp_func
        set_comp_func ::= BUILD_SET_0
                          LOAD_ARG
                          for_iter
                          BB_START
                          store
                          comp_iter

        # FIXME: the BLOCK_END_JOIN may need to be part of something else
        set_comp_func ::= BUILD_SET_0
                          LOAD_ARG
                          for_iter
                          BB_START
                          store
                          comp_iter
                          BLOCK_END_JOIN

        set_comp_func ::= BUILD_SET_0
                          LOAD_ARG
                          for_iter
                          store
                          BB_START
                          comp_iter

        """

    def p_comprehension_dict(self, _):
        """ "
        dict_comp_body ::= expr expr MAP_ADD

        dict_comp_func ::= BUILD_MAP_0
                           LOAD_ARG
                           for_iter
                           BB_START
                           store
                           comp_iter

        dict_comp_func ::= BUILD_MAP_0
                           LOAD_ARG
                           for_iter
                           BB_START
                           store
                           comp_iter
                           BLOCK_END_JOIN


        """

    def p_comprehension_list(self, _):
        """
        lc_body         ::= expr doms_end_start_opt LIST_APPEND
        lc_body         ::= expr dom_end_start_opt LIST_APPEND
        lc_body         ::= branch_op bb_end_start LIST_APPEND

        list_comp      ::= BUILD_LIST_0 list_iter

        list_iter       ::= list_for
        list_iter       ::= list_if
        list_iter       ::= list_if_and_or
        list_iter       ::= list_if_chained
        list_iter       ::= list_if_not
        list_iter       ::= list_if_or
        list_iter       ::= list_if_or_not
        list_iter       ::= lc_body

        set_iter        ::= set_for
        set_iter        ::= list_if_and_or

        set_comp        ::= BUILD_SET_0 set_iter BLOCK_END_JOIN

        # A leading "expr" is used when we have nested list comprehensions. E.g.
        #   ... for dir in dirs for filename in files
        set_for        ::= LOAD_ARG
                           BB_END for_loop
                           BB_START store set_iter
                           for_jump_unconditional
                           BLOCK_END_JOIN


        list_if         ::= branch_op list_if_end list_iter
        list_if         ::= expr list_if_end list_iter

        list_if_and_or  ::= expr_pjiff
                            expr_pjift
                            bb_end_start
                            expr_pjiff
                            list_iter

        list_if_end      ::= pjump_iff_loop bb_end_start_opt

        list_if_not      ::= expr list_if_not_end dom_end_start list_iter
        list_if_not_end  ::= for_jump_pop_ift  bb_end_start_opt
        list_if_not_end  ::= pjump_iff_forward bb_end_start_opt

        # XXX
        list_if_or      ::= expr list_if_not_end list_iter


        list_if_or     ::= expr POP_JUMP_IF_FALSE_LOOP bb_end_start_opt list_iter
        list_if_or_not ::= or1 POP_JUMP_IF_TRUE_LOOP bb_end_start_opt list_iter
        """

    def p_comprehension_set(self, _):
        """
        comp_iter     ::= comp_body
        comp_iter     ::= comp_body BLOCK_END_JOIN
        comp_iter     ::= comp_for BLOCK_END_JOIN
        comp_body     ::= gen_comp_body
        """

    def p_expr(self, _):
        """
        # expressions going to terminal symbols
        expr ::= LOAD_DEREF
        expr ::= LOAD_FAST
        expr ::= LOAD_GLOBAL
        expr ::= LOAD_NAME

        expr ::= attribute
        expr ::= bin_op
        expr ::= branch_op
        expr ::= call

        # Note: in 3.9+ only
        # expr ::= compare_in
        # expr ::= compare_is

        # experimental. Matches AST better though
        expr ::= constant

        expr ::= genexpr_func
        expr ::= list_comp

        expr ::= named_expr
        expr ::= set_comp
        expr ::= subscript

        expr ::= unary_not
        expr ::= unary_op
        expr ::= yield
        expr ::= yield_from

        expr_return ::= compare_return
        expr_return ::= and_compare_chained_return
        expr_return ::= return_expr_lambda

        # In calls, we use "arg" rather than "expr" so we can
        # bound expressions with conditional branches.
        # Arg also matches Python's AST in a Call beter.
        arg              ::= expr
        arg              ::= branch_op block_end

        attribute        ::= expr LOAD_METHOD

        # bin_op (formerly "binary_expr") is the Python AST BinOp
        bin_op            ::= arg arg binary_operator

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
        # What distinguishes these kinds of Boolean expressions from other kinds of
        # expressions, even from those that return True and False (like "is" and "in")
        # is that they have basic block and dominator pseudo instructions.
        # Therefore there will always be a jump or fallthrough a new block
        # after the code.

        branch_op ::= and
        branch_op ::= and BB_START

        branch_op ::= and_or
        branch_op ::= and_or BB_START

        branch_op ::= compare
        branch_op ::= compare BB_START

        branch_op ::= expr_jifop_and
        branch_op ::= expr_jifop_and BB_START

        branch_op ::= or BB_START

        branch_op ::= or_and BB_START

        branch_op ::= or1 block_end

        branch_op ::= or3
        branch_op ::= or3 BB_START

        branch_op ::= or_expr_jitop
        branch_op ::= or_expr_jitop BB_START

        branch_op ::= if_exp block_end
        branch_op ::= if_exp_and block_end
        branch_op ::= if_exp_compare bb_doms_end_opt
        branch_op ::= if_exp_loop
        branch_op ::= if_exp_not block_end
        branch_op ::= if_exp_or block_end
        branch_op ::= if_exp_true block_end


        # The right-hand side of a branch op
        branch_op_part ::= or_parts_pjit block_end

        # A branch op followed by an expr
        branch_op_expr ::= and_or_expr

        # FIXME: the below is to work around test_grammar expecting a "call" to be
        # on the LHS because it is also somewhere on in a rule.
        call              ::= expr CALL_METHOD_0

        compare           ::= compare_chained
        compare           ::= compare_single
        compare_return    ::= compare_chained_return
        compare_single    ::= expr expr COMPARE_OP

        constant ::= LOAD_CONST
        constant ::= LOAD_STR

        # We have this form when "comp_iter" contains
        # a "comp_if" ("if" condition on a comprehension) at the
        # end.
        genexpr_func      ::= LOAD_ARG
                              block_end
                              for_loop
                              BB_START
                              store
                              comp_iter
                              BB_START
                              POP_TOP
                              for_jump_unconditional
                              BLOCK_END_JOIN

        # named_expr is also known as the "walrus op" :=
        named_expr        ::= expr DUP_TOP store

        subscript         ::= expr expr BINARY_SUBSCR

        # unary_op (formerly "unary_expr") is the Python AST UnaryOp
        unary_op          ::= arg unary_operator

        unary_operator    ::= UNARY_POSITIVE
        unary_operator    ::= UNARY_NEGATIVE
        unary_operator    ::= UNARY_INVERT
        unary_operator    ::= UNARY_NOT

        unary_not         ::= expr UNARY_NOT

        yield             ::= expr YIELD_VALUE BB_END
        yield_from        ::= expr
                              GET_YIELD_FROM_ITER LOAD_CONST YIELD_FROM
        """

    # Conditional jumps with dominator information included
    def p_jump_conditional(self, _):
        """
        for_jump_pop_iff   ::= JUMP_FOR POP_JUMP_IF_FALSE_LOOP BB_END
        for_jump_pop_ift   ::= JUMP_FOR POP_JUMP_IF_TRUE_LOOP BB_END

        jifop              ::= JUMP_IF_FALSE_OR_POP BB_END
        jitop              ::= JUMP_IF_TRUE_OR_POP BB_END

        and_or_expr        ::= expr_jitop BLOCK_END_JOIN BB_START and_or_expr BLOCK_END_JOIN

        and_or_expr1       ::= expr_pjif BB_START expr_jitop BLOCK_END_JOIN BB_START and
                               BLOCK_END_JOIN

        loop_jump_pop_iff  ::= JUMP_LOOP POP_JUMP_IF_FALSE_LOOP
        loop_jump_pop_ift  ::= JUMP_LOOP POP_JUMP_IF_TRUE_LOOP

        pjump_iff          ::= for_jump_pop_iff
        pjump_iff          ::= pjump_iff_forward
        pjump_iff          ::= pjump_iff_loop
        pjump_iff_forward  ::= POP_JUMP_IF_FALSE dom_end_start_opt
        pjump_iff_loop     ::= JUMP_LOOP POP_JUMP_IF_FALSE_LOOP BB_END

        pjump_ift          ::= POP_JUMP_IF_TRUE
        pjump_ift          ::= for_jump_pop_ift

        """

    # Unconditional jumps
    def p_jump_unconditional(self, _):
        """
        for_jump_unconditional ::= for_loop_unconditional
        for_loop_unconditional ::= JUMP_LOOP JUMP_ABSOLUTE BB_END
        for_jump_unconditional ::= JUMP_FOR JUMP_ABSOLUTE BB_END

        jf_bb_end_start        ::= JUMP_FORWARD bb_end_start
        jf_doms_end_start      ::= JUMP_FORWARD bb_doms_end_start
        """

    def p_lambda(self, _):
        """
        # return_expr is a return value used inside a lambda

        return_expr               ::= expr RETURN_VALUE
        return_expr               ::= expr RETURN_VALUE BB_END
        return_expr               ::= expr_return
        return_expr               ::= if_exp_return
        return_expr               ::= if_else_lambda_return

        # This is wrong and control_flow may need fixing.

        return_expr               ::= if_exp_and_return
        return_expr               ::= expr return_value
        return_expr               ::= if_exp_return

        # FIXME: generalize this
        return_expr             ::= dict_comp_func
                                    RETURN_VALUE
                                    BB_END
                                    BLOCK_END_JOIN_NO_ARG

        return_expr             ::= dict_comp_func
                                    BB_START
                                    RETURN_VALUE
                                    block_join_end_final

        return_expr             ::= dict_comp_func
                                    BLOCK_END_JOIN
                                    BB_START RETURN_VALUE BB_END

        return_expr             ::= gen_comp_func
                                    BB_START
                                    LOAD_CONST
                                    RETURN_VALUE

        return_expr             ::= set_comp
                                    BB_START
                                    RETURN_VALUE
                                    BB_END
                                    BLOCK_END_JOIN_NO_ARG

        return_expr             ::= set_comp_func
                                    BB_START
                                    RETURN_VALUE
                                    block_join_end_final

        return_expr             ::= set_comp_func
                                    BLOCK_END_JOIN
                                    BB_START RETURN_VALUE BB_END

        return_expr             ::= genexpr_func
                                    BB_START
                                    LOAD_CONST
                                    RETURN_VALUE
                                    block_join_end_final

        return_expr             ::= expr RETURN_VALUE BB_END
        return_expr             ::= branch_op_expr BB_START RETURN_VALUE BB_END

        return_expr_lambda      ::= if_exp_binop_lambda
        return_expr_lambda      ::= if_exp_dead_code
        return_expr_lambda      ::= if_exp_lambda
        return_expr_lambda      ::= if_else_lambda_return
        return_expr_lambda      ::= if_exp_not_lambda

        # return_expr_lambda with a binary operator before the return
        return_expr_binop_lambda  ::= dom_start_opt
                                      expr
                                      binary_operator
                                      RETURN_VALUE
                                      bb_doms_end

        # Temporary until we have a rule generating this
        return_expr_lambda      ::= if_exp_call_lambda

        # AST IfExp (if .. and .. else) with return on both branches such as
        # inside a lambda.

        if_exp_and_return   ::= expr_pjif BB_START
                                expr_pjif BB_START
                                return_expr
                                BLOCK_END_JOIN BB_START
                                NOT_FALLEN_INTO_BLOCK
                                return_expr

        # AST IfExp (if else) with return on both branches such as
        # inside a lambda.

        if_exp_return       ::= expr_pjif
                                BB_START
                                return_expr
                                BB_START
                                NOT_FALLEN_INTO_BLOCK
                                return_expr

        if_else_lambda_return ::= branch_op
                                  BB_START return_expr_lambda
                                  BB_START NOT_FALLEN_INTO_BLOCK
                                  return_expr_lambda


        # Something is weird about the bb_end_start
        # in our parser in that if we replace it with say
        # "block_end", we get parse errors
        # Same deal in trying to combine the following to "if_exp_lambda"
        # rules into one.
        if_exp_lambda      ::= branch_op
                               POP_JUMP_IF_FALSE
                               bb_end_start_opt
                               expr
                               return_value
                               bb_doms_end_start
                               NOT_FALLEN_INTO_BLOCK
                               return_expr_lambda


        if_exp_lambda      ::= expr
                               POP_JUMP_IF_FALSE
                               bb_end_start_opt
                               expr
                               return_value
                               bb_doms_end_start
                               NOT_FALLEN_INTO_BLOCK
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
                              return_value
                              bb_end_start
                              return_expr_lambda
        """

    def p_no_fallthrough(self, _):
        """
        # short-circuit expressions that have RETURN_VALUEs at the end
        # (e.g. return 1 < i < n) may need NOT_FALLEN_INTO_BLOCK
        # because the expression *before* (1 < i) the final one, (i <
        # n), may also end in a RETURN_VALUE, instead of jumping to the
        # end of the compound expression

        return_value              ::= NOT_FALLEN_INTO_BLOCK RETURN_VALUE
        """

    def p_store(self, _):
        """
        store           ::= STORE_DEREF
        store           ::= STORE_FAST

        # store NAME appears in nested lambdas
        store           ::= STORE_NAME
        store           ::= store_subscript

        # Used in comprehensions with subscripts, e.g.
        # [0 for x[0] in __file__]
        #       ^^^^
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
        Python3_8LambdaCustom.__init__(self)

    def customize_grammar_rules(self, tokens, customize):
        self.customize_grammar_rules_lambda3_8(tokens, customize)


if __name__ == "__main__":
    # Check grammar
    from decompile_cfg.parsers.dump import dump_and_check

    # The start_symbol here is something from this file to check.
    # Note that the start_symbol from parse_heads is "lambda_start"
    # which is the same thing surrounded by dominator information.
    # But that doesn't appear here.
    p = Python3_8LambdaParser(start_symbol="lambda_start")
    modified_tokens = set(
        """JUMP_FOR JUMP_LOOP CONTINUE BB_END BB_START DOM_END DOM_START""".split()
    )

    dump_and_check(p, (3, 8), modified_tokens, set(["lambda_start"]))
