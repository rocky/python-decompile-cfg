#  Copyright (c) 2021-2022 Rocky Bernstein
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

from decompile_cfg.parsers.parse_heads import PythonBaseParser, nop_func
from decompile_cfg.parsers.p38.lambda_custom import Python38LambdaCustom
from decompile_cfg.parsers.reduce_check.and_check import and_ok
from decompile_cfg.parsers.reduce_check.if_exp_check import if_exp_ok
from decompile_cfg.parsers.reduce_check.comp_if_check import comp_if_ok

class Python38FullCustom(Python38LambdaCustom, PythonBaseParser):
    def add_make_function_rule(self, rule, opname, attr, customize):
        """Python 3.3 added a an addtional LOAD_STR before MAKE_FUNCTION and
        this has an effect on many rules.
        """
        new_rule = rule % "LOAD_STR "
        self.add_unique_rule(new_rule, opname, attr, customize)

    @staticmethod
    def call_fn_name(token):
        """Customize CALL_FUNCTION to add the number of positional arguments"""
        if token.attr is not None:
            return f"{token.kind}_{token.attr}"
        else:
            return f"{token.kind}_0"

    def remove_rules_38(self):
        self.remove_rules(
            """
           stmt               ::= async_for_stmt37
           stmt               ::= for
           stmt               ::= forelsestmt
           stmt               ::= try_except36
           stmt               ::= async_forelse_stmt

           async_for_stmt     ::= setup_loop expr
                                  GET_AITER
                                  SETUP_EXCEPT GET_ANEXT LOAD_CONST
                                  YIELD_FROM
                                  store
                                  POP_BLOCK JUMP_FORWARD bb_end_start DUP_TOP
                                  LOAD_GLOBAL COMPARE_OP POP_JUMP_IF_TRUE
                                  END_FINALLY bb_end_start
                                  for_block
                                  COME_FROM
                                  POP_TOP POP_TOP POP_TOP POP_EXCEPT POP_TOP POP_BLOCK
                                  COME_FROM_LOOP
           async_for_stmt37   ::= setup_loop expr
                                  GET_AITER
                                  SETUP_EXCEPT GET_ANEXT
                                  LOAD_CONST YIELD_FROM
                                  store
                                  POP_BLOCK JUMP_LOOP COME_FROM_EXCEPT DUP_TOP
                                  LOAD_GLOBAL COMPARE_OP POP_JUMP_IF_TRUE
                                  END_FINALLY for_block COME_FROM
                                  POP_TOP POP_TOP POP_TOP POP_EXCEPT
                                  POP_TOP POP_BLOCK
                                  COME_FROM_LOOP

          async_forelse_stmt ::= setup_loop expr
                                 GET_AITER
                                 SETUP_EXCEPT GET_ANEXT LOAD_CONST
                                 YIELD_FROM
                                 store
                                 POP_BLOCK JUMP_FORWARD COME_FROM_EXCEPT DUP_TOP
                                 LOAD_GLOBAL COMPARE_OP POP_JUMP_IF_TRUE
                                 END_FINALLY COME_FROM
                                 for_block
                                 COME_FROM
                                 POP_TOP POP_TOP POP_TOP POP_EXCEPT POP_TOP POP_BLOCK
                                 else_suite COME_FROM_LOOP

           for                ::= setup_loop expr get_for_iter store for_block POP_BLOCK
           for                ::= setup_loop expr get_for_iter store for_block POP_BLOCK NOP

           for_block          ::= c_stmts_opt COME_FROM_LOOP JUMP_LOOP
           forelsestmt        ::= setup_loop expr get_for_iter store for_block POP_BLOCK else_suite
           forelselaststmt    ::= setup_loop expr get_for_iter store for_block POP_BLOCK else_suitec
           forelselaststmtc   ::= setup_loop expr get_for_iter store for_block POP_BLOCK else_suitec

           try_except         ::= SETUP_EXCEPT suite_stmts_opt POP_BLOCK
                                  except_handler opt_come_from_except

           tryfinallystmt     ::= SETUP_FINALLY suite_stmts_opt POP_BLOCK
                                  LOAD_CONST COME_FROM_FINALLY suite_stmts_opt
                                  END_FINALLY
           tryfinally36       ::= SETUP_FINALLY returns
                                  COME_FROM_FINALLY suite_stmts_opt END_FINALLY
           tryfinally_return_stmt ::= SETUP_FINALLY suite_stmts_opt POP_BLOCK
                                      LOAD_CONST COME_FROM_FINALLY
        """
        )

    def customize_grammar_rules_full38(self, tokens, customize):

        self.customize_grammar_rules_lambda38(tokens, customize)

        self.reduce_check_table = {
            "and1": and_ok,
            "if_exp": if_exp_ok,
            "comp_if": comp_if_ok,
            "comp_if_not": comp_if_ok,
        }

        self.check_reduce["and1"] = "AST"
        self.check_reduce["if_exp_ok"] = "AST"
        self.check_reduce["comp_if_not"] = "AST"
        self.check_reduce["comp_if"] = "AST"


        # For a rough break out on the first word. This may
        # include instructions that don't need customization,
        # but we'll do a finer check after the rough breakout.
        customize_instruction_basenames = frozenset(
            (
                "BEFORE",
                "BUILD",
                "CALL",
                "CONTINUE",
                "DELETE",
                "FORMAT",
                "GET",
                "JUMP",
                "LOAD",
                "LOOKUP",
                "MAKE",
                "RETURN",
                "RAISE",
                "SETUP",
                "UNPACK",
                "WITH",
            )
        )

        # Opcode names in the custom_ops_processed set have rules that get added
        # unconditionally and the rules are constant. So they need to be done
        # only once and if we see the opcode a second we don't have to consider
        # adding more rules.
        #
        custom_ops_processed = set()

        # A set of instruction operation names that exist in the token stream.
        # We use this customize the grammar that we create.
        # 2.6-compatible set comprehensions

        # The initial initialization is done in lambea_expr.py
        self.seen_ops = frozenset([t.kind for t in tokens])
        self.seen_op_basenames = frozenset(
            [opname[: opname.rfind("_")] for opname in self.seen_ops]
        )

        # Loop over instructions adding custom grammar rules based on
        # a specific instruction seen.

        is_pypy = False
        if "PyPy" in customize:
            is_pypy = True
            self.addRule(
                """
              stmt ::= assign3_pypy
              stmt ::= assign2_pypy
              assign3_pypy       ::= expr expr expr store store store
              assign2_pypy       ::= expr expr store store
              """,
                nop_func,
            )

        n = len(tokens)

        # Determine if we have an iteration CALL_FUNCTION_1.
        has_get_iter_call_function1 = False
        for i, token in enumerate(tokens):
            if (
                token == "GET_ITER"
                and i < n - 2
                and self.call_fn_name(tokens[i + 1]) == "CALL_FUNCTION_1"
            ):
                has_get_iter_call_function1 = True

        for i, token in enumerate(tokens):
            opname = token.kind

            # Do a quick breakout before testing potentially
            # each of the dozen or so instruction in if elif.
            if (
                opname[: opname.find("_")] not in customize_instruction_basenames
                or opname in custom_ops_processed
            ):
                continue

            opname_base = opname[: opname.rfind("_")]

            # The order of opname listed is roughly sorted below

            if opname == "LOAD_ASSERT" and "PyPy" in customize:
                rules_str = """
                stmt ::= JUMP_IF_NOT_DEBUG stmts COME_FROM
                """
                self.add_unique_doc_rules(rules_str, customize)

            elif opname == "BEFORE_ASYNC_WITH":
                rules_str = """
                   stmt            ::= async_with_stmt
                   stmt            ::= async_with_as_stmt
                   c_stmt          ::= c_async_with_stmt
                """

                if self.version < (3, 8):
                    rules_str += """
                      stmt                 ::= async_with_stmt SETUP_ASYNC_WITH
                      c_stmt               ::= c_async_with_stmt SETUP_ASYNC_WITH
                      async_with_stmt      ::= expr
                                               async_with_pre
                                               POP_TOP
                                               suite_stmts_opt
                                               POP_BLOCK LOAD_CONST
                                               async_with_post
                      c_async_with_stmt    ::= expr
                                               async_with_pre
                                               POP_TOP
                                               c_suite_stmts_opt
                                               POP_BLOCK LOAD_CONST
                                               async_with_post
                      async_with_stmt      ::= expr
                                               async_with_pre
                                               POP_TOP
                                               suite_stmts_opt
                                               async_with_post
                      c_async_with_stmt    ::= expr
                                               async_with_pre
                                               POP_TOP
                                               c_suite_stmts_opt
                                               async_with_post
                      async_with_as_stmt   ::= expr
                                               async_with_pre
                                               store
                                               suite_stmts_opt
                                               POP_BLOCK LOAD_CONST
                                               async_with_post
                      c_async_with_as_stmt ::= expr
                                              async_with_pre
                                              store
                                              c_suite_stmts_opt
                                              POP_BLOCK LOAD_CONST
                                              async_with_post
                      async_with_as_stmt   ::= expr
                                              async_with_pre
                                              store
                                              suite_stmts_opt
                                              async_with_post
                      c_async_with_as_stmt ::= expr
                                              async_with_pre
                                              store
                                              suite_stmts_opt
                                              async_with_post
                    """
                else:
                    rules_str += """
                      async_with_pre       ::= BEFORE_ASYNC_WITH GET_AWAITABLE LOAD_CONST YIELD_FROM SETUP_ASYNC_WITH
                      async_with_post      ::= BEGIN_FINALLY COME_FROM_ASYNC_WITH
                                               WITH_CLEANUP_START GET_AWAITABLE LOAD_CONST YIELD_FROM
                                               WITH_CLEANUP_FINISH END_FINALLY
                      async_with_stmt      ::= expr
                                               async_with_pre
                                               POP_TOP
                                               suite_stmts
                                               POP_TOP POP_BLOCK
                                               async_with_post
                      c_async_with_stmt    ::= expr
                                               async_with_pre
                                               POP_TOP
                                               c_suite_stmts
                                               POP_TOP POP_BLOCK
                                               async_with_post
                      async_with_stmt      ::= expr
                                               async_with_pre
                                               POP_TOP
                                               suite_stmts
                                               POP_BLOCK
                                               BEGIN_FINALLY
                                               WITH_CLEANUP_START GET_AWAITABLE LOAD_CONST YIELD_FROM
                                               WITH_CLEANUP_FINISH POP_FINALLY LOAD_CONST RETURN_VALUE
                                               COME_FROM_ASYNC_WITH
                                               WITH_CLEANUP_START GET_AWAITABLE LOAD_CONST YIELD_FROM
                                               WITH_CLEANUP_FINISH END_FINALLY
                      c_async_with_stmt   ::= expr
                                              async_with_pre
                                              POP_TOP
                                              c_suite_stmts
                                              POP_BLOCK
                                              BEGIN_FINALLY
                                              WITH_CLEANUP_START GET_AWAITABLE LOAD_CONST YIELD_FROM
                                              WITH_CLEANUP_FINISH POP_FINALLY LOAD_CONST RETURN_VALUE
                                              COME_FROM_ASYNC_WITH
                                              WITH_CLEANUP_START GET_AWAITABLE LOAD_CONST YIELD_FROM
                                              WITH_CLEANUP_FINISH END_FINALLY
                      async_with_as_stmt   ::= expr
                                               async_with_pre
                                               store suite_stmts
                                               POP_TOP POP_BLOCK
                                               async_with_post
                      c_async_with_as_stmt ::= expr
                                               async_with_pre
                                               store suite_stmts
                                               POP_TOP POP_BLOCK
                                               async_with_post
                      async_with_as_stmt   ::= expr
                                               async_with_pre
                                               store suite_stmts
                                               POP_BLOCK async_with_post
                      c_async_with_as_stmt ::= expr
                                               async_with_pre
                                               store suite_stmts
                                               POP_BLOCK async_with_post
                    """
                self.addRule(rules_str, nop_func)

            elif opname == "CONTINUE":
                self.addRule("continue ::= CONTINUE", nop_func)
                custom_ops_processed.add(opname)
            elif opname == "CONTINUE_LOOP":
                self.addRule("continue ::= CONTINUE_LOOP", nop_func)
                custom_ops_processed.add(opname)
            elif opname == "DELETE_ATTR":
                self.addRule("delete ::= expr DELETE_ATTR", nop_func)
                custom_ops_processed.add(opname)
            elif opname == "DELETE_DEREF":
                self.addRule(
                    """
                   stmt           ::= del_deref_stmt
                   del_deref_stmt ::= DELETE_DEREF
                   """,
                    nop_func,
                )
                custom_ops_processed.add(opname)
            elif opname == "DELETE_SUBSCR":
                self.addRule(
                    """
                    delete ::= delete_subscript
                    delete_subscript ::= expr expr DELETE_SUBSCR
                   """,
                    nop_func,
                )
                custom_ops_processed.add(opname)

            elif opname == "GET_AITER":
                self.addRule(
                    """
                    stmt ::= generator_exp_async
                    stmt ::= genexpr_func_async
                   """,
                    nop_func,
                )
                custom_ops_processed.add(opname)
            elif opname == "JUMP_IF_NOT_DEBUG":
                self.addRule(
                    """
                    stmt        ::= assert_pypy
                    stmt        ::= assert2_pypy", nop_func)
                    assert_pypy ::=  JUMP_IF_NOT_DEBUG expr POP_JUMP_IF_TRUE
                                     LOAD_ASSERT RAISE_VARARGS_1 COME_FROM
                    assert2_pypy ::= JUMP_IF_NOT_DEBUG assert_expr POP_JUMP_IF_TRUE
                                     LOAD_ASSERT expr CALL_FUNCTION_1
                                     RAISE_VARARGS_1 COME_FROM
                    assert2_pypy ::= JUMP_IF_NOT_DEBUG expr POP_JUMP_IF_TRUE
                                     LOAD_ASSERT expr CALL_FUNCTION_1
                                     RAISE_VARARGS_1 COME_FROM,
                    """,
                    nop_func,
                )
                custom_ops_processed.add(opname)

            elif opname == "LOAD_CLASSDEREF":
                # Python 3.4+
                self.addRule("expr ::= LOAD_CLASSDEREF", nop_func)
                custom_ops_processed.add(opname)

            elif opname == "LOAD_CLASSNAME":
                self.addRule("expr ::= LOAD_CLASSNAME", nop_func)
                custom_ops_processed.add(opname)

            elif opname == "RAISE_VARARGS_0":
                self.addRule(
                    """
                    stmt        ::= raise_stmt0
                    last_stmt  ::= raise_stmt0
                    raise_stmt0 ::= RAISE_VARARGS_0
                    """,
                    nop_func,
                )
                custom_ops_processed.add(opname)
            elif opname == "RAISE_VARARGS_1":
                self.addRule(
                    """
                    stmt        ::= raise_stmt1
                    last_stmt  ::= raise_stmt1
                    raise_stmt1 ::= expr RAISE_VARARGS_1
                    """,
                    nop_func,
                )
                custom_ops_processed.add(opname)
            elif opname == "RAISE_VARARGS_2":
                self.addRule(
                    """
                    stmt        ::= raise_stmt2
                    last_stmt  ::= raise_stmt2
                    raise_stmt2 ::= expr expr RAISE_VARARGS_2
                    """,
                    nop_func,
                )
                custom_ops_processed.add(opname)

            elif opname == "RETURN_VALUE_LAMBDA":
                self.addRule(
                    """
                    return_expr_lambda ::= return_expr RETURN_VALUE_LAMBDA
                    """,
                    nop_func,
                )
                custom_ops_processed.add(opname)
            elif opname == "SETUP_EXCEPT":
                self.addRule(
                    """
                    try_except     ::= SETUP_EXCEPT suite_stmts_opt POP_BLOCK
                                       except_handler opt_come_from_except
                    c_try_except   ::= SETUP_EXCEPT c_suite_stmts POP_BLOCK
                                       c_except_handler opt_come_from_except
                    stmt           ::= tryelsestmt3
                    tryelsestmt3   ::= SETUP_EXCEPT suite_stmts_opt POP_BLOCK
                                       except_handler COME_FROM else_suite
                                       opt_come_from_except

                    tryelsestmt    ::= SETUP_EXCEPT suite_stmts_opt POP_BLOCK
                                       except_handler else_suite come_from_except_clauses

                    tryelsestmt    ::= SETUP_EXCEPT suite_stmts_opt POP_BLOCK
                                       except_handler else_suite come_froms

                    c_stmt         ::= c_tryelsestmt
                    c_tryelsestmt  ::= SETUP_EXCEPT c_suite_stmts POP_BLOCK
                                       c_except_handler
                                       come_any_froms else_suitec
                                       come_from_except_clauses
                    """,
                    nop_func,
                )
                custom_ops_processed.add(opname)

            elif opname == "WITH_CLEANUP_START":
                rules_str = """
                  stmt        ::= with_null
                  with_null   ::= with_suffix
                  with_suffix ::= WITH_CLEANUP_START WITH_CLEANUP_FINISH END_FINALLY
                """
                self.addRule(rules_str, nop_func)

            # FIXME: reconcile with same code in lambda_custom.py
            elif opname == "SETUP_WITH":
                rules_str = """
                  stmt        ::= with
                  stmt        ::= withasstmt
                  c_stmt      ::= c_with

                  c_with      ::= expr SETUP_WITH POP_TOP
                                  c_suite_stmts_opt
                                  COME_FROM_WITH
                                  with_suffix
                  c_with      ::= expr SETUP_WITH POP_TOP
                                  c_suite_stmts_opt
                                  POP_BLOCK LOAD_CONST COME_FROM_WITH
                                  with_suffix

                  with        ::= expr SETUP_WITH POP_TOP
                                  suite_stmts_opt
                                  COME_FROM_WITH
                                  with_suffix

                  withasstmt  ::= expr SETUP_WITH store suite_stmts_opt COME_FROM_WITH
                                  with_suffix

                  with        ::= expr
                                  SETUP_WITH POP_TOP suite_stmts_opt
                                  POP_BLOCK LOAD_CONST COME_FROM_WITH
                                  with_suffix
                  withasstmt  ::= expr
                                  SETUP_WITH store suite_stmts_opt
                                  POP_BLOCK LOAD_CONST COME_FROM_WITH
                                  with_suffix

                  with        ::= expr
                                  SETUP_WITH POP_TOP suite_stmts_opt
                                  POP_BLOCK LOAD_CONST COME_FROM_WITH
                                  with_suffix
                  withasstmt  ::= expr
                                  SETUP_WITH store suite_stmts_opt
                                  POP_BLOCK LOAD_CONST COME_FROM_WITH
                                  with_suffix
                """
                if self.version < (3, 8):
                    rules_str += """
                    with      ::= expr SETUP_WITH POP_TOP suite_stmts_opt POP_BLOCK
                                   LOAD_CONST
                                   with_suffix
                    """
                else:
                    rules_str += """
                     # A return at the end of a withas stmt can be this.
                     # FIXME: should this be a different kind of return?
                     return      ::= return_expr POP_BLOCK
                                     ROT_TWO
                                     BEGIN_FINALLY
                                     WITH_CLEANUP_START
                                     WITH_CLEANUP_FINISH
                                     POP_FINALLY
                                     RETURN_VALUE

                      with       ::= expr
                                     SETUP_WITH POP_TOP suite_stmts_opt
                                     POP_BLOCK LOAD_CONST COME_FROM_WITH
                                     with_suffix


                      withasstmt ::= expr
                                     SETUP_WITH store suite_stmts
                                     POP_BLOCK LOAD_CONST COME_FROM_WITH

                      withasstmt ::= expr
                                     SETUP_WITH store suite_stmts
                                     POP_BLOCK BEGIN_FINALLY COME_FROM_WITH
                                     with_suffix

                      # withasstmt ::= expr SETUP_WITH store suite_stmts
                      #                COME_FROM expr COME_FROM POP_BLOCK ROT_TWO
                      #                BEGIN_FINALLY WITH_CLEANUP_START WITH_CLEANUP_FINISH
                      #                POP_FINALLY RETURN_VALUE COME_FROM_WITH
                      #                WITH_CLEANUP_START WITH_CLEANUP_FINISH END_FINALLY

                      with         ::= expr SETUP_WITH POP_TOP suite_stmts_opt POP_BLOCK
                                       BEGIN_FINALLY COME_FROM_WITH
                                       with_suffix
                    """
                self.addRule(rules_str, nop_func)
            pass

        # self.reduce_check_table = {
        #     "ifstmts_jump": ifstmts_jump,
        #     "and": and_check,
        #     "and_cond": and_cond_check,
        #     "and_not": and_not_check,
        #     "if_and_stmt": if_and_stmt,
        #     "if_and_elsestmtc": if_and_elsestmt,
        #     "ifelsestmt": ifelsestmt,
        #     "ifelsestmtc": ifelsestmt,
        #     "iflaststmt": iflaststmt,
        #     "iflaststmtc": iflaststmt,
        #     "ifstmt": ifstmt,
        #     "ifstmtc": ifstmt,
        #     "lastc_stmt": lastc_stmt,
        #     "list_if_not": list_if_not,
        #     "not_or": not_or_check,
        #     "or": or_check,
        #     "or_cond": or_cond_check,
        #     "testtrue": testtrue,
        #     "testfalsec": testtrue,
        #     "while1elsestmt": while1elsestmt,
        #     "while1stmt": while1stmt,
        #     "whilestmt": whilestmt,
        #     "c_tryelsestmt": c_tryelsestmt,
        #     "c_try_except": tryexcept,
        # }

        # self.check_reduce["and"] = "AST"
        # self.check_reduce["and_cond"] = "AST"
        # self.check_reduce["and_not"] = "AST"
        # self.check_reduce["annotate_tuple"] = "tokens"
        # self.check_reduce["aug_assign1"] = "AST"
        # self.check_reduce["aug_assign2"] = "AST"
        # self.check_reduce["c_try_except"] = "AST"
        # self.check_reduce["c_tryelsestmt"] = "AST"
        # self.check_reduce["if_and_stmt"] = "AST"
        # self.check_reduce["if_and_elsestmtc"] = "AST"
        # self.check_reduce["ifelsestmt"] = "AST"
        # self.check_reduce["ifelsestmtc"] = "AST"
        # self.check_reduce["iflaststmt"] = "AST"
        # self.check_reduce["iflaststmtc"] = "AST"
        # self.check_reduce["ifstmt"] = "AST"
        # self.check_reduce["ifstmtc"] = "AST"
        # self.check_reduce["ifstmts_jump"] = "AST"
        # self.check_reduce["ifstmts_jumpc"] = "AST"
        # self.check_reduce["import_from37"] = "AST"
        # self.check_reduce["lastc_stmt"] = "tokens"
        # self.check_reduce["list_if_not"] = "AST"
        # self.check_reduce["while1elsestmt"] = "tokens"
        # self.check_reduce["while1stmt"] = "tokens"
        # self.check_reduce["whilestmt"] = "tokens"
        # self.check_reduce["not_or"] = "AST"
        # self.check_reduce["or"] = "AST"
        # self.check_reduce["or_cond"] = "tokens"
        # self.check_reduce["testtrue"] = "tokens"
        # self.check_reduce["testfalsec"] = "tokens"


        # self.remove_rules_38()
        # self.check_reduce["break"] = "tokens"
        # self.check_reduce["for38"] = "tokens"
        # self.check_reduce["pop_return"] = "tokens"
        # self.check_reduce["whileTruestmt38"] = "tokens"
        # self.check_reduce["whilestmt38"] = "tokens"
        # self.check_reduce["try_elsestmtl38"] = "AST"

        # self.reduce_check_table["break"] = break_check
        # self.reduce_check_table["for38"] = for38_check
        # self.reduce_check_table["pop_return"] = pop_return_check

        return

    def reduce_is_invalid(self, rule, ast, tokens, first, last):
        invalid = Python38LambdaCustom.reduce_is_invalid(self, rule, ast, tokens, first, last)
        if invalid:
            return invalid
        lhs = rule[0]
        if lhs in ("whileTruestmt38", "whilestmt38"):
            jb_index = last - 1
            while jb_index > 0 and tokens[jb_index].kind.startswith("COME_FROM"):
                jb_index -= 1
            t = tokens[jb_index]
            if t.kind != "JUMP_LOOP":
                return True
            return t.attr != tokens[first].off2int()
            pass

        return False
