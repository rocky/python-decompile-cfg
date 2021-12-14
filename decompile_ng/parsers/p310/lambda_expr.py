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
used as a superclass in other grammars, such as a full grammar for Python 3.10.
"""

from decompile_ng.parsers.p310.base import Python310BaseParser
from decompile_ng.parsers.parse_heads import PythonParserLambda, PythonBaseParser
from decompile_ng.parsers.treenode import SyntaxTree
from spark_parser import DEFAULT_DEBUG as PARSER_DEFAULT_DEBUG

class Python310LambdaParser(Python310BaseParser, PythonParserLambda):
    def p_310walrus(self, args):
        """
        # named_expr is also known as the "walrus op" :=
        expr              ::= named_expr
        named_expr        ::= expr DUP_TOP store
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

        bb_doms_end_start_opt ::= bb_doms_end dom_start
        bb_doms_end_start_opt ::=
        """

    # Conditional jumps with dominator information included
    def p_310conditional_jump(self, args):
        """
        jifop       ::= JUMP_IF_FALSE_OR_POP BB_END dom_start
        # jitop       ::= JUMP_IF_TRUE_OR_POP BB_END dom_start
        jifop_expr  ::= JUMP_IF_FALSE_OR_POP bb_doms_end dom_start expr
        jitop_expr  ::= JUMP_IF_TRUE_OR_POP bb_doms_end dom_start expr
        """

    def p_310lambda(self, args):
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

    def p_310bool_ops(self, args):
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

        #### Below not gone over

        # Note: "and" like "nor" might not have a trailing "come_from".
        #       "nand" and "or", in contrast, *must* have at least one "come_from".
        not_or       ::= and_parts expr_pjif _come_froms

        # Nonterminals that end in "_cond" are used in "conditions":
        # used for testing in control structures where the test is important and
        # the value popped. Conditions also generally have non-local COME_FROMs
        # that often need to be checked in the control structure. This is for example
        # how we determine the difference between some "if not (not a or b) versus
        # "if a and b".

        and_cond     ::= and_parts expr_pjif _come_froms
        and_cond     ::= testfalse expr_pjif _come_froms
        and_not_cond ::= and_not

        nand       ::= and_parts expr_pjit  come_froms
        c_nand     ::= and_parts expr_pjift come_froms

        # Note: "nor" like "and" might not have a trailing "come_from".
        #       "nand" and "or_cond", in contrast, *must* have at least one "come_from".
        or_cond     ::= or_parts expr_pjif come_froms
        or_cond     ::= not_and_not expr_pjif come_froms
        or_cond1    ::= and POP_JUMP_IF_TRUE come_froms expr_pjif come_from_opt

        nor_cond    ::= or_parts expr_pjif

        # When we alternating and/or's such as:
        #    a and (b or c) and d
        # instead of POP_JUMP_IF_TRUE, JUMP_IF_FALSE_OR_POP is sometimes be used
        # The semantic rules for "and" require expr-like things in positions 0 and 1,
        # thus the use of expr_jifop_cfs below.

        or_and1        ::= or_parts and_parts come_froms
        # and_or         ::= expr_jifop expr come_from_opt JUMP_IF_TRUE_OR_POP expr _come_froms

        ## A COME_FROM is dropped off because of JUMP-to-JUMP optimization
        # and       ::= expr_pjif expr

        ## Note that "POP_JUMP_IF_FALSE" is what we check on in the "and" reduce rule.
        # and       ::= expr_pjif expr COME_FROM

        jump_if_false_cf ::= POP_JUMP_IF_FALSE COME_FROM
        and_or_cond      ::= and_parts expr POP_JUMP_IF_TRUE come_froms expr_pjif _come_froms

        # For "or", keep index 0 and 1 be the two expressions.

        or        ::= expr_pjit  expr COME_FROM
        or        ::= expr_pjit  expr jump_if_false_cf

        or_expr ::= expr JUMP_IF_TRUE expr COME_FROM
        """

    # def p_come_froms(self, args):
    #     """
    #     # Zero or one COME_FROM
    #     # And/or expressions have this
    #     come_from_opt ::= COME_FROM?

    #     # One or more COME_FROMs - joins of tryelse's have this
    #     come_froms    ::= COME_FROM+

    #     # Zero or more COME_FROMs - loops can have this
    #     _come_froms   ::= COME_FROM*
    #     _come_froms   ::= COME_FROM_LOOP
    #     """

    def p_jump(self, args):
        """
        jump               ::= JUMP_FORWARD
        jump               ::= JUMP_BACK
        jump_or_break      ::= jump
        jump_or_break      ::= BREAK_LOOP

        # These are used to keep parse tree indices the same
        # in "if"/"else" like rules.
        jump_forward_else  ::= JUMP_FORWARD _come_froms
        jump_forward_else  ::= come_froms jump COME_FROM

        pjump_ift          ::= POP_JUMP_IF_TRUE
        pjump_ift          ::= POP_JUMP_IF_TRUE_BACK

        pjump_iff          ::= POP_JUMP_IF_FALSE
        pjump_iff          ::= POP_JUMP_IF_FALSE_BACK

        # pjump              ::= pjump_iff
        # pjump              ::= pjump_ift
        """

    def p_310chained(self, args):
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

        compare_chained     ::= compare_chained37
        compare_chained     ::= compare_chained37_false

        compare_chained_and ::= expr chained_parts
                                compare_chained2a_false_37
                                come_froms
                                POP_TOP JUMP_FORWARD COME_FROM
                                negated_testtrue
                                come_froms

        # We don't use testtrue directly because we need to tell the semantic
        # action to negate the testtrue
        negated_testtrue ::= testtrue


        c_compare_chained   ::= c_compare_chained37_false

        compare_chained37   ::= expr chained_parts
        compare_chained37   ::= expr compare_chained1a_37
        compare_chained37   ::= expr compare_chained1c_37
        c_compare_chained37   ::= expr c_compare_chained1a_37
        # c_compare_chained37   ::= expr c_compare_chained1c_37

        compare_chained37_false   ::= expr compare_chained1_false_37
        compare_chained37_false   ::= expr compare_chained1b_false_37
        compare_chained37_false   ::= expr compare_chained2_false_37

        c_compare_chained37_false ::= expr c_compare_chained2_false_37
        c_compare_chained37_false ::= expr c_compare_chained1b_false_37
        c_compare_chained37_false ::= compare_chained37_false

        chained_parts              ::= chained_part+
        chained_part               ::= expr DUP_TOP ROT_THREE COMPARE_OP come_from_opt POP_JUMP_IF_FALSE

        # c_chained_parts            ::= c_chained_part+
        # c_chained_part             ::= expr DUP_TOP ROT_THREE COMPARE_OP come_from_opt POP_JUMP_IF_FALSE_BACK
        # c_chained_parts            ::= chained_parts


        compare_chained1a_37       ::= chained_parts
                                       compare_chained2a_37 COME_FROM
                                       POP_TOP come_from_opt
        c_compare_chained1a_37     ::= chained_parts
                                       c_compare_chained2a_37 COME_FROM
                                       POP_TOP come_from_opt

        compare_chained1b_false_37 ::= chained_parts
                                       compare_chained2b_false_37
                                       POP_TOP jump _come_froms

        c_compare_chained1b_false_37 ::= chained_parts
                                         c_compare_chained2b_false_37 POP_TOP jump _come_froms
        c_compare_chained1b_false_37 ::= chained_parts
                                         compare_chained2b_false_37 POP_TOP jump _come_froms

        compare_chained1c_37       ::= chained_parts
                                       compare_chained2a_37 POP_TOP

        compare_chained1_false_37  ::= chained_parts
                                       compare_chained2c_37 POP_TOP JUMP_FORWARD come_from_opt
        compare_chained1_false_37  ::= chained_parts
                                       compare_chained2b_false_37 POP_TOP jump COME_FROM

        compare_chained2_false_37  ::= chained_parts
                                      compare_chained2a_false_37 POP_TOP JUMP_BACK COME_FROM
        c_compare_chained2_false_37  ::= chained_parts
                                         c_compare_chained2a_false_37 POP_TOP JUMP_BACK COME_FROM

        compare_chained2a_37       ::= expr COMPARE_OP come_from_opt POP_JUMP_IF_TRUE JUMP_FORWARD
        c_compare_chained2a_37     ::= expr COMPARE_OP come_from_opt POP_JUMP_IF_TRUE_BACK JUMP_FORWARD


        compare_chained2a_37       ::= expr COMPARE_OP come_from_opt POP_JUMP_IF_TRUE JUMP_BACK
        compare_chained2a_false_37 ::= expr COMPARE_OP come_from_opt POP_JUMP_IF_FALSE jf_cfs


        compare_chained2b_false_37   ::= expr COMPARE_OP come_from_opt POP_JUMP_IF_FALSE
                                         jump_or_break COME_FROM
        c_compare_chained2b_false_37 ::= expr COMPARE_OP come_from_opt POP_JUMP_IF_FALSE_BACK
                                         jump_or_break COME_FROM
        c_compare_chained2a_false_37 ::= expr COMPARE_OP come_from_opt POP_JUMP_IF_FALSE_BACK
                                         jf_cfs
        c_compare_chained2a_false_37 ::= expr COMPARE_OP come_from_opt POP_JUMP_IF_FALSE_BACK
        c_compare_chained2b_false_37 ::= expr COMPARE_OP come_from_opt JUMP_FORWARD COME_FROM


        compare_chained2c_37       ::= chained_parts compare_chained2a_false_37
        """

    def p_expr(self, args):
        """
        expr ::= LOAD_CODE
        expr ::= LOAD_CONST
        expr ::= LOAD_DEREF
        expr ::= LOAD_FAST
        expr ::= LOAD_GLOBAL
        expr ::= LOAD_NAME
        expr ::= LOAD_STR
        expr ::= and
        expr ::= bin_op
        expr ::= call
        expr ::= compare
        expr ::= subscript
        expr ::= subscript2
        expr ::= unary_not
        expr ::= unary_op
        expr ::= not
        expr ::= yield
        expr ::= attribute37
        expr ::= bool_op_compound

        # One thing that distinguishes Boolean expressions from other kinds of expressions is that
        # they have basic block and dominator pseudo instructions.
        expr    ::= bool_op
        bool_op ::= or bb_doms_end_opt
        bool_op ::= and bb_doms_end_opt
        bool_op ::= and_or bb_doms_end
        bool_op ::= or_and bb_doms_end

        # A "bool_op_compound" is a boolean with a nonbranching unary or binary operator at the end.
        # For example, in: "not a and b", the "not" is at the end after "a and b" and is non-branching.
        # But it appears at the beginning in source code.
        # In contrast, in  "(a and b) + 1": the plus is at the end and it is non-branching. And
        # it appears at the the end in source code

        bool_op_compound ::= bool_op_compound_prefix
        bool_op_compound ::= bool_op_compound_suffix

        bool_op_compound_prefix ::= bool_op DOM_START BB_START unary_operator
        bool_op_compound_suffix ::= bool_op DOM_START BB_START expr binary_operator


        # Python 3.3+ adds yield from.
        expr          ::= yield_from
        yield_from    ::= expr GET_YIELD_FROM_ITER LOAD_CONST YIELD_FROM

        attribute37       ::= expr LOAD_METHOD

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

        # unary_op (formerly "unary_expr") is the Python AST UnaryOp
        unary_op          ::= expr unary_operator

        unary_operator    ::= UNARY_POSITIVE
        unary_operator    ::= UNARY_NEGATIVE
        unary_operator    ::= UNARY_INVERT
        unary_operator    ::= UNARY_NOT

        unary_not         ::= expr UNARY_NOT

        subscript         ::= expr expr BINARY_SUBSCR
        subscript2        ::= expr expr DUP_TOP_TWO BINARY_SUBSCR

        yield             ::= expr YIELD_VALUE

        expr              ::= if_exp

        compare           ::= compare_chained
        compare           ::= compare_single
        compare_single    ::= expr expr COMPARE_OP
        c_compare         ::= c_compare_chained


        # FIXME: the below is to work around test_grammar expecting a "call" to be
        # on the LHS because it is also somewhere on in a rule.
        call           ::= expr CALL_METHOD_0
        """

    def p_list_comprehension(self, args):
        """
        expr ::= list_comp

        list_iter ::= list_for
        list_iter ::= list_if
        list_iter ::= list_if_not
        list_iter ::= list_if_or_not
        list_iter ::= lc_body

        lc_body   ::= expr LIST_APPEND
        list_for  ::= expr for_iter store list_iter jb_or_c _come_froms
        list_comp ::= BUILD_LIST_0 list_iter

        list_if_not_end ::= pjump_ift _come_froms
        list_if_not ::= expr list_if_not_end list_iter come_from_opt

        list_if     ::= expr pjump_iff list_iter come_from_opt
        list_if     ::= expr jump_if_false_cf   list_iter
        list_if_or_not ::= expr_pjit expr_pjit COME_FROM list_iter

        list_if_end ::= pjump_iff _come_froms
        list_if     ::= expr list_if_end list_iter come_from_opt

        jb_or_c ::= JUMP_BACK
        jb_or_c ::= CONTINUE


        """

    def p_conditionals(self, args):
        """
        expr                       ::= if_exp37
        bool_op                    ::= and_cond
        bool_op                    ::= and_not_cond
        bool_op                    ::= and POP_JUMP_IF_TRUE expr

        expr_pjif                  ::= expr POP_JUMP_IF_FALSE BB_END
        expr_pjit                  ::= expr POP_JUMP_IF_TRUE BB_END
        expr_jifop                 ::= expr JUMP_IF_FALSE_OR_POP BB_END
        expr_jitop                 ::= expr JUMP_IF_TRUE_OR_POP BB_END
        expr_pjiff                 ::= expr pjump_iff
        expr_pjift                 ::= expr pjump_ift

        if_exp                     ::= expr_pjif expr jump_forward_else expr come_froms

        if_exp37                   ::= expr expr    jf_cfs expr COME_FROM
        if_exp37                   ::= bool_op expr jf_cfs expr COME_FROM
        jf_cfs                     ::= JUMP_FORWARD _come_froms
        list_iter                  ::= list_if37
        list_iter                  ::= list_if37_not
        list_if37                  ::= c_compare_chained37_false list_iter
        list_if37_not              ::= compare_chained37 list_iter

        # A reduction check distinguishes between "and" and "and_not"
        # based on whether the POP_IF_JUMP location matches the location of the
        # POP_JUMP_IF_FALSE.

        and_not                    ::= expr_pjif expr_pjit
        or_and_not                 ::= expr_pjit and_not COME_FROM

        not_and_not                ::= not expr_pjif COME_FROM

        expr                       ::= if_exp_37a
        expr                       ::= if_exp_37b
        if_exp_37a                 ::= and_not expr JUMP_FORWARD come_froms expr COME_FROM
        if_exp_37b                 ::= expr_pjif expr_pjif jump_forward_else expr
        """

    def p_comprehension3(self, args):
        """
        # Python3 scanner adds LOAD_LISTCOMP. Python3 does list comprehension like
        # other comprehensions (set, dictionary).

        # Our "continue" heuristic -  in two successive JUMP_BACKS, the first
        # one may be a continue - sometimes classifies a JUMP_BACK
        # as a CONTINUE. The two are kind of the same in a comprehension.

        comp_for       ::= expr get_for_iter store comp_iter CONTINUE _come_froms
        comp_for       ::= expr get_for_iter store comp_iter JUMP_BACK _come_froms
        get_for_iter   ::= GET_ITER _come_froms FOR_ITER

        comp_body      ::= dict_comp_body
        comp_body      ::= set_comp_body
        dict_comp_body ::= expr expr MAP_ADD
        set_comp_body  ::= expr SET_ADD

        # See also common Python p_list_comprehension
        """

    def p_dict_comp3(self, args):
        """"
        or_jump_if_false_cf    ::= or POP_JUMP_IF_FALSE COME_FROM
        c_or_jump_if_false_cf  ::= c_or POP_JUMP_IF_FALSE_BACK COME_FROM

        c_or       ::= or
        c_or       ::= c_or_parts expr
        c_or_parts ::= expr_pjift+

        # Semantic rules require "comp_if" to have index 0 be some
        # sort of "expr" and index 1 to be some sort of "comp_iter"
        c_compare     ::= compare

        comp_if       ::= expr_pjif comp_iter
        comp_if       ::= expr_pjiff comp_iter
        comp_if       ::= c_compare comp_iter
        comp_if       ::= or_jump_if_false_cf comp_iter
        comp_if       ::= c_or_jump_if_false_cf comp_iter
        comp_if_not   ::= expr pjump_ift comp_iter

        comp_iter     ::= comp_body
        comp_iter     ::= comp_if
        comp_iter     ::= comp_if_not
        """

    def p_expr3(self, args):
        """
        expr               ::= if_exp_not
        if_exp_not         ::= expr POP_JUMP_IF_TRUE expr jump_forward_else expr COME_FROM

        # a JUMP_FORWARD to another JUMP_FORWARD can get turned into
        # a JUMP_ABSOLUTE with no COME_FROM
        if_exp             ::= expr_pjif expr jump_forward_else expr

        # if_exp_true are are IfExp which always evaluate true, e.g.:
        #      x = a if 1 else b
        # There is dead or non-optional remnants of the condition code though,
        # and we use that to match on to reconstruct the source more accurately
        expr           ::= if_exp_true
        if_exp_true    ::= expr JUMP_FORWARD expr COME_FROM

        """

    def p_set_comp(self, args):
        """
        comp_iter     ::= comp_for
        comp_body     ::= gen_comp_body
        gen_comp_body ::= expr YIELD_VALUE POP_TOP
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
        ## Will need to redo semantic actiion

        store           ::= STORE_FAST
        store           ::= STORE_NAME
        store           ::= STORE_GLOBAL
        store           ::= STORE_DEREF
        store           ::= expr STORE_ATTR
        store           ::= store_subscript
        store_subscript ::= expr expr STORE_SUBSCR
        """

    def __init__(self, start_symbol: str, debug_parser: dict = PARSER_DEFAULT_DEBUG):
        PythonParserLambda.__init__(
            self, SyntaxTree, debug_parser=debug_parser, start_symbol=start_symbol
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
    p = Python310LambdaParser(start_symbol="return_lambda")
    modified_tokens = set(
        """JUMP_BACK CONTINUE RETURN_END_IF BB_END BB_START DOM_END DOM_START

LOAD_GENEXPR LOAD_ASSERT LOAD_SETCOMP LOAD_DICTCOMP LOAD_CLASSNAME
           RETURN_LAST
        """.split()
        )

    dump_and_check(p, (3, 10), modified_tokens)
