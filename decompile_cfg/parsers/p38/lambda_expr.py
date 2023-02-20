#  Copyright (c) 2020-2023 Rocky Bernstein
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

        # An "and" is one or more "and_parts" followed by a BLOCK_END_JOIN

        # The "and" rule form with the "BB_END" is the inner-most "and".
        # All the other nested "ands" omit the "BB_END".

        and_parts       ::= expr_jifop BB_START
        and_parts       ::= expr_jifop BB_START and_part
        and             ::= and_parts expr BB_END block_end_joins
        and             ::= and_parts expr block_end_joins


        and2            ::= and_parts_jifop
                            bb_end_start
                            expr

        # and_part_pjif are the right-hand side of an "and" without the leading expr
        and_part_pjif   ::= expr_pjif
        and_parts_pjif  ::= and_part_pjif+

        and_parts_jifop ::= and_part_jifop+

        and1            ::= and_parts_pjif BB_START expr

        # Outer "or"s that contain other "or" will not have a BB_END before BLOCK_END_JOIN
        or              ::= expr_jitop
                            BB_START
                            expr
                            BLOCK_END_JOIN

        # The inner-most "or" can have a BB_END before the JOIN
        or              ::= expr_jitop
                            BB_START
                            expr
                            BB_END BLOCK_END_JOIN


        or_part_pjit         ::= expr_pjit
        or_parts_pjit        ::= expr_pjit BB_START or_part_pjit

        or_part_pjit_true_loop  ::= expr_pjit_loop
        or_parts_pjit_true_loop ::= or_part_pjit_true_loop+

        # FIXME: something may be fishy here.
        # We probably need a reduction rule to distinguish the false and true jumps.
        or_part_pjit_false_loop  ::= expr_pjif_loop
        or_parts_pjit_false_loop ::= or_part_pjit_false_loop+

        or1                 ::= or_parts_pjit expr

        # and_or is (a and ...) or y

        # Note: I don't know why, but  we can't replace "expr jitop expr"
        # with "or"
        and_or              ::= and_parts_pjif
                                BB_START
                                expr_jitop
                                BLOCK_END_JOIN BLOCK_END_JOIN BB_START
                                expr
                                BB_END BLOCK_END_JOIN

        and_or_expr         ::= expr_pjif
                                BB_START
                                expr_jitop
                                BLOCK_END_JOIN BB_START
                                expr
                                BB_END BLOCK_END_JOIN

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

        # or_and is (a or ...) and y

        or_and         ::= or_parts_pjit
                           BB_START
                           expr_jifop
                           block_end_joins BB_START
                           expr
                           BB_END BLOCK_END_JOIN

        or_and         ::= or_parts_pjit
                           BB_START
                           expr_jifop
                           block_end_joins BB_START
                           branch_op


        or_and         ::= or_parts_pjit
                           BB_START
                           expr_jifop
                           block_end_joins BB_START
                           branch_op

        # "expr" below at end instead of block_end_joins above
        # when "and" part is a simple expression
        or_and         ::= expr_pjit
                           BB_START
                           expr_jifop
                           block_end_joins BB_START
                           expr
                           BB_END BLOCK_END_JOIN


        if_exp_dead_code   ::= return_expr_lambda
                               bb_end_start
                               return_expr_lambda

        # Corresponds to AST IfExp; note this
        # must include an "else" part.
        # Don't confuse with comprehension if's
        if_exp        ::= if_exp_jump_false
        if_exp        ::= if_exp_jump_true

        if_exp_jump_false ::= expr
                              POP_JUMP_IF_FALSE
                              bb_end_start_opt
                              expr
                              jf_bb_end_start
                              expr

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

    def p_chained(self, args):
        """
        chained_part         ::= expr
                                 DUP_TOP ROT_THREE COMPARE_OP
                                 bb_doms_end_start_opt
                                 POP_JUMP_IF_FALSE
        chained_parts        ::= chained_part+

        # A "compare_chained" is two comparisions like x <= y <= z
        # In the Python docs it says "Comparisons can be chained ..."
        # In the Python AST, this appears as: Compare(.. ops=)

        compare_chained      ::= expr
                                 compare_chained1
                                 block_end
                                 not_fallen_into_block_opt
                                 ROT_TWO POP_TOP
                                 bb_doms_end_start_opt

        compare_chained      ::= expr chained_parts
        compare_chained      ::= compare_chained37_false
        compare_chained      ::= expr compare_chained1a_37
        compare_chained      ::= expr compare_chained1b_false


        # FIXME: simplify the compare_chain1 recursion?
        compare_chained1     ::= expr DUP_TOP ROT_THREE COMPARE_OP jifop_opt
                                 compare_chained1

        compare_chained1     ::= expr DUP_TOP ROT_THREE COMPARE_OP jifop_opt
                                 compare_chained2 bb_doms_end_start_opt

        compare_chained1a_37 ::= chained_parts
                                 compare_chained2a_37
                                 block_end
                                 POP_TOP block_end

        compare_chained2     ::= expr COMPARE_OP JUMP_FORWARD
        compare_chained2     ::= expr COMPARE_OP return_value

        compare_chained2a_37 ::= expr COMPARE_OP block_end POP_JUMP_IF_TRUE JUMP_FORWARD


        # When used in an "if" of a comprehension
        compare_chained_comprehension  ::= expr DUP_TOP ROT_THREE COMPARE_OP pjump_iff_forward
                                           compare_chained2_comprehension

        compare_chained2_comprehension ::= expr
                                           COMPARE_OP
                                           loop_jump_pop_iff
                                           JUMP_FORWARD
                                           bb_end_start_opt

        # We could propagate loop up through compare_chained and
        # then  to comp_if_xxx etc (e.g comp_if_or2) but this would be
        # too much work. The compromise here is to note the loop
        # in a nonterminal and if we need it, have a reduction check
        # test at the nonterminal symbol level.
        compare_chained37_false        ::= expr
                                           compare_chained1b_false_loop

        compare_chained37_false        ::= expr
                                           compare_chained

        compare_chained1b_false        ::= chained_parts
                                           bb_end_start
                                           compare_chained2b_false
                                           POP_TOP jump
                                           bb_doms_end_start_opt

        compare_chained1b_false_loop   ::= chained_parts
                                           bb_end_start
                                           compare_chained2b_false_loop
                                           POP_TOP jump bb_doms_end_start_opt

        compare_chained1b_false_loop   ::= expr
                                           compare_chained2b_false_loop
                                           POP_TOP JUMP_LOOP bb_doms_end_start_opt

        compare_chained2b_false        ::= expr COMPARE_OP
                                           POP_JUMP_IF_FALSE
                                           bb_end_start_opt
                                           jump_or_break
                                           block_end
                                           SIBLING_BLOCK


        compare_chained2b_false_loop   ::= expr COMPARE_OP
                                           bb_end_start_opt
                                           loop_jump_pop_iff
                                           jump_or_break
                                           block_end

        compare_chained2b_false_loop   ::= expr COMPARE_OP
                                           bb_end_start_opt
                                           for_jump_pop_iff
                                           jump_or_break
                                           block_end


        """

    # Dominator and basic block pseudo operations needed
    # to assist control flow
    def p_dom(self, args):
        """
        dom_start          ::= DOM_START BB_START
        dom_start_opt      ::= dom_start?
        dom_end            ::= BB_END DOM_END
        bb_end_start       ::= BB_END block_start
        bb_end_start_opt   ::= bb_end_start?
        bb_doms_end        ::= BB_END doms_end
        bb_doms_end_opt    ::= bb_doms_end?

        block_end           ::= BB_END
        block_end           ::= BB_END BLOCK_END_JOIN_NO_ARG
        block_end_joins     ::= BLOCK_END_JOIN+
        block_end_joins_opt ::= BLOCK_END_JOIN+

        block_start        ::= BB_START

        dom_end_opt        ::= dom_end?
        doms_end           ::= DOM_END+
        dom_end_opt        ::= dom_end?
        dom_end_start      ::= dom_end dom_start
        dom_end_start_opt  ::= dom_end_start?
        doms_end_start_opt ::= bb_doms_end dom_start

        bb_end_start          ::= BB_END dom_start
        bb_doms_end_start     ::= bb_doms_end dom_start
        bb_doms_end_start_opt ::= bb_doms_end_start?

        # In contrast to bb_ends, a block_end can include dominator regions.
        block_end        ::= bb_end_start_opt
        block_end        ::= bb_doms_end_start
        """

    def p_conditionals(self, args):
        """
        expr_pjif                  ::= expr POP_JUMP_IF_FALSE BB_END
        expr_pjif_loop             ::= expr for_jump_pop_iff
        expr_pjif_loop             ::= expr loop_jump_pop_iff
        expr_pjit                  ::= expr POP_JUMP_IF_TRUE BB_END
        expr_pjit_loop             ::= expr for_jump_pop_ift
        expr_pjit_loop             ::= expr loop_jump_pop_ift
        expr_jifop                 ::= expr JUMP_IF_FALSE_OR_POP BB_END
        expr_jitop                 ::= expr JUMP_IF_TRUE_OR_POP BB_END

        # FIXME: the below two names are horrible and can be confused with the above
        # "expr_pji{f,t} rules. The differences that here we don't care if we
        # loop or not whereas above the two are split out.

        expr_pjiff                 ::= expr pjump_iff
        expr_pjift                 ::= expr pjump_ift
        """

    def p_comprehension(self, args):
        """
        comp_body      ::= dict_comp_body
        comp_body      ::= gen_comp_body
        comp_body      ::= list_comp_body
        comp_body      ::= set_comp_body

        # I think this can be removed:
        # comp_for     ::= expr get_for_iter store comp_iter
        #                  CONTINUE
        #                  bb_end_start_opt

        comp_for       ::= expr get_for_iter store comp_iter
                           for_jump_unconditional
                           block_end


        # Note: `comp_if_xxx`, we always start with an
        # `expr `and end with a `comp_iter`. Semantic actions
        # expect this.
        #
        # FIXME: Maybe we can refactor this grammar to
        # reduce redundancy?

        comp_if         ::= expr_pjif
                            comp_iter

        comp_if         ::= expr_pjiff
                            comp_iter

        comp_if         ::= expr_pjif_loop
                            comp_iter

        comp_if_chained ::= list_if_compare
                            bb_end_start
                            POP_TOP jump_loop_absolute
                            bb_doms_end_start
                            comp_iter


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
        comp_if         ::= expr_pjift bb_end_start comp_iter

        comp_if_not_and ::= expr_pjif
                            expr JUMP_FOR POP_JUMP_IF_TRUE_LOOP
                            block_end
                            comp_iter
        comp_if_not_or  ::= expr_pjif
                            expr JUMP_FOR POP_JUMP_IF_FALSE_LOOP
                            bb_end_start_opt
                            comp_iter

        comp_iter     ::= comp_body
        comp_iter     ::= comp_if
        comp_iter     ::= comp_if_chained
        comp_iter     ::= comp_if_or
        comp_iter     ::= comp_if_or2
        comp_iter     ::= comp_if_or_not
        comp_iter     ::= comp_if_not
        comp_iter     ::= comp_if_not_and
        comp_iter     ::= comp_if_not_or

        comp_iter      ::= comp_for
        comp_for       ::= expr gen_comp_body for_jump_unconditional block_end

        expr_or_arg     ::= LOAD_ARG
        expr_or_arg     ::= expr

        for_loop        ::= BREAK_FOR LOOP FOR_ITER

        for_iter        ::= bb_end_start_opt
                            for_loop
                            bb_end_start

        gen_comp_body   ::= expr
                            bb_doms_end_start_opt
                            YIELD_VALUE
                            block_end
                            POP_TOP

        generator_exp   ::= expr_or_arg
                            bb_end_start
                            for_loop
                            bb_end_start
                            store
                            comp_iter
                            for_jump_unconditional
                            block_end

        get_for_iter   ::= GET_ITER block_end for_iter

        # Our "continue" heuristic -  in two successive JUMP_LOOPS, the first
        # one may be a continue - sometimes classifies a JUMP_LOOP
        # as a CONTINUE. The two are kind of the same in a comprehension.

        set_comp_body  ::= expr SET_ADD
        set_comp_body  ::= expr block_end SET_ADD


        list_comp_body ::= LOAD_FAST LIST_APPEND

        set_comp_func ::= BUILD_SET_0
                          expr_or_arg
                          bb_end_start_opt
                          for_iter store comp_iter
                          for_jump_unconditional
                          block_end
        """

    def p_comprehension_dict(self, args):
        """ "
        dict_comp_body ::= expr expr MAP_ADD

        dict_comp_func ::= BUILD_MAP_0
                          expr_or_arg
                          bb_end_start_opt
                          for_iter
                          store
                          comp_iter
                          for_jump_unconditional
                          bb_doms_end_start
                          RETURN_VALUE
                          bb_doms_end
        """

    def p_comprehension_list(self, args):
        """
        lc_body         ::= expr doms_end_start_opt LIST_APPEND
        lc_body         ::= expr dom_end_start_opt LIST_APPEND
        lc_body         ::= branch_op bb_end_start LIST_APPEND

        list_comp      ::= BUILD_LIST_0 list_iter
        list_comp_func ::= BUILD_LIST_0
                           expr_or_arg
                           bb_end_start_opt
                           for_iter store comp_iter
                           for_jump_unconditional
                           dom_end_start_opt

        list_iter       ::= list_for
        list_iter       ::= list_if
        list_iter       ::= list_if_and_or
        list_iter       ::= list_if_chained
        list_iter       ::= list_if_not
        list_iter       ::= list_if_or
        list_iter       ::= list_if_or_not
        list_iter       ::= lc_body

        set_iter        ::= set_for
        set_iter        ::= list_if
        set_iter        ::= list_if_and_or
        set_iter        ::= list_if_chained
        set_iter        ::= list_if_not
        set_iter        ::= set_comp_body

        set_comp        ::= BUILD_SET_0 set_iter

        # A leading "expr" is used when we have nested list comprehensions. E.g.
        #   ... for dir in dirs for filename in files
        list_for        ::= expr_or_arg
                            for_iter
                            store list_iter
                            for_jump_unconditional
                            bb_doms_end_start_opt

        set_for        ::= expr_or_arg
                           for_iter
                           store set_iter
                           for_jump_unconditional
                           bb_doms_end_start_opt

        list_if         ::= branch_op list_if_end list_iter
        list_if         ::= expr list_if_end list_iter

        list_if         ::= expr for_jump_iff list_iter
        list_if_chained ::= list_if_compare
                            bb_end_start
                            POP_TOP for_jump_unconditional
                            bb_doms_end_start
                            list_iter

        list_if_chained ::= list_if_compare
                            bb_end_start
                            POP_TOP for_jump_unconditional
                            bb_doms_end_start
                            list_iter

        list_if_compare ::= expr compare_chained_comprehension
        list_if_compare ::= expr compare_chained

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
        expr ::= call
        expr ::= compare

        # Note: in 3.9+ only
        # expr ::= compare_in
        # expr ::= compare_is

        # experimental. Matches AST better though
        expr ::= constant

        expr ::= genexpr_func
        expr ::= list
        expr ::= list_comp

        expr ::= named_expr
        expr ::= set_comp
        expr ::= subscript

        expr ::= unary_not
        expr ::= unary_op
        expr ::= yield
        expr ::= yield_from

        # In calls, we use "arg" rather than "expr" so we can
        # bound expressions with conditional branches.
        # Arg also matches Python's AST in a Call beter.
        arg              ::= expr
        arg              ::= branch_op block_end

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

        branch_op ::= and
        branch_op ::= and BB_START

        branch_op ::= and_or_expr
        branch_op ::= and_or_expr BB_START

        branch_op ::= and_or
        branch_op ::= and_or BB_START

        branch_op ::= or_and
        branch_op ::= or_and BB_START

        branch_op ::= and_or_expr
        branch_op ::= and_or_expr BB_START

        branch_op ::= and1
        branch_op ::= and1 BB_START

        branch_op ::= or
        branch_op ::= or BB_START

        branch_op ::= or1 block_end

        branch_op ::= if_exp block_end
        branch_op ::= if_exp_and block_end
        branch_op ::= if_exp_compare bb_doms_end_opt
        branch_op ::= if_exp_loop
        branch_op ::= if_exp_not block_end
        branch_op ::= if_exp_or block_end
        branch_op ::= if_exp_true block_end


        branch_op_compound_prefix ::= branch_op DOM_START BB_START unary_operator
        branch_op_compound_suffix ::= branch_op DOM_START BB_START expr binary_operator

        # The right-hand side of a branch op
        branch_op_part ::= and_parts_pjif block_end
        branch_op_part ::= or_parts_pjit block_end

        # FIXME: the below is to work around test_grammar expecting a "call" to be
        # on the LHS because it is also somewhere on in a rule.
        call              ::= expr CALL_METHOD_0

        compare           ::= compare_chained
        compare           ::= compare_single
        compare_single    ::= expr expr COMPARE_OP

        # Note: in 3.9+ only
        # compare_is        ::= expr expr IS_OP
        # compare_in        ::= expr expr CONTAINS_OP

        constant ::= LOAD_CONST
        constant ::= LOAD_STR

        genexpr_func      ::= LOAD_ARG
                              block_end
                              for_loop
                              bb_end_start
                              store
                              comp_iter
                              for_jump_unconditional
                              block_end


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

        yield             ::= expr YIELD_VALUE
        yield_from        ::= expr
                              GET_YIELD_FROM_ITER LOAD_CONST YIELD_FROM
        """

    # Conditional jumps with dominator information included
    def p_jump_conditional (self, args):
        """
        for_jump_pop_iff   ::= JUMP_FOR POP_JUMP_IF_FALSE_LOOP
        for_jump_pop_ift   ::= JUMP_FOR POP_JUMP_IF_TRUE_LOOP

        jifop_opt          ::= JUMP_IF_FALSE_OR_POP bb_end_start_opt
        jifop_start        ::= JUMP_IF_FALSE_OR_POP bb_end_start

        jitop              ::= JUMP_IF_TRUE_OR_POP BB_END

        loop_jump_pop_iff  ::= JUMP_LOOP POP_JUMP_IF_FALSE_LOOP
        loop_jump_pop_ift  ::= JUMP_LOOP POP_JUMP_IF_TRUE_LOOP

        pjump_iff          ::= for_jump_pop_iff
        pjump_iff          ::= pjump_iff_forward
        pjump_iff          ::= pjump_iff_loop
        pjump_iff_forward  ::= POP_JUMP_IF_FALSE dom_end_start_opt
        pjump_iff_loop     ::= JUMP_FOR POP_JUMP_IF_FALSE_LOOP dom_end_start_opt
        pjump_iff_loop     ::= JUMP_LOOP POP_JUMP_IF_FALSE_LOOP dom_end_start_opt

        pjump_ift          ::= POP_JUMP_IF_TRUE
        pjump_ift          ::= for_jump_pop_ift

        """

    # Unconditional jumps
    def p_jump_unconditional(self, args):
        """
        for_jump_unconditional ::= JUMP_LOOP JUMP_ABSOLUTE
        for_jump_unconditional ::= JUMP_FOR JUMP_ABSOLUTE

        jf_bb_end_start        ::= JUMP_FORWARD bb_end_start
        jf_doms_end_start      ::= JUMP_FORWARD bb_doms_end_start

        jump                   ::= JUMP_FORWARD
        jump                   ::= JUMP_LOOP JUMP_ABSOLUTE
        jump                   ::= for_jump_unconditional

        # Note: full.py has jump_or_break ::= BREAK_LOOP
        jump_or_break          ::= jump

        # async_iter uses this. Maybe we should use afor_jump_unconditional?
        jump_loop_absolute     ::= JUMP_LOOP JUMP_ABSOLUTE

        """

    def p_lambda(self, args):
        """
        # return_expr_lambda is a return value used inside a lambda

        return_expr               ::= expr RETURN_VALUE
        return_expr               ::= expr return_value

        # return_expr_lambda      ::= dom_start
        #                             expr
        #                             dom_start_opt
        #                             return_value
        #                             bb_doms_end

        # We need a block_end because there can be a jump
        # in a conditional to just before the RETURN_VALUE
        return_expr_lambda      ::= dom_start_opt
                                    expr
                                    block_end
                                    return_value
                                    bb_doms_end

        # FIXME: generalize this
        return_expr_lambda      ::= dom_start_opt
                                    dict_comp_func
                                    RETURN_VALUE
                                    bb_doms_end

        return_expr_lambda      ::= dom_start_opt
                                    dict_comp_func

        return_expr_lambda      ::= dom_start_opt
                                    generator_exp
                                    LOAD_CONST
                                    RETURN_VALUE
                                    bb_doms_end

        return_expr_lambda      ::= dom_start_opt
                                    list_comp_func
                                    RETURN_VALUE
                                    bb_doms_end

        return_expr_lambda      ::= dom_start_opt
                                    set_comp_func
                                    RETURN_VALUE
                                    bb_doms_end

        return_expr_lambda      ::= if_exp_binop_lambda
        return_expr_lambda      ::= if_exp_dead_code
        return_expr_lambda      ::= if_exp_lambda
        return_expr_lambda      ::= if_exp_not_lambda

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
                               return_value
                               bb_doms_end_start
                               NOT_FALLEN_INTO_BLOCK
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

    def p_no_fallthrough(self, args):
        """
        # short-circuit expressions that have RETURN_VALUEs at the end
        # (e.g. return 1 < i < n) may need NOT_FALLEN_INTO_BLOCK
        # because the expression *before* (1 < i) the final one, (i <
        # n), may also end in a RETURN_VALUE, instead of jumping to the
        # end of the compound expression

        return_value              ::= NOT_FALLEN_INTO_BLOCK RETURN_VALUE
        not_fallen_into_block_opt ::= NOT_FALLEN_INTO_BLOCK?

        """

    def p_store(self, args):
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
        """JUMP_FOR JUMP_LOOP CONTINUE BB_END BB_START DOM_END DOM_START""".split()
    )

    dump_and_check(p, (3, 8), modified_tokens, set(["lambda_start"]))
