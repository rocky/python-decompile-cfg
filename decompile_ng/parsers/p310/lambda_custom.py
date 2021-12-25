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
Cgrammar Customization rules for Python 3.10's Lambda expression grammar.
"""

from decompile_ng.parsers.p310.base import Python310BaseParser
from decompile_ng.parsers.parse_heads import PythonParserLambda, PythonBaseParser, nop_func
from spark_parser import DEFAULT_DEBUG as PARSER_DEFAULT_DEBUG

class Python310LambdaCustom(Python310BaseParser):
    def __init__(self):
        self.new_rules = set()
        self.customized = {}

    def customize_grammar_rules_lambda310(self, tokens, customize):
        super(Python310LambdaCustom, self).customize_grammar_rules(tokens, customize)
        self.check_reduce["call_kw"] = "AST"

        is_pypy = False

        # For a rough break out on the first word. This may
        # include instructions that don't need customization,
        # but we'll do a finer check after the rough breakout.
        customize_instruction_basenames = frozenset(
            (
                "BUILD",
                "BEFORE",
                "BUILD",
                "CALL",
                "DICT",
                "GET",
                "FORMAT",
                "LIST",
                "LOAD",
                "MAKE",
                "SETUP",
            )
        )

        # Opcode names in the custom_ops_processed set have rules that get added
        # unconditionally and the rules are constant. So they need to be done
        # only once and if we see the opcode a second we don't have to consider
        # adding more rules.
        #
        custom_ops_processed = frozenset()

        # A set of instruction operation names that exist in the token stream.
        # We use this customize the grammar that we create.
        # 2.6-compatible set comprehensions
        self.seen_ops = frozenset([t.kind for t in tokens])
        self.seen_op_basenames = frozenset(
            [opname[: opname.rfind("_")] for opname in self.seen_ops]
        )

        # Note: BUILD_TUPLE_UNPACK_WITH_CALL gets considered by
        # default because it starts with BUILD. So we'll set to ignore it from
        # the start.
        custom_ops_processed = set(("BUILD_TUPLE_UNPACK_WITH_CALL", "DICT_MERGE"))

        # Loop over instructions adding custom grammar rules based on
        # a specific instruction seen.

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
                and tokens[i + 1] == "CALL_FUNCTION_1"
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

            if opname_base == "BUILD_CONST_KEY_MAP":
                kvlist_n = "expr " * (token.attr)
                rule = """
                    expr ::= dict
                    dict ::= %sLOAD_CONST %s
                """ % (
                    kvlist_n,
                    opname,
                )
                self.addRule(rule, nop_func)
            # Must come before BUILD_LIST
            elif opname.startswith("BUILD_LIST_UNPACK"):
                v = token.attr
                rule = "build_list_unpack ::= %s%s" % ("expr " * v, opname)
                self.addRule(rule, nop_func)
                rule = "expr ::= build_list_unpack"
                self.add_unique_rule(rule, opname, token.attr, customize)

            elif opname.startswith("BUILD_LIST"):
                v = token.attr
                if v == 0:
                    rule_str = """
                       list        ::= BUILD_LIST_0
                       list_unpack ::= BUILD_LIST_0 expr LIST_EXTEND
                       list        ::= list_unpack
                    """
                    self.add_unique_doc_rules(rule_str, customize)
                else:
                    rule_str = f"""
                     list  ::= {'expr ' * v}{opname}
                     expr  ::= list
                    """
                    self.add_unique_doc_rules(rule_str, customize)

            elif opname_base.startswith("BUILD_MAP"):
                if opname == "BUILD_MAP_n":
                    # PyPy sometimes has no count. Sigh.
                    # FIXME...
                    pass
                else:
                    v = token.attr
                    if v == 0:
                        rules_str = f"""
                            dict ::= BUILD_MAP_0
                            expr ::= dict
                        """
                    else:
                        kvlist_n = f"kvlist_{token.attr}"
                        rules_str = f"""
                            {kvlist_n} ::= {"expr " * (token.attr * 2)}{opname}
                            dict ::=  {kvlist_n}
                            expr ::= dict
                        """
                    self.add_unique_doc_rules(rules_str, customize)

            elif opname == "DICT_UPDATE":
                self.add_unique_doc_rules(
                    f"""
                    dicts_unpack ::= dicts_unpack dict_update
                    dicts_unpack ::= dict_update

                    dict_update ::= dict DICT_UPDATE
                    dict_unpack ::= BUILD_MAP_0 dicts_unpack
                    expr        ::= dict_unpack
                    """,
                    customize,
                )

            elif opname == "GET_ITER":
                self.add_unique_doc_rules(
                    """
                    expr      ::= get_iter
                    get_iter  ::= expr GET_ITER
                    """,
                    customize,
                )

            elif opname == "LOAD_ASSERT":
                if "PyPy" in customize:
                    rules_str = """
                    stmt ::= JUMP_IF_NOT_DEBUG stmts COME_FROM
                    """
                    self.add_unique_doc_rules(rules_str, customize)
            elif opname == "LIST_TO_TUPLE":
                rule_str = """
                    lists ::= lists list
                    lists ::= list
                    list  ::= expr LIST_EXTEND
                    tuple_starred ::= BUILD_LIST_0 lists LIST_TO_TUPLE
                    expr ::= tuple_starred
                    """
                self.add_unique_doc_rules(rule_str, customize)
            elif opname == "FORMAT_VALUE":
                rules_str = """
                    expr              ::= formatted_value1
                    formatted_value1  ::= expr FORMAT_VALUE
                """
                self.add_unique_doc_rules(rules_str, customize)
            elif opname == "FORMAT_VALUE_ATTR":
                rules_str = """
                expr              ::= formatted_value2
                formatted_value2  ::= expr expr FORMAT_VALUE_ATTR
                """
                self.add_unique_doc_rules(rules_str, customize)


            elif opname_base.startswith("MAKE_FUNCTION"):
                args_pos, args_kw, annotate_args, closure = token.attr
                stack_count = args_pos + args_kw + annotate_args
                if closure:
                    if args_pos:
                        rule = """
                             expr     ::= mklambda
                             mklambda ::= %s%s%s%s
                             """ % (
                            "expr " * stack_count,
                            "load_closure " * closure,
                            "BUILD_TUPLE_1 LOAD_LAMBDA LOAD_STR ",
                            opname,
                        )
                    else:
                        rule = """
                             expr     ::= mklambda
                             mklambda ::= %s%s%s""" % (
                            "load_closure " * closure,
                            "LOAD_LAMBDA LOAD_STR ",
                            opname,
                        )
                    self.add_unique_rule(rule, opname, token.attr, customize)

                else:
                    rule = """
                         expr     ::= mklambda
                         mklambda ::= %sLOAD_LAMBDA LOAD_STR %s""" % (
                        ("expr " * stack_count),
                        opname,
                    )
                    self.add_unique_rule(rule, opname, token.attr, customize)

                rule = "mkfunc ::= %s%s%s%s" % (
                    "expr " * stack_count,
                    "load_closure " * closure,
                    "LOAD_CODE LOAD_STR ",
                    opname,
                )
                self.add_unique_rule(rule, opname, token.attr, customize)

                if has_get_iter_call_function1:
                    rule_pat = (
                        "generator_exp ::= %sload_genexpr %%s%s expr "
                        "GET_ITER CALL_FUNCTION_1"
                    ) % ("expr " * args_pos, opname)
                    self.add_make_function_rule(rule_pat, opname, token.attr, customize)
                    rule_pat = """
                           expr          ::= generator_exp
                           load_genexpr  ::= LOAD_GENEXPR
                           load_genexpr  ::= BUILD_TUPLE_1 LOAD_GENEXPR LOAD_STR
                           generator_exp ::= %sload_closure load_genexpr %%s%s expr
                           GET_ITER CALL_FUNCTION_1""" % (
                        "expr " * args_pos,
                        opname,
                    )
                    self.add_make_function_rule(rule_pat, opname, token.attr, customize)
                    if is_pypy or (i >= 2 and tokens[i - 2] == "LOAD_LISTCOMP"):
                        # 3.6+ sometimes bundles all of the
                        # 'exprs' in the rule above into a
                        # tuple.
                        rule_pat = (
                            "list_comp ::= load_closure LOAD_LISTCOMP %%s%s "
                            "expr GET_ITER CALL_FUNCTION_1" % (opname,)
                        )
                        self.add_make_function_rule(
                            rule_pat, opname, token.attr, customize
                        )
                        rule_pat = (
                            "list_comp ::= %sLOAD_LISTCOMP %%s%s expr "
                            "GET_ITER CALL_FUNCTION_1" % ("expr " * args_pos, opname)
                        )
                        self.add_make_function_rule(
                            rule_pat, opname, token.attr, customize
                        )

                if is_pypy or (i >= 2 and tokens[i - 2] == "LOAD_LAMBDA"):
                    rule_pat = """
                        expr     ::= mklambda
                        mklambda ::= %s%sLOAD_LAMBDA %%s%s
                        """ % (
                        ("expr " * args_pos),
                        ("kwarg " * args_kw),
                        opname,
                    )
                    self.add_make_function_rule(rule_pat, opname, token.attr, customize)
                continue

                args_pos, args_kw, annotate_args, closure = token.attr

                j = 2

                if has_get_iter_call_function1:
                    rule_pat = (
                        "generator_exp ::= %sload_genexpr %%s%s expr "
                        "GET_ITER CALL_FUNCTION_1" % ("expr " * args_pos, opname)
                    )
                    self.add_make_function_rule(rule_pat, opname, token.attr, customize)

                    if is_pypy or (i >= j and tokens[i - j] == "LOAD_LISTCOMP"):
                        # In the tokens we saw:
                        #   LOAD_LISTCOMP LOAD_CONST MAKE_FUNCTION (>= 3.3) or
                        #   LOAD_LISTCOMP MAKE_FUNCTION (< 3.3) or
                        #   and have GET_ITER CALL_FUNCTION_1
                        # Todo: For Pypy we need to modify this slightly
                        rule_pat = (
                            "list_comp ::= %sLOAD_LISTCOMP %%s%s expr "
                            "GET_ITER CALL_FUNCTION_1" % ("expr " * args_pos, opname)
                        )
                        self.add_make_function_rule(
                            rule_pat, opname, token.attr, customize
                        )

                # FIXME: Fold test  into add_make_function_rule
                if is_pypy or (i >= j and tokens[i - j] == "LOAD_LAMBDA"):
                    rule_pat = """
                        expr     ::= mklambda
                        mklambda ::= %s%sLOAD_LAMBDA %%s%s
                        """ % (
                        ("expr " * args_pos),
                        ("kwarg " * args_kw),
                        opname,
                    )
                    self.add_make_function_rule(rule_pat, opname, token.attr, customize)

                if args_kw == 0:
                    kwargs = "no_kwargs"
                    self.add_unique_rule("no_kwargs ::=", opname, token.attr, customize)
                else:
                    kwargs = "kwargs"

                # positional args before keyword args
                rule = "mkfunc ::= %s%s %s%s" % (
                    "expr " * args_pos,
                    kwargs,
                    "LOAD_CODE LOAD_STR ",
                    opname,
                )
                self.add_unique_rule(rule, opname, token.attr, customize)

            elif opname == "MAKE_FUNCTION_8":
                if "LOAD_DICTCOMP" in self.seen_ops:
                    # Is there something general going on here?
                    rule = """
                       dict_comp ::= load_closure LOAD_DICTCOMP LOAD_STR
                                     MAKE_FUNCTION_8 expr
                                     GET_ITER CALL_FUNCTION_1
                       """
                    self.addRule(rule, nop_func)
                elif "LOAD_SETCOMP" in self.seen_ops:
                    rule = """
                       set_comp ::= load_closure LOAD_SETCOMP LOAD_STR
                                    MAKE_FUNCTION_8 expr
                                    GET_ITER CALL_FUNCTION_1
                       """
                    self.addRule(rule, nop_func)

            elif opname == "BEFORE_ASYNC_WITH":
                rules_str = """
                  stmt               ::= async_with_stmt SETUP_ASYNC_WITH
                  async_with_pre     ::= BEFORE_ASYNC_WITH GET_AWAITABLE LOAD_CONST YIELD_FROM SETUP_ASYNC_WITH
                  async_with_post    ::= COME_FROM_ASYNC_WITH
                                         WITH_CLEANUP_START GET_AWAITABLE LOAD_CONST YIELD_FROM
                                         WITH_CLEANUP_FINISH END_FINALLY

                  stmt               ::= async_with_as_stmt
                  async_with_as_stmt ::= expr
                                         async_with_pre
                                         store
                                         suite_stmts_opt
                                         POP_BLOCK LOAD_CONST
                                         async_with_post

                 async_with_stmt     ::= expr
                                         async_with_pre
                                         POP_TOP
                                         suite_stmts_opt
                                         POP_BLOCK LOAD_CONST
                                         async_with_post
                 async_with_stmt     ::= expr
                                         async_with_pre
                                         POP_TOP
                                         suite_stmts_opt
                                         async_with_post
                """
                self.addRule(rules_str, nop_func)

            elif opname.startswith("BUILD_STRING"):
                v = token.attr
                rules_str = """
                    expr                 ::= joined_str
                    joined_str           ::= %sBUILD_STRING_%d
                """ % (
                    "expr " * v,
                    v,
                )
                self.add_unique_doc_rules(rules_str, customize)
                if "FORMAT_VALUE_ATTR" in self.seen_ops:
                    rules_str = """
                      formatted_value_attr ::= expr expr FORMAT_VALUE_ATTR expr BUILD_STRING
                      expr                 ::= formatted_value_attr
                    """
                    self.add_unique_doc_rules(rules_str, customize)
            elif opname.startswith("BUILD_MAP_UNPACK_WITH_CALL"):
                v = token.attr
                rule = "build_map_unpack_with_call ::= %s%s" % ("expr " * v, opname)
                self.addRule(rule, nop_func)
            elif opname.startswith("BUILD_TUPLE_UNPACK_WITH_CALL"):
                v = token.attr
                rule = (
                    "build_tuple_unpack_with_call ::= "
                    + "expr1024 " * int(v // 1024)
                    + "expr32 " * int((v // 32) % 32)
                    + "expr " * (v % 32)
                    + opname
                )
                self.addRule(rule, nop_func)
                rule = "starred ::= %s %s" % ("expr " * v, opname)
                self.addRule(rule, nop_func)
            elif opname == "SETUP_WITH":
                rules_str = """
                with       ::= expr SETUP_WITH POP_TOP suite_stmts_opt COME_FROM_WITH
                               WITH_CLEANUP_START WITH_CLEANUP_FINISH END_FINALLY

                # Removes POP_BLOCK LOAD_CONST from 3.6-
                withasstmt ::= expr SETUP_WITH store suite_stmts_opt COME_FROM_WITH
                               WITH_CLEANUP_START WITH_CLEANUP_FINISH END_FINALLY
                """
                if self.version < (3, 8):
                    rules_str += """
                    with       ::= expr SETUP_WITH POP_TOP suite_stmts_opt POP_BLOCK
                                   LOAD_CONST
                                   WITH_CLEANUP_START WITH_CLEANUP_FINISH END_FINALLY
                    """
                else:
                    rules_str += """
                    with        ::= expr SETUP_WITH POP_TOP suite_stmts_opt POP_BLOCK
                                   BEGIN_FINALLY COME_FROM_WITH
                                   WITH_CLEANUP_START WITH_CLEANUP_FINISH
                                   END_FINALLY
                    """
                self.addRule(rules_str, nop_func)
                pass
            pass

    def custom_classfunc_rule(self, opname, token, customize, next_token):

        args_pos, args_kw = self.get_pos_kw(token)

        # Additional exprs for * and ** args:
        #  0 if neither
        #  1 for CALL_FUNCTION_VAR or CALL_FUNCTION_KW
        #  2 for * and ** args (CALL_FUNCTION_VAR_KW).
        # Yes, this computation based on instruction name is a little bit hoaky.
        nak = (len(opname) - len("CALL_FUNCTION")) // 3
        uniq_param = args_kw + args_pos

        if frozenset(("GET_AWAITABLE", "YIELD_FROM")).issubset(self.seen_ops):
            rule = (
                "async_call ::= expr "
                + ("expr " * args_pos)
                + ("kwarg " * args_kw)
                + "expr " * nak
                + token.kind
                + " GET_AWAITABLE LOAD_CONST YIELD_FROM"
            )
            self.add_unique_rule(rule, token.kind, uniq_param, customize)
            self.add_unique_rule(
                "expr ::= async_call", token.kind, uniq_param, customize
            )

        if opname.startswith("CALL_FUNCTION_KW"):
            self.addRule("expr ::= call_kw36", nop_func)
            values = "expr " * token.attr
            rule = "call_kw36 ::= expr {values} LOAD_CONST {opname}".format(**locals())
            self.add_unique_rule(rule, token.kind, token.attr, customize)
        elif opname == "CALL_FUNCTION_EX_KW":
            self.addRule(
                """expr        ::= call_ex_kw4
                   call_ex_kw4 ::= expr
                                   expr
                                   BUILD_MAP_0 expr DICT_MERGE
                                   CALL_FUNCTION_EX_KW
                """,
                nop_func,
            )
            if "BUILD_MAP_UNPACK_WITH_CALL" in self.seen_op_basenames:
                self.addRule(
                    """expr       ::= call_ex_kw
                      call_ex_kw  ::= expr expr build_map_unpack_with_call
                                      CALL_FUNCTION_EX_KW
                             """,
                    nop_func,
                )
            if "DICT_MERGE" in self.seen_ops:
                self.addRule(
                    f"""expr           ::= call_ex_kw3
                        tuple_starred ::= BUILD_LIST_1 expr LIST_EXTEND LIST_TO_TUPLE
                        call_ex_kw3    ::= expr
                                           {("expr " * args_pos)}
                                           tuple_starred
                                           BUILD_MAP_0 expr DICT_MERGE
                                           CALL_FUNCTION_EX_KW
                     """,
                    nop_func,
                )
            if "BUILD_TUPLE_UNPACK_WITH_CALL" in self.seen_op_basenames:
                # FIXME: should this be parameterized by EX value?
                self.addRule(
                    """expr        ::= call_ex_kw3
                       call_ex_kw3 ::= expr
                                       build_tuple_unpack_with_call
                                       expr
                                      CALL_FUNCTION_EX_KW
                    """,
                    nop_func,
                )
                if "BUILD_MAP_UNPACK_WITH_CALL" in self.seen_op_basenames:
                    # FIXME: should this be parameterized by EX value?
                    self.addRule(
                        """expr        ::= call_ex_kw2
                           call_ex_kw2 ::= expr
                           build_tuple_unpack_with_call
                           build_map_unpack_with_call
                           CALL_FUNCTION_EX_KW
                        """,
                        nop_func,
                    )

        elif opname == "CALL_FUNCTION_EX":
            self.addRule(
                """expr        ::= call_ex
                   starred     ::= expr
                   call_ex     ::= expr starred CALL_FUNCTION_EX
                """,
                nop_func,
            )
            if "BUILD_MAP_UNPACK_WITH_CALL" in self.seen_ops:
                self.addRule(
                    """expr        ::= call_ex_kw
                       call_ex_kw  ::= expr expr
                       build_map_unpack_with_call CALL_FUNCTION_EX
                     """,
                    nop_func,
                )
            if "BUILD_TUPLE_UNPACK_WITH_CALL" in self.seen_ops:
                self.addRule(
                    """expr        ::= call_ex_kw3
                       call_ex_kw3 ::= expr
                                       build_tuple_unpack_with_call
                                       %s
                                       CALL_FUNCTION_EX
                    """
                    % "expr "
                    * token.attr,
                    nop_func,
                )
                pass

            # FIXME: Is this right?
            self.addRule(
                """expr        ::= call_ex_kw4
                   call_ex_kw4 ::= expr
                                   expr
                                   expr
                                   CALL_FUNCTION_EX
                """,
                nop_func,
            )
            pass
        else:
            Python310BaseParser.custom_classfunc_rule(
                self, opname, token, customize, next_token
            )
