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
Grammar Customization rules for Python 3.8's Lambda expression grammar.
"""

from decompile_cfg.parsers.p38.base import Python38BaseParser
from decompile_cfg.parsers.parse_heads import ParserError, nop_func
from decompile_cfg.parsers.reduce_check.and_check import and_ok
from decompile_cfg.parsers.reduce_check.if_exp_check import if_exp_ok
from spark_parser.spark import rule2str

class Python38LambdaCustom(Python38BaseParser):
    def __init__(self):
        self.new_rules = set()
        self.customized = {}

    def custom_classfunc_rule_lambda(self, opname, token, customize, next_token):
        """
        call ::= expr {expr}^n CALL_FUNCTION_n
        call ::= expr {expr}^n CALL_FUNCTION_VAR_n
        call ::= expr {expr}^n CALL_FUNCTION_VAR_KW_n
        call ::= expr {expr}^n CALL_FUNCTION_KW_n

        classdefdeco2 ::= LOAD_BUILD_CLASS mkfunc {expr}^n-1 CALL_FUNCTION_n
        """
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

        if opname.startswith("CALL_FUNCTION_VAR"):
            token.kind = self.call_fn_name(token)
            if opname.endswith("KW"):
                kw = "expr "
            else:
                kw = ""
            rule = (
                "call ::= expr expr "
                + ("arg " * args_pos)
                + ("kwarg " * args_kw)
                + kw
                + token.kind
            )

            # Note: semantic actions make use of the fact of whether "args_pos"
            # zero or not in creating a template rule.
            self.add_unique_rule(rule, token.kind, args_pos, customize)

        # Has to come before generic CALL_FUNCTION else below
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
            if "DICT_MERGE" in self.seen_ops:
                self.addRule(
                    f"""expr               ::= call_ex_kw3
                        tuple_list_starred ::= BUILD_LIST_1 expr LIST_EXTEND LIST_TO_TUPLE
                        call_ex_kw3        ::= expr
                                               {("expr " * args_pos)}
                                               tuple_list_starred
                                               BUILD_MAP_0 expr DICT_MERGE
                                               CALL_FUNCTION_EX_KW
                     """,
                    nop_func,
                )

        if opname.startswith("CALL_FUNCTION_KW"):
            self.addRule("expr ::= call_kw36", nop_func)
            values = "expr " * token.attr
            rule = "call_kw36 ::= expr {values} LOAD_CONST {opname}".format(**locals())
            self.add_unique_rule(rule, token.kind, token.attr, customize)

        else:
            if opname == "CALL_FUNCTION_EX":
                # FIXME probably not right. Probably the number of expr's should match
                # the number after BUILD_LIST_
                # FIXME: can BUILD_LIST_1 appear?
                self.addRule(
                    """
                             expr        ::= call_ex
                             starred     ::= expr
                             call_ex     ::= expr starred CALL_FUNCTION_EX
                             """,
                    nop_func,
                )
                if opname == "BUILD_MAP_UNPACK_WITH_CALL":
                    self.addRule(
                        """expr        ::= call_ex_kw
                           call_ex_kw  ::= expr expr
                           build_map_unpack_with_call CALL_FUNCTION_EX
                         """,
                        nop_func,
                    )
                if opname == "BUILD_TUPLE_UNPACK_WITH_CALL":
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
                pass

            else:
                # FIXME: Is this correct still? Note: 3.5+ have subclassed this method; so we don't handle
                # 'CALL_FUNCTION_VAR'.
                token.kind = self.call_fn_name(token)

                rule = (
                    "call ::= arg "
                    + ("arg " * args_pos)
                    + ("kwarg " * args_kw)
                    + "expr " * nak
                    + token.kind
                )

                self.add_unique_rule(rule, token.kind, uniq_param, customize)

            if "LOAD_BUILD_CLASS" in self.seen_ops:
                if (
                    next_token == "CALL_FUNCTION"
                    and next_token.attr == 1
                    and args_pos > 1
                ):
                    rule = "classdefdeco2 ::= LOAD_BUILD_CLASS mkfunc %s%s_%d" % (
                        ("expr " * (args_pos - 1)),
                        opname,
                        args_pos,
                    )
                    self.add_unique_rule(rule, token.kind, uniq_param, customize)

    def customize_grammar_rules_lambda38(self, tokens, customize):

        self.reduce_check_table = {
            "and1": and_ok,
            "if_exp": if_exp_ok
        }

        self.check_reduce["and1"] = "AST"
        self.check_reduce["if_exp"] = "AST"

        is_pypy = False

        # For a rough break out on the first word. This may
        # include instructions that don't need customization,
        # but we'll do a finer check after the rough breakout.
        customize_instruction_basenames = frozenset(
            (
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
                "UNPACK",
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

        custom_ops_processed = set(["DICT_MERGE"])

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
                    """
                    self.add_unique_doc_rules(rule_str, customize)

            elif opname_base.startswith("BUILD_MAP"):
                if opname == "BUILD_MAP_UNPACK":
                    self.addRule(
                        f"""
                        expr        ::= dict_unpack
                        dict_unpack ::= {"expr " * token.attr} BUILD_MAP_UNPACK
                        """,
                        nop_func,
                    )
                    pass

                elif opname == "BUILD_MAP_n":
                    # PyPy sometimes has no count. Sigh.
                    # FIXME...
                    pass
                else:
                    v = token.attr
                    if v == 0:
                        rules_str = """
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

                if opname.startswith("BUILD_MAP_UNPACK_WITH_CALL"):
                    self.addRule(
                        """expr       ::= call_ex_kw
                          call_ex_kw  ::= expr expr build_map_unpack_with_call
                                          CALL_FUNCTION_EX_KW
                        """,
                        nop_func,
                    )
                    v = token.attr
                    rule = "build_map_unpack_with_call ::= %s%s" % ("expr " * v, opname)
                    self.addRule(rule, nop_func)


            elif opname_base in (
                "BUILD_SET",
                "BUILD_TUPLE",
            ):
                v = token.attr

                if opname == "BUILD_TUPLE_UNPACK_WITH_CALL":
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

                is_LOAD_CLOSURE = False
                if opname_base == "BUILD_TUPLE":
                    # If is part of a "load_closure", then it is not part of a
                    # "list".
                    is_LOAD_CLOSURE = True
                    for j in range(v):
                        if tokens[i - j - 1].kind != "LOAD_CLOSURE":
                            is_LOAD_CLOSURE = False
                            break
                    if is_LOAD_CLOSURE:
                        rule = "load_closure ::= %s%s" % (("LOAD_CLOSURE " * v), opname)
                        self.add_unique_rule(rule, opname, token.attr, customize)
                if not is_LOAD_CLOSURE or v == 0:
                    # We do this complicated test to speed up parsing of
                    # pathelogically long literals, especially those over 1024.
                    build_count = token.attr
                    thousands = build_count // 1024
                    thirty32s = (build_count // 32) % 32
                    if thirty32s > 0:
                        rule = "arg32 ::=%s" % (" arg" * 32)
                        self.add_unique_rule(rule, opname_base, build_count, customize)
                        pass
                    if thousands > 0:
                        self.add_unique_rule(
                            "arg1024 ::=%s" % (" arg32" * 32),
                            opname_base,
                            build_count,
                            customize,
                        )
                        pass
                    collection = opname_base[opname_base.find("_") + 1 :].lower()
                    rule = (
                        f"{collection} ::= "
                        + "arg1024 " * thousands
                        + "argr32 " * thirty32s
                        + "arg " * (build_count % 32)
                        + opname
                    )
                    self.add_unique_rules([f"expr ::= {collection}", rule], customize)
                    continue
                continue

            elif opname_base == "BUILD_SLICE":
                if token.attr == 2:
                    self.add_unique_rules(
                        [
                            "expr ::= build_slice2",
                            "build_slice2 ::= expr expr BUILD_SLICE_2",
                        ],
                        customize,
                    )
                else:
                    assert token.attr == 3, (
                        "BUILD_SLICE value must be 2 or 3; is %s" % v
                    )
                    self.add_unique_rules(
                        [
                            "expr ::= build_slice3",
                            "build_slice3 ::= expr expr expr BUILD_SLICE_3",
                        ],
                        customize,
                    )

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

            elif opname == "BUILD_MAP_UNPACK_WITH_CALL":
                v = token.attr
                rule = "build_map_unpack_with_call ::= %s%s" % ("expr " * v, opname)
                self.addRule(rule, nop_func)

            elif opname == "BUILD_TUPLE_UNPACK_WITH_CALL":
                v = token.attr
                rule = (
                    "build_tuple_unpack_with_call ::= "
                    + "expr1024 " * int(v // 1024)
                    + "expr32 " * int((v // 32) % 32)
                    + "expr " * (v % 32)
                    + opname
                )
                self.addRule(rule, nop_func)
                rule = "starred ::= %s%s" % ("arg " * v, opname)
                self.addRule(rule, nop_func)

            elif opname in frozenset(
                (
                    "CALL_FUNCTION",
                    "CALL_FUNCTION_EX",
                    "CALL_FUNCTION_EX_KW",
                    "CALL_FUNCTION_VAR",
                    "CALL_FUNCTION_VAR_KW",
                )
            ) or opname.startswith("CALL_FUNCTION_KW"):

                self.addRule(
                    """expr        ::= call_ex_kw4
                       call_ex_kw4 ::= arg arg arg
                                       CALL_FUNCTION_EX_KW
                     """,
                    nop_func,
                )
                if "BUILD_MAP_UNPACK_WITH" in self.seen_op_basenames:
                    self.addRule(
                        """expr        ::= call_ex_kw
                           call_ex_kw  ::= expr expr build_map_unpack_with_call
                                           CALL_FUNCTION_EX_KW
                        """,
                        nop_func,
                    )

                if "BUILD_TUPLE_UNPACK_WITH" in self.seen_op_basenames:
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

                if "BUILD_MAP_UNPACK_WITH" in self.seen_op_basenames:
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

                if opname == "CALL_FUNCTION" and token.attr == 1:
                    rule = """
                     expr         ::= dict_comp
                     dict_comp    ::= LOAD_DICTCOMP LOAD_STR MAKE_FUNCTION_0 expr
                                      GET_ITER CALL_FUNCTION_1
                    classdefdeco1 ::= expr classdefdeco2 CALL_FUNCTION_1
                    classdefdeco1 ::= expr classdefdeco1 CALL_FUNCTION_1
                    """
                    self.addRule(rule, nop_func)

                # Don't add to custom_ops_processed for CALL_FUNCTION_EX_KW, since
                # the the call_ex_... rules above cover this.
                if opname not in ("CALL_FUNCTION_EX_KW", "CALL_FUNCTION_KW"):
                    self.custom_classfunc_rule_lambda(opname, token, customize, tokens[i + 1])


            elif opname_base == "CALL_METHOD":
                # PyPy and Python 3.7+ only - DRY with parse2

                args_pos, args_kw = self.get_pos_kw(token)

                # number of apply equiv arguments:
                nak = (len(opname_base) - len("CALL_METHOD")) // 3
                rule = (
                    "call ::= arg "
                    + ("arg " * args_pos)
                    + ("kwarg " * args_kw)
                    + "arg " * nak
                    + opname
                )
                self.add_unique_rule(rule, opname, token.attr, customize)

            elif opname == "DICT_UPDATE":
                self.add_unique_doc_rules(
                    """
                    dicts_unpack ::= dicts_unpack dict_update
                    dicts_unpack ::= dict_update

                    dict_update ::= dict DICT_UPDATE
                    dict_unpack ::= BUILD_MAP_0 dicts_unpack
                    expr        ::= dict_unpack
                    """,
                    customize,
                )

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

            elif opname == "GET_AITER":
                self.addRule(
                    """
                    dict_comp_async      ::= LOAD_DICTCOMP
                                             LOAD_STR
                                             MAKE_FUNCTION_0
                                             expr
                                             GET_AITER
                                             CALL_FUNCTION_1

                    dict_comp_async      ::= BUILD_MAP_0 LOAD_ARG
                                             dict_comp_async

                    expr                 ::= dict_comp_async
                    expr                 ::= generator_exp_async
                    expr                 ::= list_comp_async

                    func_async_middle   ::= POP_BLOCK JUMP_FORWARD COME_FROM_EXCEPT
                                            DUP_TOP LOAD_GLOBAL COMPARE_OP POP_JUMP_IF_TRUE
                                            END_FINALLY bb_end_start

                    func_async_prefix   ::= _come_froms SETUP_EXCEPT GET_ANEXT LOAD_CONST YIELD_FROM

                    generator_exp_async  ::= load_genexpr LOAD_STR MAKE_FUNCTION_0 expr
                                             GET_AITER CALL_FUNCTION_1

                    generator_exp_async  ::= LOAD_ARG func_async_prefix
                                             store
                                             JUMP_LOOP bb_end_start
                                             POP_TOP POP_TOP POP_TOP POP_EXCEPT POP_TOP

                    genexpr_func_async  ::= LOAD_ARG func_async_prefix
                                            store
                                            func_async_middle comp_iter
                                            JUMP_LOOP bb_end_start
                                            POP_TOP POP_TOP POP_TOP POP_EXCEPT POP_TOP

                    get_aiter            ::= expr GET_AITER

                    list_afor            ::= get_aiter list_afor2

                    list_comp_async      ::= LOAD_LISTCOMP LOAD_STR MAKE_FUNCTION_0
                                             expr GET_AITER CALL_FUNCTION_1
                                             GET_AWAITABLE LOAD_CONST
                                             YIELD_FROM

                    list_comp_async      ::= BUILD_LIST_0 LOAD_ARG list_afor2
                    list_comp_async      ::= LOAD_LISTCOMP LOAD_STR MAKE_FUNCTION_0
                                             expr GET_AITER CALL_FUNCTION_1
                                             GET_AWAITABLE LOAD_CONST
                                             YIELD_FROM
                    list_iter            ::= list_afor
                   """,
                    nop_func,
                )
                custom_ops_processed.add(opname)

            elif opname == "GET_ANEXT":
                self.addRule(
                    """
                    expr                 ::= genexpr_func_async
                    expr                 ::= BUILD_MAP_0 genexpr_func_async
                    expr                 ::= list_comp_async

                    func_async_prefix    ::= block_break
                                             SETUP_FINALLY GET_ANEXT LOAD_CONST YIELD_FROM POP_BLOCK

                    genexpr_func_async   ::= LOAD_ARG func_async_prefix
                                             store
                                             comp_iter
                                             JUMP_LOOP
                                             block_break
                                             END_ASYNC_FOR

                    list_afor2           ::= func_async_prefix
                                             store
                                             list_iter
                                             JUMP_LOOP
                                             block_break
                                             END_ASYNC_FOR

                    list_afor2           ::= func_async_prefix
                                             store
                                             func_async_middle
                                             list_iter
                                             JUMP_LOOP
                                             bb_end_start
                                             POP_TOP POP_TOP POP_TOP POP_EXCEPT POP_TOP

                    list_comp_async      ::= BUILD_LIST_0 LOAD_ARG list_afor2

                   """,
                    nop_func,
                )
                custom_ops_processed.add(opname)

            elif opname == "GET_AWAITABLE":
                rule_str = """
                    await_expr ::= expr GET_AWAITABLE LOAD_CONST YIELD_FROM
                    expr       ::= await_expr
                """
                self.add_unique_doc_rules(rule_str, customize)

            elif opname == "GET_ITER":
                self.add_unique_doc_rules(
                    """
                    expr      ::= get_iter
                    get_iter  ::= expr block_break GET_ITER
                    """,
                    customize,
                )

            elif opname == "LIST_TO_TUPLE":
                rule_str = """
                    lists ::= lists list
                    lists ::= list
                    list  ::= expr LIST_EXTEND
                    tuple_list_starred ::= BUILD_LIST_0 lists LIST_TO_TUPLE
                    expr ::= tuple_list_starred
                    """
                self.add_unique_doc_rules(rule_str, customize)

            elif opname == "LOAD_ASSERT":
                if "PyPy" in customize:
                    rules_str = """
                    stmt ::= JUMP_IF_NOT_DEBUG stmts COME_FROM
                    """
                    self.add_unique_doc_rules(rules_str, customize)

            elif opname == "LOAD_ATTR":
                self.addRule(
                    """
                  expr      ::= attribute
                  attribute ::= expr LOAD_ATTR
                  """,
                    nop_func,
                )
                custom_ops_processed.add(opname)

            elif opname == "LOAD_CLOSURE":
                self.addRule("""load_closure ::= LOAD_CLOSURE+""", nop_func)

            elif opname == "LOAD_DICTCOMP":
                if has_get_iter_call_function1:
                    rule_pat = (
                        "dict_comp ::= LOAD_DICTCOMP %sMAKE_FUNCTION_0 expr "
                        "GET_ITER CALL_FUNCTION_1"
                    )
                    self.add_make_function_rule(rule_pat, opname, token.attr, customize)
                    pass
                custom_ops_processed.add(opname)



            elif opname == "LOAD_GENEXPR":
                self.addRule("load_genexpr ::= LOAD_GENEXPR", nop_func)
                custom_ops_processed.add(opname)

            elif opname == "LOAD_LISTCOMP":
                self.add_unique_rule(
                    "expr ::= list_comp", opname, token.attr, customize
                )
                custom_ops_processed.add(opname)

            elif opname == "LOAD_NAME":
                if (
                    token.attr == "__annotations__"
                    and "SETUP_ANNOTATIONS" in self.seen_ops
                ):
                    token.kind = "LOAD_ANNOTATION"
                    self.addRule(
                        """
                        stmt       ::= SETUP_ANNOTATIONS
                        stmt       ::= ann_assign
                        ann_assign ::= expr LOAD_ANNOTATION LOAD_STR STORE_SUBSCR
                        """,
                        nop_func,
                    )
                    pass
            elif opname == "LOAD_SETCOMP":
                # Should this be generalized and put under MAKE_FUNCTION?
                if has_get_iter_call_function1:
                    self.addRule("expr ::= set_comp", nop_func)
                    rule_pat = (
                        "set_comp ::= LOAD_SETCOMP %sMAKE_FUNCTION_0 expr "
                        "GET_ITER CALL_FUNCTION_1"
                    )
                    self.add_make_function_rule(rule_pat, opname, token.attr, customize)
                    pass
                custom_ops_processed.add(opname)
            elif opname == "LOOKUP_METHOD":
                # A PyPy speciality - DRY with parse3
                self.addRule(
                    """
                             expr      ::= attribute
                             attribute ::= expr LOOKUP_METHOD
                             """,
                    nop_func,
                )
                custom_ops_processed.add(opname)
            elif opname.startswith("MAKE_CLOSURE"):
                # DRY with MAKE_FUNCTION
                # Note: this probably doesn't handle kwargs proprerly

                if opname == "MAKE_CLOSURE_0" and "LOAD_DICTCOMP" in self.seen_ops:
                    # Is there something general going on here?
                    # Note that 3.6+ doesn't do this, but we'll remove
                    # this rule in parse36.py
                    rule = """
                        dict_comp ::= load_closure LOAD_DICTCOMP LOAD_STR
                                      MAKE_CLOSURE_0 expr
                                      GET_ITER CALL_FUNCTION_1
                    """
                    self.addRule(rule, nop_func)

                args_pos, args_kw, annotate_args = token.attr

                # FIXME: Fold test  into add_make_function_rule
                j = 2
                if is_pypy or (i >= j and tokens[i - j] == "LOAD_LAMBDA"):
                    rule_pat = """
                                expr        ::= lambda_body
                                lambda_body ::= %sload_closure LOAD_LAMBDA %%s%s
                               """ % (
                        "expr " * args_pos,
                        opname,
                    )
                    self.add_make_function_rule(rule_pat, opname, token.attr, customize)

                if has_get_iter_call_function1:
                    rule_pat = (
                        "generator_exp ::= %sload_closure load_genexpr %%s%s expr "
                        "GET_ITER CALL_FUNCTION_1" % ("expr " * args_pos, opname)
                    )
                    self.add_make_function_rule(rule_pat, opname, token.attr, customize)

                    if has_get_iter_call_function1:
                        if is_pypy or (i >= j and tokens[i - j] == "LOAD_LISTCOMP"):
                            # In the tokens we saw:
                            #   LOAD_LISTCOMP LOAD_CONST MAKE_FUNCTION (>= 3.3) or
                            #   LOAD_LISTCOMP MAKE_FUNCTION (< 3.3) or
                            #   and have GET_ITER CALL_FUNCTION_1
                            # Todo: For Pypy we need to modify this slightly
                            rule_pat = (
                                "list_comp ::= %sload_closure LOAD_LISTCOMP %%s%s expr "
                                "GET_ITER CALL_FUNCTION_1"
                                % ("expr " * args_pos, opname)
                            )
                            self.add_make_function_rule(
                                rule_pat, opname, token.attr, customize
                            )
                        if is_pypy or (i >= j and tokens[i - j] == "LOAD_SETCOMP"):
                            rule_pat = (
                                "set_comp ::= %sload_closure LOAD_SETCOMP %%s%s expr "
                                "GET_ITER CALL_FUNCTION_1"
                                % ("expr " * args_pos, opname)
                            )
                            self.add_make_function_rule(
                                rule_pat, opname, token.attr, customize
                            )
                        if is_pypy or (i >= j and tokens[i - j] == "LOAD_DICTCOMP"):
                            self.add_unique_rule(
                                "dict_comp ::= %sload_closure LOAD_DICTCOMP %s "
                                "expr GET_ITER CALL_FUNCTION_1"
                                % ("expr " * args_pos, opname),
                                opname,
                                token.attr,
                                customize,
                            )

                if args_kw > 0:
                    kwargs_str = "kwargs "
                else:
                    kwargs_str = ""

                rule = "mkfunc ::= %s%s%s load_closure LOAD_CODE LOAD_STR %s" % (
                    "expr " * args_pos,
                    kwargs_str,
                    "expr " * annotate_args,
                    opname,
                )

                self.add_unique_rule(rule, opname, token.attr, customize)

                if args_kw == 0:
                    rule = "mkfunc ::= %sload_closure load_genexpr %s" % (
                        "expr " * args_pos,
                        opname,
                    )
                    self.add_unique_rule(rule, opname, token.attr, customize)

                pass

            elif opname_base.startswith("MAKE_FUNCTION"):
                args_pos, args_kw, annotate_args, closure = token.attr
                stack_count = args_pos + args_kw + annotate_args

                if closure:

                    if opname == "MAKE_FUNCTION_8":
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

                    if args_pos:
                        if opname == "MAKE_FUNCTION_9":
                            # This was seen ion line 447 of Python 3.8
                            # This is needed for Python 3.8 line 447 of site-packages/nltk/tgrep.py
                            # line 447:
                            #    lambda i: lambda n, m=None, l=None: ...
                            # which has
                            #  L. 447         0  LOAD_CONST               (None, None)
                            #                 2  LOAD_CLOSURE             'i'
                            #                 4  LOAD_CLOSURE             'predicate'
                            #                 6  BUILD_TUPLE_2         2
                            #                 8  LOAD_LAMBDA              '<code_object <lambda>>'
                            #                10  LOAD_STR                 '_tgrep_relation_action.<locals>.<lambda>.<locals>.<lambda>'
                            #                12  MAKE_FUNCTION_9          'default, closure'
                            # FIXME: Possibly we need to generalize for more nested lambda's of lambda's?
                            rule = """
                                 expr        ::= lambda_body
                                 lambda_body ::= %s%s%s%s
                                 """ % (
                                "expr " * stack_count,
                                "load_closure " * closure,
                                "BUILD_TUPLE_2 LOAD_LAMBDA LOAD_STR ",
                                opname,
                            )
                            self.add_unique_rule(rule, opname, token.attr, customize)
                        rule = """
                             expr        ::= lambda_body
                             lambda_body ::= %s%s%s%s
                             """ % (
                            "expr " * stack_count,
                            "load_closure " * closure,
                            "BUILD_TUPLE_1 LOAD_LAMBDA LOAD_STR ",
                            opname,
                        )

                    else:
                        rule = """
                             expr        ::= lambda_body
                             lambda_body ::= %s%s%s""" % (
                            "load_closure " * closure,
                            "LOAD_LAMBDA LOAD_STR ",
                            opname,
                        )
                    self.add_unique_rule(rule, opname, token.attr, customize)

                else:
                    rule = """
                         expr        ::= lambda_body
                         lambda_body ::= %sLOAD_LAMBDA LOAD_STR %s""" % (
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


                # This might be obsolete
                if has_get_iter_call_function1:
                    rule_pat = (
                        "generator_exp ::= %sload_genexpr %%s%s expr "
                        "GET_ITER CALL_FUNCTION_1" % ("expr " * args_pos, opname)
                    )
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
                        expr        ::= lambda_body
                        lambda_body ::= %s%sLOAD_LAMBDA %%s%s
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
                        expr        ::= lambda_body
                        lambda_body ::= %s%sLOAD_LAMBDA %%s%s
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
                pass

            # Does this go here or in full which seems more full.
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

            elif opname_base in ("UNPACK_EX",):
                before_count, after_count = token.attr
                rule = (
                    """
                        store  ::= unpack
                        unpack ::= """
                    + opname
                    + " store" * (before_count + after_count + 1)
                )
                self.addRule(rule, nop_func)

            elif opname_base == "UNPACK_SEQUENCE":
                rule = (
                    """
                    store  ::= unpack
                    unpack ::= """
                    + opname
                    + " store" * token.attr
                )
                self.addRule(rule, nop_func)

    def reduce_is_invalid(self, rule: list, ast, tokens, first: int, last: int):
        lhs = rule[0]
        n = len(tokens)
        last = min(last, n - 1)
        fn = self.reduce_check_table.get(lhs, None)
        try:
            if fn:
                return not fn(self, lhs, n, rule, ast, tokens, first, last)
        except:
            import sys, traceback

            print(
                f"Exception in {fn.__name__} {sys.exc_info()[1]}\n"
                + f"rule: {rule2str(rule)}\n"
                + f"offsets {tokens[first].offset} .. {tokens[last].offset}"
            )
            print(traceback.print_tb(sys.exc_info()[2], -1))
            raise ParserError(tokens[last], tokens[last].off2int(), self.debug["rules"])
        return False
