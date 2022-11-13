#  Copyright (c) 2017-2022 Rocky Bernstein
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
"""spark grammar for the full Python 3.10 language and comple-mode variants.

This contains grammar rules but not rules for the start symbol or a
start symbol name. That is elsewhere.

By leaving out the start symbol rules and name, this module and its
classes be can used as a superclass in other grammars, although
Python38Parser is probably pretty much top-level.

Methods that start p_ have docstrings that are rule names.
Here we add a suffix _38full ito ensure there are no method name
conflicts with classes are smooshed together.
"""

from spark_parser import DEFAULT_DEBUG as PARSER_DEFAULT_DEBUG
from decompile_cfg.parsers.p38.lambda_expr import Python38LambdaParser
from decompile_cfg.parsers.p38.full_custom import Python38FullCustom


class Python38ParserFull(Python38LambdaParser, Python38FullCustom):
    def __init__(
        self,
        start_symbol: str="stmts",
        debug_parser:dict=PARSER_DEFAULT_DEBUG
    ):
        Python38LambdaParser.__init__(self, start_symbol, debug_parser)
        self.customized = {}

    def customize_grammar_rules(self, tokens, customize):
        self.customize_grammar_rules_full38(tokens, customize)

    ###############################################
    #  Python 3.8 grammar rules with statements
    ###############################################
    def p_stmt_loop38full(self, args):
        """
        #########################################################
        # Higher-level rules for statements in some sort of loop.
        #
        # Loops allow "continue" and "break" at the Python level.
        # At the bytecode level, there are backward jumps.
        #
        # Productions that can appear outside of
        # loop should be derivable from inside a loop, but
        # not necessarily vice versa, such as for "BREAK"
        # and "CONTINUE" (pseudo or real) instructions.
        #
        # Nonterminal names that start "c_" or end in "c", indicates
        # rule that can only to appear in a loop.
        # (The "c" stands for "continue". It is
        # a little bit historical. "l" was considered but can
        # be confused with "last".)
        #
        #########################################################
        c_stmts ::= _stmts
        c_stmts ::= _stmts lastc_stmt
        c_stmts ::= lastc_stmt
        c_stmts ::= continues
        c_stmts ::= c_stmt+
        c_stmts ::= c_returns

        # Additional statements that *must* be in a loop
        c_stmt  ::= break
        c_stmt  ::= continue

        c_stmt  ::= c_tryfinallystmt

        c_stmt  ::= c_try_except
        c_stmt  ::= c_try_except38
        c_stmt  ::= stmt

        else_suitec ::= c_stmts
        else_suitec ::= c_returns
        else_suitec ::= suite_stmts

        c_suite_stmts     ::= c_stmts
        c_suite_stmts     ::= suite_stmts
        c_suite_stmts_opt ::= c_suite_stmts
        c_suite_stmts_opt ::= suite_stmts_opt

        c_returns         ::= c_stmts return
        c_returns         ::= returns

        c_except  ::=  POP_TOP POP_TOP POP_TOP stmts_opt POP_EXCEPT jump
        c_except  ::=  POP_TOP POP_TOP POP_TOP c_returns

        # FIXME regularize name c_last_stmt, etc.
        # Do we really need these?
        lastc_stmt ::= forelselaststmtc
        lastc_stmt ::= iflaststmtc
        """

    def p_stmt_38full(self, args):
        """
        pass ::=

        stmts_opt ::= stmts
        stmts_opt ::= pass

        stmts  ::= stmt+
        stmts  ::= stmts last_stmt
        _stmts ::= stmts

        suite_stmts ::= _stmts
        suite_stmts ::= returns

        suite_stmts_opt ::= suite_stmts

        # passtmt is needed for semantic actions to add "pass"
        suite_stmts_opt ::= pass

        else_suite_opt ::= else_suite
        else_suite_opt ::= pass

        else_suite ::= suite_stmts
        else_suite ::= returns


        expr_stmt ::= expr POP_TOP
        expr_stmt ::= branch_op dom_start POP_TOP
        call_stmt ::= call

        stmt ::= break
        stmt ::= call_stmt
        stmt ::= classdef
        stmt ::= dict_comp_func
        stmt ::= expr_stmt

        stmt ::= for
        stmt ::= for38
        stmt ::= for38
        stmt ::= forelselaststmt38
        stmt ::= forelselaststmtc38
        stmt ::= forelsestmt
        stmt ::= forelsestmt38

        stmt ::= generator_exp

        stmt ::= if_and_elsestmt
        stmt ::= if_and_stmt
        stmt ::= if_or_not_elsestmt
        stmt ::= if_or_stmt
        stmt ::= ifelsestmt
        stmt ::= ifstmt
        stmt ::= ifstmt_branch

        stmt ::= last_stmt

        stmt ::= set_comp_func
                 RETURN_VALUE
                 bb_doms_end

        stmt ::= try_elsestmtl38
        stmt ::= try_except
        stmt ::= try_except38
        stmt ::= try_except38r
        stmt ::= try_except38r2
        stmt ::= try_except38r3
        stmt ::= try_except38r4
        stmt ::= try_except_as
        stmt ::= try_except_ret38
        stmt ::= try_except_ret38a
        stmt ::= tryelsestmt
        stmt ::= tryfinally_return_stmt1
        stmt ::= tryfinally_return_stmt2
        stmt ::= tryfinally38
        stmt ::= tryfinally38astmt
        stmt ::= tryfinally38rstmt
        stmt ::= tryfinally38rstmt2
        stmt ::= tryfinally38rstmt3
        stmt ::= tryfinally38rstmt4
        stmt ::= tryfinally38stmt
        stmt ::= tryfinallystmt

        stmt ::= while1elsestmt
        stmt ::= while1stmt
        stmt ::= whileTruestmt38
        stmt ::= whileelsestmt
        stmt ::= whilestmt
        stmt ::= whilestmt38

        # last_stmt is a Python statement for which
        # end is a "return" or raise statement and
        # thefore may not have a COME_FROM after
        # it. It does *not* have to be the last stmt of
        # a list of stmts or c_stmts
        last_stmt  ::= forelselaststmt
        # last_stmt  ::= iflaststmt

        stmt   ::= delete
        delete ::= DELETE_FAST
        delete ::= DELETE_NAME
        delete ::= DELETE_GLOBAL

        stmt   ::= return

        return ::= return_expr RETURN_VALUE bb_doms_end_opt

        # "returns" nonterminal is a sequence of statements that ends in a RETURN statement.
        # In later Python versions with jump optimization, this can cause JUMPs
        # that would normally appear to be omitted.

        returns ::= return
        returns ::= _stmts return

        """
        pass

    # # A "condition", in contrast to an "expr"ession ,is something that is is used in
    # # tests and pops the condition after testing
    # def p_if_conditions(self, args):
    #     """
    #     condition ::= and_or_cond
    #     condition ::= nor_cond
    #     condition ::= or_cond
    #     stmt ::= if_cond_stmt
    #     if_cond_stmt ::= condition stmt
    #     if_cond_else_stmt ::= condition
    #     """

    def p_function_def_38full(self, args):
        """
        stmt               ::= function_def
        function_def       ::= mkfunc store
        stmt               ::= function_def_deco
        function_def_deco  ::= mkfuncdeco store
        mkfuncdeco         ::= expr mkfuncdeco CALL_FUNCTION_1
        mkfuncdeco         ::= expr mkfuncdeco0 CALL_FUNCTION_1
        mkfuncdeco0        ::= mkfunc
        load_closure       ::= load_closure LOAD_CLOSURE
        load_closure       ::= LOAD_CLOSURE
        """

    def p_augmented_assign_38full(self, args):
        """
        stmt ::= aug_assign1
        stmt ::= aug_assign2

        # This is odd in that other aug_assign1's have only 3 slots
        # The store isn't used as that's supposed to be also
        # indicated in the first expr
        aug_assign1 ::= expr expr
                        inplace_op store
        aug_assign1 ::= expr expr
                        inplace_op ROT_THREE STORE_SUBSCR
        aug_assign2 ::= expr DUP_TOP LOAD_ATTR expr
                        inplace_op ROT_TWO STORE_ATTR

        inplace_op ::= INPLACE_ADD
        inplace_op ::= INPLACE_SUBTRACT
        inplace_op ::= INPLACE_MULTIPLY
        inplace_op ::= INPLACE_TRUE_DIVIDE
        inplace_op ::= INPLACE_FLOOR_DIVIDE
        inplace_op ::= INPLACE_MODULO
        inplace_op ::= INPLACE_POWER
        inplace_op ::= INPLACE_LSHIFT
        inplace_op ::= INPLACE_RSHIFT
        inplace_op ::= INPLACE_AND
        inplace_op ::= INPLACE_XOR
        inplace_op ::= INPLACE_OR
        """

    def p_assign_38full(self, args):
        """
        assign ::= expr DUP_TOP designList
        assign ::= expr store
        assign ::= branch_op dom_start store
        assign ::= expr bb_end_start store

        assign2 ::= expr expr ROT_TWO store store
        assign3 ::= expr expr expr ROT_THREE ROT_TWO store store store

        # Note. The below is right-recursive:
        designList ::= store store
        designList ::= store DUP_TOP designList

        ## Can we replace with left-recursive, and redo with:
        ##
        ##   designList  ::= designLists store store
        ##   designLists ::= designLists store DUP_TOP
        ##   designLists ::=
        ## Will need to redo semantic actions

        store           ::= expr STORE_ATTR
        store           ::= store_subscript

        stmt ::= assign
        stmt ::= assign2
        stmt ::= assign3
        """

    def p_await_38full(self, args):
        # Python 3.5+ Await things
        """
        stmt       ::= await_stmt
        await_stmt ::= await_expr POP_TOP
        """

    def p_ifstmt_38full(self, args):
        """
        # If statement inside a loop. The RHS may have looping jumps in them.
        c_stmt  ::= ifstmtc
        c_stmt  ::= if_and_elsestmtc

        if_or_stmt  ::= expr POP_JUMP_IF_TRUE expr pop_jump come_froms
                        stmts COME_FROM
        if_and_stmt ::= expr_pjif expr COME_FROM
                        stmts _come_froms

        if_or_not_elsestmt  ::= expr POP_JUMP_IF_TRUE
                                come_from_opt expr POP_JUMP_IF_TRUE come_froms
                                stmts jf_cfs else_suite opt_come_from_except


        # For "iflaststmt" there is a rule check for the below that the end of
        # "stmts" doesn't fall through.
        iflaststmt  ::= testexpr stmts
        iflaststmt  ::= testexpr returns
        iflaststmt  ::= testexpr stmts JUMP_FORWARD

        iflaststmtc ::= testexpr c_stmts
        iflaststmtc ::= testexpr c_stmts JUMP_LOOP
        iflaststmtc ::= testexpr c_stmts JUMP_LOOP COME_FROM_LOOP
        iflaststmtc ::= testexpr c_stmts JUMP_LOOP POP_BLOCK

        # c_stmts might terminate, or have "continue" so no JUMP_LOOP.
        # But if that's true, the "testexpr" needs still to jump to the "COME_FROM'
        iflaststmtc ::= testexpr c_stmts come_froms

        # Note: in if/else kinds of statements, we err on the side
        # of missing "else" clauses. Therefore we include grammar
        # rules with and without ELSE.

        if_and_elsestmt ::= testfalse testfalse
                            stmts_opt jf_bb_end_start else_suite block_end
        ifelsestmt      ::= testexpr
                            stmts_opt jf_bb_end_start else_suite block_end
        ifelsestmt      ::= branch_op
                            stmts_opt jf_bb_end_start else_suite block_end

        ifelsestmtc ::= testexpr
                        stmts_opt jump_forward_else
                        else_suitec opt_come_from_except
        ifelsestmtc ::= testexpr
                        stmts_opt cf_jump_back
                        else_suitec

        # This handles the case where a "JUMP_ABSOLUTE" is part
        # of an inner if in stmts_opt
        ifelsestmtc ::= testexpr c_stmts come_froms
                        else_suite

        ifelsestmtr ::= testexpr return_if_stmts returns

        # These rules need reduce checks on dominator information.
        # In particular, testexpr has to jump to to the end
        # of "ifstmt".
        ifstmt        ::= testexpr ifstmts_jump

        ifstmt_branch ::= or_and_not stmts block_end
        ifstmt_branch ::= or_and1 stmts block_end
        ifstmt_branch ::= not_and_not stmts block_end

        ifstmts_jump ::= return_if_stmts
        ifstmts_jump ::= stmts_opt block_end
        ifstmts_jump ::= block_end stmts block_end

        # Python 3.4+ optimizes the trailing two JUMPS away
        ifstmts_jump ::= stmts_opt JUMP_FORWARD JUMP_FORWARD _come_froms
        """

    def p_for_loop_38full(self, args):
        """
        setup_loop  ::= SETUP_LOOP _come_froms
        for         ::= setup_loop expr get_for_iter store for_block
                        POP_BLOCK
        for         ::= setup_loop expr get_for_iter store for_block
                        POP_BLOCK COME_FROM_LOOP

        # FIXME: investigate - can code really produce a NOP?
        for         ::= setup_loop expr get_for_iter store for_block POP_BLOCK NOP
                        COME_FROM_LOOP


        come_from_loops ::= COME_FROM_LOOP*

        for_block   ::= block_end stmts_opt come_from_loops JUMP_LOOP
        for_block   ::= stmts

        for_block   ::= stmts_opt COME_FROM_LOOP JUMP_BACK
        for_block   ::= stmts_opt _come_froms JUMP_BACK
        for_block   ::= stmts_opt come_from_loops JUMP_BACK
        for_block   ::= c_stmts
        for_block   ::= c_stmts JUMP_BACK

        forelsestmt ::= SETUP_LOOP expr get_for_iter store
                        for_block POP_BLOCK else_suite _come_froms

        forelsestmt ::= setup_loop expr get_for_iter store for_block POP_BLOCK else_suitec
        forelsestmt ::= setup_loop expr get_for_iter store for_block POP_BLOCK else_suite
                        COME_FROM_LOOP


        forelselaststmt ::= SETUP_LOOP expr get_for_iter store
                for_block POP_BLOCK else_suitec _come_froms

        forelselaststmt  ::= setup_loop expr get_for_iter store for_block POP_BLOCK else_suitec
                              COME_FROM_LOOP

        forelselaststmtc ::= SETUP_LOOP expr get_for_iter store
                for_block POP_BLOCK else_suitec _come_froms
        """


    def p_stmt_jump_38full(self, args):
        """
        jf_bb_end_start    ::= JUMP_FORWARD bb_end_start
        """

    def p_try_except_38full(self, args):
        """
        # Note: there is a suite_stmts_opt which seems
        # to be bookkeeping which is not expressed in source code
        except             ::= POP_TOP POP_TOP POP_TOP c_stmts_opt break POP_EXCEPT JUMP_LOOP


        # In 3.6+, A sequence of statements ending in a RETURN can cause
        # JUMP_FORWARD END_FINALLY to be omitted from try middle

        except_handler     ::= JUMP_FORWARD COME_FROM_EXCEPT except_return
        except_handler     ::= jmp_abs COME_FROM_EXCEPT except_stmts

        except_handler38   ::= COME_FROM_EXCEPT except_stmts
        except_handler38   ::= JUMP_FORWARD COME_FROM_EXCEPT except_stmts


        # Try middle following a returns
        except_handler38   ::= COME_FROM_EXCEPT except_stmts END_FINALLY

        except_handler38   ::= jump COME_FROM_FINALLY
                               except_stmts END_FINALLY opt_come_from_except
        except_handler38a  ::= COME_FROM_FINALLY POP_TOP POP_TOP POP_TOP
                               POP_EXCEPT POP_TOP stmts END_FINALLY
        except_handler38b  ::= COME_FROM_FINALLY POP_TOP POP_TOP POP_TOP
                               POP_EXCEPT returns END_FINALLY
        except_handler38c  ::= COME_FROM_FINALLY except_cond1a except_stmts
                               COME_FROM
        except_handler38c  ::= COME_FROM_FINALLY except_cond1a except_stmts
                               POP_EXCEPT JUMP_FORWARD COME_FROM

        except_handler_as  ::= COME_FROM_FINALLY except_cond_as tryfinallystmt
                               POP_EXCEPT JUMP_FORWARD COME_FROM

        except_suite_finalize ::= SETUP_FINALLY returns
                                  COME_FROM_FINALLY suite_stmts_opt END_FINALLY jump

        except_ret38       ::= SETUP_FINALLY expr ROT_FOUR POP_BLOCK POP_EXCEPT
                               CALL_FINALLY RETURN_VALUE COME_FROM
                               COME_FROM_FINALLY
                               suite_stmts_opt END_FINALLY
        except_ret38a      ::= COME_FROM_FINALLY POP_TOP POP_TOP POP_TOP
                               expr ROT_FOUR
                               POP_EXCEPT RETURN_VALUE END_FINALLY

        except_return    ::= POP_TOP POP_TOP POP_TOP returns

        try_except         ::= SETUP_FINALLY suite_stmts_opt POP_BLOCK
                               except_handler38
        try_except         ::= SETUP_FINALLY suite_stmts_opt POP_BLOCK
                               except_handler38
                               jump_excepts
                               come_from_except_clauses
        try_except38       ::= SETUP_FINALLY POP_BLOCK POP_TOP suite_stmts_opt
                               except_handler38a
        # suite_stmts has a return
        try_except38       ::= SETUP_FINALLY POP_BLOCK suite_stmts
                               except_handler38b
        try_except38r      ::= SETUP_FINALLY return_except
                               except_handler38b
        return_except      ::= stmts POP_BLOCK return


        # In 3.8 there seems to be some sort of code fiddle with POP_EXCEPT when there
        # is a final return in the "except" block.
        # So we treat the "return" separate from the other statements
        cond_except_stmt      ::= except_cond1 except_stmts
        cond_except_stmts_opt ::= cond_except_stmt*

        try_except38r2     ::= SETUP_FINALLY
                               suite_stmts_opt
                               POP_BLOCK JUMP_FORWARD
                               COME_FROM_FINALLY POP_TOP POP_TOP POP_TOP
                               cond_except_stmts_opt
                               POP_EXCEPT return
                               END_FINALLY
                               COME_FROM

        try_except38r3     ::= SETUP_FINALLY
                               suite_stmts_opt
                               POP_BLOCK JUMP_FORWARD
                               COME_FROM_FINALLY
                               cond_except_stmts_opt
                               POP_EXCEPT return
                               COME_FROM
                               END_FINALLY
                               COME_FROM


        try_except38r4     ::= SETUP_FINALLY
                               returns_in_except
                               COME_FROM_FINALLY
                               except_cond1
                               return
                               COME_FROM
                               END_FINALLY


        try_except_as      ::= SETUP_FINALLY POP_BLOCK suite_stmts
                               except_handler_as END_FINALLY COME_FROM
        try_except_as      ::= SETUP_FINALLY suite_stmts
                               except_handler_as END_FINALLY COME_FROM


        try_except_ret38   ::= SETUP_FINALLY returns except_ret38a
        try_except_ret38a  ::= SETUP_FINALLY returns except_handler38c
                               END_FINALLY come_from_opt

        try_except38     ::= SETUP_EXCEPT returns except_handler38
                             opt_come_from_except
        try_except38     ::= SETUP_EXCEPT suite_stmts
        try_except38     ::= SETUP_EXCEPT suite_stmts_opt POP_BLOCK
                             except_handler38 come_from_opt

        tryfinally_return_stmt1 ::= SETUP_FINALLY suite_stmts_opt POP_BLOCK LOAD_CONST
                                    COME_FROM_FINALLY returns
        tryfinally_return_stmt2 ::= SETUP_FINALLY suite_stmts_opt POP_BLOCK LOAD_CONST
                                    COME_FROM_FINALLY

        tryfinally38     ::= SETUP_FINALLY returns
                             COME_FROM_FINALLY suite_stmts
        tryfinally38     ::= SETUP_FINALLY returns
                             COME_FROM_FINALLY suite_stmts_opt END_FINALLY
        """

    def p_whilestmt_38full(self, args):
        """
        while1elsestmt ::= setup_loop c_stmts JUMP_BACK POP_BLOCK else_suite COME_FROM_LOOP
        while1elsestmt ::= setup_loop c_stmts JUMP_BACK _come_froms POP_BLOCK else_suitec COME_FROM_LOOP
        while1elsestmt ::= setup_loop c_stmts JUMP_BACK else_suite COME_FROM_LOOP
        while1elsestmt ::= setup_loop c_stmts JUMP_BACK else_suitec

        # FIXME: Python 3.? starts adding branch optimization? Put this starting there.

        while1stmt ::= setup_loop c_stmts COME_FROM JUMP_BACK COME_FROM_LOOP
        while1stmt ::= setup_loop c_stmts COME_FROM JUMP_BACK POP_BLOCK COME_FROM_LOOP
        while1stmt ::= setup_loop c_stmts COME_FROM_LOOP
        while1stmt ::= setup_loop c_stmts COME_FROM_LOOP JUMP_BACK POP_BLOCK COME_FROM_LOOP
        while1stmt ::= setup_loop c_stmts POP_BLOCK COME_FROM_LOOP

        whileTruestmt ::= SETUP_LOOP stmts_opt JUMP_BACK COME_FROM_LOOP
        whileTruestmt ::= setup_loop stmts_opt JUMP_BACK POP_BLOCK _come_froms

        # FIXME the below masks a bug in not detecting COME_FROM_LOOP
        # grammar rules with COME_FROM -> COME_FROM_LOOP already exist
        whileelsestmt     ::= setup_loop testexpr stmts_opt
                              JUMP_BACK POP_BLOCK
                              else_suite COME_FROM

        whileelsestmt     ::= setup_loop testexpr stmts_opt
                              JUMP_BACK POP_BLOCK
                              else_suite COME_FROM_LOOP

        # There is no JUMP_BACK here because c_stmts contineus, returns, or breaks
        whileelsestmt     ::= setup_loop testexpr
                              c_stmts come_froms POP_BLOCK
                              else_suite COME_FROM_LOOP

        whilestmt ::= setup_loop testexprc stmts_opt COME_FROM JUMP_BACK POP_BLOCK COME_FROM_LOOP
        whilestmt ::= setup_loop testexprc stmts_opt JUMP_BACK POP_BLOCK COME_FROM_LOOP

        # We can be missing a COME_FROM_LOOP if the "while" statement is nested inside an if/else
        # so after the POP_BLOCK we have a JUMP_FORWARD which forms the "else" portion of the "if"
        # This is undoubtedly some sort of JUMP optimization going on.
        # We have a reduction check for this peculiar case.

        whilestmt ::= setup_loop testexpr stmts_opt JUMP_BACK come_froms POP_BLOCK

        whilestmt ::= setup_loop testexpr stmts_opt JUMP_BACK come_froms POP_BLOCK COME_FROM_LOOP
        whilestmt ::= setup_loop testexpr stmts_opt come_froms JUMP_BACK come_froms POP_BLOCK COME_FROM_LOOP
        whilestmt ::= setup_loop testexpr stmts_opt come_froms POP_BLOCK COME_FROM_LOOP
        whilestmt ::= setup_loop testexpr returns POP_BLOCK COME_FROM_LOOP
        whilestmt ::= setup_loop testexpr returns come_froms POP_BLOCK COME_FROM_LOOP
        """

    def p_import20(self, args):
        """
        stmt ::= import
        stmt ::= import_from
        stmt ::= import_from_star
        stmt ::= importmultiple

        importlist ::= importlist alias
        importlist ::= alias
        alias      ::= IMPORT_NAME store
        alias      ::= IMPORT_FROM store
        alias      ::= IMPORT_NAME attributes store

        import           ::= LOAD_CONST LOAD_CONST alias
        import_from_star ::= LOAD_CONST LOAD_CONST IMPORT_NAME IMPORT_STAR
        import_from_star ::= LOAD_CONST LOAD_CONST IMPORT_NAME_ATTR IMPORT_STAR
        import_from      ::= LOAD_CONST LOAD_CONST IMPORT_NAME importlist POP_TOP
        importmultiple   ::= LOAD_CONST LOAD_CONST alias imports_cont

        imports_cont ::= import_cont+
        import_cont  ::= LOAD_CONST LOAD_CONST alias

        attributes   ::= LOAD_ATTR+
        """

    def p_import_38full(self, args):
        """
        # The 3.8base scanner adds IMPORT_NAME_ATTR
        alias            ::= IMPORT_NAME_ATTR attributes store
        alias            ::= IMPORT_NAME_ATTR store

        alias37          ::= IMPORT_NAME store
        alias37          ::= IMPORT_FROM store

        import_as37      ::= LOAD_CONST LOAD_CONST importlist37 store POP_TOP
        import_from      ::= LOAD_CONST LOAD_CONST importlist POP_TOP
        import_from37    ::= LOAD_CONST LOAD_CONST IMPORT_NAME_ATTR importlist37 POP_TOP
        import_from_as37 ::= LOAD_CONST LOAD_CONST import_from_attr37 store POP_TOP

        # A single entry in a dotted import a.b.c.d
        import_one       ::= importlists ROT_TWO IMPORT_FROM
        import_one       ::= importlists ROT_TWO POP_TOP IMPORT_FROM

        # Semantic checks distinguish importattr37 from import_from_attr37
        # in the former the "from" slot in a prior LOAD_CONST is null.

        # Used in: import .. as ..
        importattr37      ::= IMPORT_NAME_ATTR IMPORT_FROM

        # Used in: from xx import .. as ..
        import_from_attr37 ::= IMPORT_NAME_ATTR IMPORT_FROM

        importlist37  ::= import_one
        importlist37  ::= importattr37
        importlist37  ::= alias37+

        importlists   ::= importlist37+

        stmt          ::= import_as37
        stmt          ::= import_from_as37
        stmt          ::= import_from37
        """

    def p_32on(self, args):
        """
        # Python 3.5+ has jump optimization to remove the redundant
        # jump_excepts. But in 3.3 we need them added

        except_handler ::= JUMP_FORWARD COME_FROM_EXCEPT except_stmts
                           END_FINALLY

        tryelsestmt    ::= SETUP_EXCEPT suite_stmts_opt POP_BLOCK
                           except_handler else_suite
                           jump_excepts come_from_except_clauses

        jump_excepts   ::= jump_except+

        kv3       ::= expr expr STORE_MAP
        """
        return

    def p_35on(self, args):
        """
        inplace_op       ::= INPLACE_MATRIX_MULTIPLY
        binary_operator  ::= BINARY_MATRIX_MULTIPLY

        jb_cf     ::= JUMP_BACK COME_FROM
        ifelsestmtc ::= testexpr stmts_opt JUMP_FORWARD else_suitec

        # We want to keep the positions of the "then" and
        # "else" statements in "ifelstmtl" similar to others of this ilk.
        testexpr_cf ::= testexpr come_froms

        # iflaststmt  ::= testexpr stmts_opt JUMP_FORWARD
        """

    def p_grammar_38full(self, args):
        """sstmt ::= stmt
        sstmt ::= ifelsestmtr
        sstmt ::= return RETURN_LAST

        return_if_stmts ::= return_if_stmt come_from_opt
        return_if_stmts ::= _stmts return_if_stmt _come_froms
        returns         ::= _stmts return_if_stmt


        break     ::= BREAK_LOOP
        continue  ::= CONTINUE
        continues ::= _stmts lastc_stmt continue
        continues ::= lastc_stmt continue
        continues ::= continue


        kwarg      ::= LOAD_STR expr
        kwargs     ::= kwarg+

        classdef ::= build_class store

        # FIXME: we need to add these because don't detect this properly
        # in custom rules. Specifically if one of the exprs is CALL_FUNCTION
        # then we'll mistake that for the final CALL_FUNCTION.
        # We can fix by triggering on the CALL_FUNCTION op
        # Python3 introduced LOAD_BUILD_CLASS
        # Other definitions are in a custom rule
        build_class ::= LOAD_BUILD_CLASS mkfunc expr call CALL_FUNCTION_3
        build_class ::= LOAD_BUILD_CLASS mkfunc expr call expr CALL_FUNCTION_4

        stmt ::= classdefdeco
        classdefdeco ::= classdefdeco1 store

        assert  ::= expr
                    POP_JUMP_IF_TRUE
                    LOAD_ASSERT
                    RAISE_VARARGS_1
                    bb_end_start

        assert2 ::= expr
                    POP_JUMP_IF_TRUE
                    LOAD_ASSERT
                    expr
                    CALL_FUNCTION_1
                    RAISE_VARARGS_1
                    bb_end_start

        # Some LOAD_GLOBALs we don't convert to LOAD_ASSERT because
        # of the intevening "expr CALL_FUNCTION1" which can be an arbitrary number
        # of instructions
        assert2_not ::= expr
                    POP_JUMP_IF_FALSE
                    LOAD_GLOBAL
                    expr
                    CALL_FUNCTION_1
                    RAISE_VARARGS_1
                    bb_end_start


        # "assert_invert" tests on the negative of the condition given
        stmt          ::= assert_invert
        assert_invert ::= testtrue LOAD_GLOBAL RAISE_VARARGS_1

        pop_jump    ::= POP_JUMP_IF_TRUE
        pop_jump    ::= POP_JUMP_IF_FALSE

        testexpr   ::= testfalse
        testexpr   ::= testtrue
        testexpr   ::= or_and_not

        testfalse  ::= expr_pjif
        testfalsec ::= expr POP_JUMP_IF_TRUE_LOOP
        testfalsec ::= c_compare_chained1b_false_38

        testtrue   ::= expr_pjit
        testtruec  ::= expr POP_JUMP_IF_FALSE_LOOP
        # Do we have to check the c_compare_chained38 ends in a POP_JUMP_IF_FALSE_BACK?
        testtruec  ::= c_compare_chained38_false
        testtruec  ::= c_compare_chained38
        testtruec  ::= c_nand

        testtrue   ::= compare_chained38
        testtrue   ::= compare_chained_and

        testtrue   ::= nor_cond

        testfalse  ::= and_not
        testfalse  ::= not_or
        testfalse  ::= compare_chained38_false
        testfalse  ::= or_cond
        testfalse  ::= or_cond1
        testfalse  ::= and_or_cond

        cf_jump_back ::= COME_FROM JUMP_LOOP

        # This is nested inside a try_except
        tryfinallystmt   ::= SETUP_FINALLY suite_stmts_opt
                             POP_BLOCK LOAD_CONST
                             COME_FROM_FINALLY suite_stmts_opt END_FINALLY

        c_tryfinallystmt ::= SETUP_FINALLY c_suite_stmts_opt
                             POP_BLOCK LOAD_CONST COME_FROM_FINALLY
                             c_suite_stmts_opt END_FINALLY

        # This a funny kind of try finally inside a try_except in a loop
        c_except_suite     ::= SETUP_FINALLY c_suite_stmts
                               POP_BLOCK LOAD_CONST
                               COME_FROM_FINALLY LOAD_CONST STORE_FAST DELETE_FAST
                               END_FINALLY
                               POP_EXCEPT JUMP_LOOP COME_FROM

        c_except_suite     ::= except_suite
        c_except_suite     ::= c_stmts POP_EXCEPT JUMP_LOOP
        c_except_handler38 ::= COME_FROM_EXCEPT c_except_stmts END_FINALLY
        c_try_except38     ::= SETUP_EXCEPT suite_stmts_opt POP_BLOCK
                               c_except_handler38 come_from_opt
        c_try_except38     ::= SETUP_EXCEPT returns
                               c_except_handler38 come_from_opt


        except_handler ::= jmp_abs COME_FROM except_stmts
                           _come_froms END_FINALLY
        except_handler ::= jmp_abs COME_FROM_EXCEPT except_stmts
                           _come_froms END_FINALLY

        c_except_handler ::= jmp_abs COME_FROM c_except_stmts
                           _come_froms END_FINALLY
        c_except_handler ::= jmp_abs COME_FROM_EXCEPT c_except_stmts
                           _come_froms END_FINALLY
        c_except_handler ::= jmp_abs COME_FROM_EXCEPT c_except_stmts

        try_except   ::= SETUP_EXCEPT suite_stmts_opt POP_BLOCK
                         except_handler
                         jump_excepts come_from_except_clauses

        c_try_except ::= SETUP_EXCEPT c_suite_stmts_opt POP_BLOCK
                         c_except_handler
                         jump_excepts come_from_except_clauses

        # FIXME: remove this
        except_handler ::= JUMP_FORWARD COME_FROM except_stmts
                           come_froms END_FINALLY come_from_opt

        except_stmts   ::= except_stmt+

        except_stmt    ::= except_cond1 except_suite come_from_opt
        except_stmt    ::= except_cond2 except_suite come_from_opt
        except_stmt    ::= except_cond2 except_suite_finalize
        except_stmt    ::= except
        except_stmt    ::= stmt

        c_except_stmts ::= except_stmts
        c_except_stmts ::= c_except_stmt+
        c_except_stmt  ::= c_stmt
        c_except_stmt  ::= c_except
        c_except_stmt  ::= except_cond1 c_except_suite come_from_opt
        c_except_stmt  ::= except_cond2 c_except_suite come_from_opt
        c_except_stmt  ::= stmt

        ## FIXME: what's except_pop_except?
        except_stmt    ::= except_pop_except

        # Python3 introduced POP_EXCEPT
        except_suite ::= stmts_opt POP_EXCEPT jump_except
        jump_except ::= JUMP_ABSOLUTE
        jump_except ::= JUMP_LOOP
        jump_except ::= JUMP_FORWARD
        jump_except ::= CONTINUE

        # This is used in Python 3 in
        # "except ... as e" to remove 'e' after the stmts_opt finishes
        except_suite_finalize ::= SETUP_FINALLY stmts_opt except_var_finalize
                                  END_FINALLY jump

        except_suite_finalize ::= SETUP_FINALLY stmts_opt except_var_finalize
                                  END_FINALLY POP_EXCEPT jump

        except_var_finalize ::= POP_BLOCK POP_EXCEPT LOAD_CONST COME_FROM_FINALLY
                                LOAD_CONST store delete
        except_var_finalize ::= POP_BLOCK            LOAD_CONST COME_FROM_FINALLY
                                LOAD_CONST store delete

        except_suite   ::= returns
        c_except_suite ::= c_returns

        except_cond1 ::= DUP_TOP expr COMPARE_OP
                         POP_JUMP_IF_FALSE POP_TOP POP_TOP POP_TOP

        except_cond2 ::= DUP_TOP expr COMPARE_OP
                         POP_JUMP_IF_FALSE POP_TOP store POP_TOP come_from_opt

        except  ::=  POP_TOP POP_TOP POP_TOP stmts_opt POP_EXCEPT JUMP_FORWARD
        except  ::=  POP_TOP POP_TOP POP_TOP returns

        jmp_abs ::= JUMP_ABSOLUTE
        jmp_abs ::= JUMP_LOOP
        jmp_abs ::= JUMP_FORWARD

        stmt    ::= assert
        stmt    ::= assert2
        stmt    ::= assert2_not
        """

    def p_except_38full(self, args):
        """
        except_handler ::= JUMP_FORWARD COME_FROM_EXCEPT except_stmts
                           come_froms END_FINALLY

        c_except_handler ::= jmp_abs COME_FROM c_except_stmts
                           _come_froms END_FINALLY
        c_except_handler ::= jmp_abs COME_FROM_EXCEPT c_except_stmts
                           _come_froms END_FINALLY
        c_except_handler ::= jmp_abs COME_FROM_EXCEPT c_except_stmts
        """

    def p_come_from_38full(self, args):
        """
        # In 3.7+ a SETUP_LOOP to a JUMP_FORWARD can
        # get replaced by the JUMP_FORWARD addressed. Therefore come froms may
        # appear out of nesting order. For example:
        #   if x
        #     for ... jump forward endif (1)
        #        ...
        #        break - jump forward endif (2)
        #     end for
        #     optional jump forward endif (1)
        #   else:
        #       ...
        #   endif
        #   come from loop 2 - note not strictly nested
        #   come from if-then 1

        come_any_froms ::= come_any_froms come_any_from
        come_any_froms ::= come_any_from
        come_any_from  ::= COME_FROM_LOOP
        come_any_from  ::= COME_FROM_EXCEPT
        come_any_from  ::= COME_FROM

        opt_come_from_except ::= come_any_froms?
        opt_come_from_loop   ::= COME_FROM_LOOP?

        come_from_except_clauses ::= COME_FROM_EXCEPT_CLAUSE*
        """

    def p_jump_38full(self, args):
        """
        # Do we need this?
        # Note: lambda_expr.py has jump_or_break ::= jump
        jump_or_break      ::= BREAK_LOOP

        return_expr ::= expr

        # FIXME: simplify this
        return_expr_or_cond ::= if_exp_ret
        return_expr_or_cond ::= return_expr

        testfalse ::= or POP_JUMP_IF_FALSE COME_FROM
        testfalse ::= nand
        testfalse ::= and

        testexprc   ::= testexpr
        testexprc   ::= testfalsec
        testexprc   ::= testtruec
        iflaststmtc ::= testexprc c_stmts
        iflaststmtc ::= testexprc c_stmts JUMP_LOOP COME_FROM_LOOP
        iflaststmtc ::= testexprc c_stmts JUMP_LOOP opt_pop_block

        opt_pop_block ::= POP_BLOCK?

        """

    def p_stmt_more_38full(self, args):
        """
        if_exp_lambda      ::= expr_pjif expr return_if_lambda
                               return_stmt_lambda
        if_exp_not_lambda
                           ::= expr POP_JUMP_IF_TRUE expr return_if_lambda
                               return_stmt_lambda
        return_stmt_lambda ::= return_expr RETURN_VALUE_LAMBDA

        stmt               ::= return_closure
        return_closure     ::= LOAD_CLOSURE RETURN_VALUE RETURN_LAST

        stmt               ::= whileTruestmt
        ifelsestmt         ::= testexpr stmts_opt JUMP_FORWARD else_suite block_end

        ifstmtc            ::= testexpr ifstmts_jumpc
        ifstmtc            ::= testexprc ifstmts_jumpc _come_froms

        ifstmts_jumpc             ::= ifstmts_jump
        ifstmts_jumpc             ::= stmts_opt come_froms
        ifstmts_jumpc             ::= COME_FROM c_stmts come_froms
        ifstmts_jumpc             ::= c_stmts
        ifstmts_jumpc             ::= c_stmts JUMP_LOOP

        ifstmts_jump              ::= stmts come_froms
        ifstmts_jump              ::= COME_FROM stmts come_froms


        # The following can happen when the jump offset is large and
        # Python is looking to do a small jump to a larger jump to get
        # around the problem that the offset can't be represented in
        # the size allowed for the jump offset. This is more likely to
        # happen in wordcode Python since the offset range has been
        # reduced.  FIXME: We should add a reduction check that the
        # final jump goes to another jump.

        ifstmts_jumpc     ::= COME_FROM c_stmts JUMP_LOOP
        ifstmts_jumpc     ::= COME_FROM c_stmts JUMP_FORWARD

        """

    def p_expr_full(self, args):
        """
        expr       ::= LOAD_ASSERT
        # named_expr is also known as the "walrus op" :=
        expr       ::= named_expr
        expr       ::= subscript2

        named_expr        ::= expr DUP_TOP store

        # Note: we don't have global storing in lambda's.
        store             ::= STORE_GLOBAL

        subscript2 ::= expr expr DUP_TOP_TWO BINARY_SUBSCR
        """

    def p_38if_ifelse(self, args):
        """
        # cf_pt introduced to keep indices the same in ifelsestmtc
        cf_pt              ::= COME_FROM POP_TOP

        # 3.8 can push a looping JUMP_LOOP into into a JUMP_ from a statement that jumps to it
        ifpoplaststmtc     ::= testexpr POP_TOP stmts_opt
        if_and_elsestmtc   ::= expr_pjif
                               expr_pjif
                               c_stmts jb_cfs else_suitec opt_come_from_except
        jb_cfs      ::= come_from_opt JUMP_LOOP come_froms
        lastc_stmt         ::= ifpoplaststmtc

        # The below ifelsetmtc is a really weird one for the inner if/else in:
        #  if a:
        #      while i:
        #       if c:
        #         j = j + 1
        #                 # A JUMP_LOOP is here...
        #       else:
        #          break
        #                 # but also a JUMP_LOOP is inserted here!
        #  else:
        #    j = 10
        """

    def p_for38full(self, args):
        """
        for38              ::= expr get_for_iter store for_block JUMP_LOOP block_end
        for38              ::= expr get_for_iter store for_block JUMP_LOOP block_end POP_BLOCK
        for38              ::= expr get_for_iter store for_block block_end

        forelsestmt38      ::= expr get_for_iter store for_block POP_BLOCK else_suite
        forelsestmt38      ::= expr get_for_iter store for_block JUMP_LOOP _come_froms else_suite
        """

    def p_misc38full(self, args):
        """
        sstmt ::= sstmt RETURN_LAST

        # 3.6 redoes how return_closure works. FIXME: Isolate to LOAD_CLOSURE
        return_closure   ::= LOAD_CLOSURE DUP_TOP STORE_NAME RETURN_VALUE RETURN_LAST

        except_suite ::= stmts_opt COME_FROM POP_EXCEPT jump_except COME_FROM

        compare_chained2 ::= expr COMPARE_OP block_end JUMP_FORWARD

        stmt               ::= async_for_stmt38
        stmt               ::= async_forelse_stmt38

        # break could be isolated to loops but many
        # rules would be for with and without loops.
        # There is a possibility we wil need a reduction rule
        # if this generalization causes problems, but I don't
        # think it will.
        # Oddly, these don't appear in code fragments
        # STORE_GLOBAL makes sense; not sure about STORE_NAME though.
        store              ::= STORE_GLOBAL

        call_stmt          ::= call POP_TOP

        break ::= POP_BLOCK BREAK_LOOP
        break ::= POP_BLOCK POP_TOP BREAK_LOOP
        break ::= POP_TOP BREAK_LOOP
        break ::= POP_EXCEPT BREAK_LOOP

        # FIXME: this should be restricted to being inside a try block
        stmt               ::= except_ret38
        stmt               ::= except_ret38a

        # Seems to be used to discard values before a return in a "for" loop
        discard_top        ::= ROT_TWO POP_TOP
        discard_tops       ::= discard_top+
        pop_tops           ::= POP_TOP+

        return             ::= return_expr
                               discard_tops RETURN_VALUE

        return             ::= pop_return
        return             ::= popb_return
        return             ::= pop_ex_return
        except_stmt        ::= pop_ex_return
        pop_return         ::= POP_TOP return_expr RETURN_VALUE
        popb_return        ::= return_expr POP_BLOCK RETURN_VALUE
        pop_ex_return      ::= return_expr ROT_FOUR POP_EXCEPT RETURN_VALUE

        except_stmt        ::= except_cond1a except_suite come_from_opt

        get_for_iter       ::= GET_ITER BREAK_FOR for_iter

        c_stmt             ::= c_forelsestmt38
        c_stmt             ::= pop_tops return
        c_forelsestmt38    ::= expr get_for_iter store for_block POP_BLOCK else_suitec
        c_forelsestmt38    ::= expr get_for_iter store for_block JUMP_LOOP _come_froms else_suitec

        forelselaststmt38  ::= expr get_for_iter store for_block POP_BLOCK else_suitec
        forelselaststmtc38 ::= expr get_for_iter store for_block POP_BLOCK else_suitec

        whilestmt38        ::= _come_froms testexpr stmts_opt COME_FROM JUMP_LOOP POP_BLOCK
        whilestmt38        ::= _come_froms testexpr stmts_opt JUMP_LOOP POP_BLOCK
        whilestmt38        ::= _come_froms testexpr stmts_opt JUMP_LOOP come_froms
        whilestmt38        ::= _come_froms testexpr returns               POP_BLOCK
        whilestmt38        ::= _come_froms testexpr c_stmts     JUMP_LOOP _come_froms
        whilestmt38        ::= _come_froms testexpr c_stmts     come_froms

        # while1elsestmt   ::=          c_stmts     JUMP_LOOP
        whileTruestmt      ::= _come_froms c_stmts              JUMP_LOOP _come_froms POP_BLOCK
        while1stmt         ::= _come_froms c_stmts COME_FROM_LOOP
        while1stmt         ::= _come_froms c_stmts COME_FROM JUMP_LOOP COME_FROM_LOOP
        whileTruestmt38    ::= _come_froms c_stmts JUMP_LOOP _come_froms
        whileTruestmt38    ::= _come_froms c_stmts JUMP_LOOP COME_FROM_EXCEPT_CLAUSE

        except_cond1       ::= DUP_TOP expr COMPARE_OP POP_JUMP_IF_FALSE
                               POP_TOP POP_TOP POP_TOP
                               POP_EXCEPT
        except_cond1a      ::= DUP_TOP expr COMPARE_OP POP_JUMP_IF_FALSE
                               POP_TOP POP_TOP POP_TOP

        # except .. as var
        except_cond_as     ::= DUP_TOP expr COMPARE_OP POP_JUMP_IF_FALSE
                               POP_TOP STORE_FAST POP_TOP

        try_elsestmtl38    ::= SETUP_FINALLY suite_stmts_opt POP_BLOCK
                               except_handler38 COME_FROM
                               else_suitec opt_come_from_except
        try_except         ::= SETUP_FINALLY suite_stmts_opt POP_BLOCK
                               except_handler38
        try_except         ::= SETUP_FINALLY suite_stmts_opt POP_BLOCK
                               except_handler38
                               jump_excepts
                               come_from_except_clauses

        c_try_except       ::= SETUP_FINALLY c_suite_stmts POP_BLOCK
                               except_handler38

        c_stmt             ::= c_tryfinallystmt38
        c_tryfinallystmt38 ::= SETUP_FINALLY c_suite_stmts_opt
                               POP_BLOCK
                               CALL_FINALLY
                               POP_BLOCK
                               POP_EXCEPT
                               CALL_FINALLY
                               JUMP_FORWARD
                               POP_BLOCK BEGIN_FINALLY
                               COME_FROM
                               COME_FROM_FINALLY
                               c_suite_stmts_opt END_FINALLY

        c_tryfinallystmt38 ::= SETUP_FINALLY c_suite_stmts_opt
                               POP_BLOCK BEGIN_FINALLY COME_FROM COME_FROM_FINALLY
                               c_suite_stmts_opt END_FINALLY

        try_except38       ::= SETUP_FINALLY POP_BLOCK POP_TOP suite_stmts_opt
                               except_handler38a

        # suite_stmts has a return
        try_except38       ::= SETUP_FINALLY POP_BLOCK suite_stmts
                               except_handler38b
        try_except38r      ::= SETUP_FINALLY return_except
                               except_handler38b
        return_except      ::= stmts POP_BLOCK return


        # In 3.8 any POP_EXCEPT comes before the "break" loop.
        # We should add a rule to check that JUMP_FORWARD is indeed a "break".
        break              ::=  POP_EXCEPT JUMP_FORWARD
        break              ::=  POP_BLOCK POP_TOP JUMP_FORWARD

        tryfinallystmt     ::= SETUP_FINALLY suite_stmts_opt POP_BLOCK
                               BEGIN_FINALLY COME_FROM_FINALLY suite_stmts_opt
                               END_FINALLY


        lc_setup_finally   ::= LOAD_CONST SETUP_FINALLY
        call_finally_pt    ::= CALL_FINALLY POP_TOP
        cf_cf_finally      ::= come_from_opt COME_FROM_FINALLY
        pop_finally_pt     ::= POP_FINALLY POP_TOP
        ss_end_finally     ::= suite_stmts END_FINALLY
        sf_pb_call_returns ::= SETUP_FINALLY POP_BLOCK CALL_FINALLY returns
        sf_pb_call_returns ::= SETUP_FINALLY POP_BLOCK POP_EXCEPT CALL_FINALLY returns
        suite_stmts_return ::= suite_stmts expr
        suite_stmts_return ::= expr


        # FIXME: DRY rules below
        tryfinally38rstmt  ::= sf_pb_call_returns
                               cf_cf_finally
                               ss_end_finally
        tryfinally38rstmt  ::= sf_pb_call_returns
                               cf_cf_finally END_FINALLY
                               suite_stmts
        tryfinally38rstmt  ::= sf_pb_call_returns
                               cf_cf_finally POP_FINALLY
                               ss_end_finally
        tryfinally38rstmt  ::= sf_pb_call_returns
                               COME_FROM_FINALLY POP_FINALLY
                               ss_end_finally

        tryfinally38rstmt2 ::= lc_setup_finally POP_BLOCK call_finally_pt
                               returns
                               cf_cf_finally pop_finally_pt
                               ss_end_finally POP_TOP

        tryfinally38rstmt3 ::= SETUP_FINALLY expr POP_BLOCK CALL_FINALLY RETURN_VALUE
                               COME_FROM COME_FROM_FINALLY
                               ss_end_finally

        tryfinally38rstmt4 ::= lc_setup_finally suite_stmts_opt POP_BLOCK
                               BEGIN_FINALLY COME_FROM_FINALLY
                               suite_stmts_return
                               POP_FINALLY ROT_TWO POP_TOP
                               RETURN_VALUE
                               END_FINALLY POP_TOP


        tryfinally38stmt   ::= SETUP_FINALLY suite_stmts_opt POP_BLOCK
                               BEGIN_FINALLY COME_FROM_FINALLY
                               POP_FINALLY suite_stmts_opt END_FINALLY

        tryfinally38astmt  ::= LOAD_CONST SETUP_FINALLY suite_stmts_opt POP_BLOCK
                               BEGIN_FINALLY COME_FROM_FINALLY
                               POP_FINALLY POP_TOP suite_stmts_opt END_FINALLY POP_TOP
        """

def info(args):
    # Check grammar
    import sys

    p = Python38ParserFull()
    if len(args) > 0:
        arg = args[0][:2]
        if arg != (3, 8):
            raise RuntimeError("Only 3.8 supported")
    p.check_grammar()
    if len(sys.argv) > 1 and sys.argv[1] == "dump":
        print("-" * 50)
        p.dump_grammar()


if __name__ == "__main__":
    # Check grammar
    from decompile_cfg.parsers.dump import dump_and_check

    p = Python38ParserFull(start_symbol="stmts")
    modified_tokens = set(
        """JUMP_LOOP CONTINUE
           LOAD_GENEXPR LOAD_ASSERT LOAD_SETCOMP LOAD_DICTCOMP LOAD_CLASSNAME
           LAMBDA_MARKER RETURN_LAST
        """.split()
    )

    dump_and_check(p, (3, 8), modified_tokens, set(["stmts"]))
