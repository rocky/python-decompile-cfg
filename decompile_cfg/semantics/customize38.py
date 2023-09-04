#  Copyright (c) 2019-2023 by Rocky Bernstein
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
"""Isolate Python 3.8 version-specific semantic actions here.
"""

import re

########################
# Python 3.8 changes
#######################

from decompile_cfg.semantics.consts import PRECEDENCE, TABLE_DIRECT
from decompile_cfg.semantics.customize37 import FSTRING_CONVERSION_MAP
from decompile_cfg.semantics.helper import escape_string, strip_quotes


def customize_for_version3_8(self):

    # FIXME: pytest doesn't add proper keys in testing. Reinstate after we have fixed pytest.
    # for lhs in 'for forelsestmt forelselaststmt '
    #             'forelselaststmtc tryfinally38'.split():
    #     del TABLE_DIRECT[lhs]

    TABLE_DIRECT.update(
        {
            "and_compare_chained_return": (
                "%c %c",
                (0, "and_parts"),
                (1, "compare_chained_middle_return"),
            ),
            "async_for_stmt38": (
                "%|async for %c in %c:\n%+%c%-%-\n\n",
                (2, "store"),
                (0, "expr"),
                (3, "for_block"),
            ),
            "async_forelse_stmt38": (
                "%|async for %c in %c:\n%+%c%-%|else:\n%+%c%-\n\n",
                (2, "store"),
                (0, "expr"),
                (3, "for_block"),
                (6, "else_suite"),
            ),
            "async_with_stmt38": (
                "%|async with %c:\n%+%c%-\n",
                (0, "expr"),
                7),
            "async_with_as_stmt38": (
                "%|async with %c as %c:\n%+%|%c%-",
                (0, "expr"),
                (6, "store"),
                (7, "suite_stmts"),
            ),
            "c_forelsestmt38": (
                "%|for %c in %c:\n%+%c%-%|else:\n%+%c%-\n\n",
                (2, "store"),
                (0, "expr"),
                (3, "for_block"),
                -1,
            ),
            "c_tryfinallystmt38": (
                "%|try:\n%+%c%-%|finally:\n%+%c%-\n\n",
                (1, "c_suite_stmts_opt"),
                (-2, "c_suite_stmts_opt"),
            ),
            "except_cond1a": (
                "%|except %c:\n",
                (1, "expr"),
            ),
            "except_cond_as": (
                "%|except %c as %c:\n",
                (1, "expr"),
                (-2, "STORE_FAST"),
            ),
            "except_handler38": ("%c", (2, "except_stmts")),
            "except_handler38a": ("%c", (-2, "stmts")),
            "except_handler38c": (
                "%c%+%c%-",
                (1, "except_cond1a"),
                (2, "except_stmts"),
            ),
            "except_handler_as": (
                "%c%+\n%+%c%-",
                (1, "except_cond_as"),
                (2, "tryfinallystmt"),
            ),
            "except_ret38a": ("return %c", (4, "expr")),
            # Note: there is a suite_stmts_opt which seems
            # to be bookkeeping which is not expressed in source code
            "except_ret38": ("%|return %c\n", (1, "expr")),
            "for38": (
                "%|for %c in %c:\n%+%c%-\n\n",
                (2, "store"),
                (0, "expr"),
                (3, "for_block"),
            ),
            "forelsestmt38": (
                "%|for %c in %c:\n%+%c%-%|else:\n%+%c%-\n\n",
                (2, "store"),
                (0, "expr"),
                (3, "for_block"),
                -1,
            ),
            "forelselaststmt38": (
                "%|for %c in %c:\n%+%c%-%|else:\n%+%c%-",
                (2, "store"),
                (0, "expr"),
                (3, "for_block"),
                -2,
            ),
            "forelselaststmtc38": (
                "%|for %c in %c:\n%+%c%-%|else:\n%+%c%-\n\n",
                (2, "store"),
                (0, "expr"),
                (3, "for_block"),
                -2,
            ),
            "if_exp_and_return": (
                "%c if %p and %p else %c\n",
                (2, "return_expr"),
                (0, "expr_pjif", PRECEDENCE["if_exp"]),
                (1, "expr_pjif", PRECEDENCE["and"]),
                (3, "return_expr"),
            ),
            "ifpoplaststmtc": ("%|if %c:\n%+%c%-", (0, "testexpr"), (2, "c_stmts")),
            "pop_return": ("%|return %c\n", (1, "return_expr")),
            "popb_return": ("%|return %c\n", (0, "return_expr")),
            "pop_ex_return": ("%|return %c\n", (0, "return_expr")),
            "set_for": (
                " for %c in %c",
                (2, "store"),
                (0, "expr_or_arg"),
            ),
            "whilestmt38": (
                "%|while %c:\n%+%c%-\n\n",
                (1, ("bool_op", "testexpr", "testexpr")),
                (2, ("c_stmts", "pass")),
            ),
            "whileTruestmt38": (
                "%|while True:\n%+%c%-\n\n",
                (1, "c_stmts", "pass"),
            ),
            "try_elsestmtl38": (
                "%|try:\n%+%c%-%c%|else:\n%+%c%-",
                (1, "suite_stmts_opt"),
                (3, "except_handler38"),
                (5, "else_suitec"),
            ),
            "try_except38": (
                "%|try:\n%+%c\n%-%|except:\n%+%c%-\n\n",
                (2, ("suite_stmts_opt", "suite_stmts")),
                (3, ("except_handler38a", "except_handler38b", "except_handler38c")),
            ),
            "try_except38r": (
                "%|try:\n%+%c\n%-%|except:\n%+%c%-\n\n",
                (1, "return_except"),
                (2, "except_handler38b"),
            ),
            "try_except38r2": (
                "%|try:\n%+%c\n%-%|except:\n%+%c%c%-\n\n",
                (1, "suite_stmts_opt"),
                (8, "cond_except_stmts_opt"),
                (10, "return"),
            ),
            "try_except38r4": (
                "%|try:\n%+%c\n%-%|except:\n%+%c%c%-\n\n",
                (1, "returns_in_except"),
                (3, "except_cond1"),
                (4, "return"),
            ),
            "try_except_as": (
                "%|try:\n%+%c%-\n%|%-%c\n\n",
                (
                    -4,
                    ("suite_stmts", "_stmts"),
                ),  # Go from the end because of POP_BLOCK variation
                (-3, "except_handler_as"),
            ),
            "try_except_ret38": (
                "%|try:\n%+%c%-\n%|except:\n%+%|%c%-\n\n",
                (1, "returns"),
                (2, "except_ret38a"),
            ),
            "try_except_ret38a": (
                "%|try:\n%+%c%-%c\n\n",
                (1, "returns"),
                (2, "except_handler38c"),
            ),
            "tryfinally38rstmt": (
                "%|try:\n%+%c%-%|finally:\n%+%c%-\n\n",
                (0, "sf_pb_call_returns"),
                (-1, ("ss_end_finally", "suite_stmts", "_stmts")),
            ),
            "tryfinally38rstmt2": (
                "%|try:\n%+%c%-%|finally:\n%+%c%-\n\n",
                (4, "returns"),
                -2,
                "ss_end_finally",
            ),
            "tryfinally38rstmt3": (
                "%|try:\n%+%|return %c%-\n%|finally:\n%+%c%-\n\n",
                (1, "expr"),
                (-1, "ss_end_finally"),
            ),
            "tryfinally38rstmt4": (
                "%|try:\n%+%c%-\n%|finally:\n%+%c%-\n\n",
                (1, "suite_stmts_opt"),
                (5, "suite_stmts_return"),
            ),
            "tryfinally38stmt": (
                "%|try:\n%+%c%-%|finally:\n%+%c%-\n\n",
                (1, "suite_stmts_opt"),
                (6, "suite_stmts_opt"),
            ),
            "tryfinally38astmt": (
                "%|try:\n%+%c%-%|finally:\n%+%c%-\n\n",
                (2, "suite_stmts_opt"),
                (8, "suite_stmts_opt"),
            ),
            "named_expr": (  # AKA "walrus operator"
                "%c := %p",
                (2, "store"),
                (0, "expr", PRECEDENCE["named_expr"] - 1),
            ),
        }
    )

    def gen_function_parens_adjust(mapping_key, node):
        """If we can avoid the outer parenthesis
        of a generator function, set the node key to
        'call_generator' and the caller will do the default
        action on that. Otherwise we do nothing.
        """
        if mapping_key.kind != "CALL_FUNCTION_1":
            return

        args_node = node[-2]
        if args_node == "pos_arg":
            assert args_node[0] == "expr"
            n = args_node[0][0]
            if n == "generator_exp":
                node.kind = "call_generator"
            pass
        return

    def n_except_return_value(node):
        if node[0] == "POP_BLOCK":
            self.default(node[1])
        else:
            self.template_engine(("%|return %c\n", (0, "expr")), node)
        self.prune()

    self.n_except_return_value = n_except_return_value

    # FIXME: now that we've split out cond_except_stmt,
    # we should be able to get this working as a pure transformation rule,
    # so no procedure is needed here.
    def try_except38r3(node):
        self.template_engine(("%|try:\n%+%c\n%-", (1, "suite_stmts_opt")), node)
        cond_except_stmts_opt = node[5]
        assert cond_except_stmts_opt == "cond_except_stmts_opt"
        for child in cond_except_stmts_opt:
            if child == "cond_except_stmt":
                if child[0] == "except_cond1":
                    self.template_engine(
                        ("%c\n", (0, "except_cond1"), (1, "expr")), child
                    )
                    self.template_engine(("%+%c%-\n", (1, "except_stmts")), child)
                pass
            pass
        self.template_engine(("%+%c%-\n", (7, "return")), node)
        self.prune()

    self.n_try_except38r3 = try_except38r3

    def n_call(node):
        p = self.prec
        self.prec = 100
        mapping = self._get_mapping(node)
        table = mapping[0]
        key = node
        for i in mapping[1:]:
            key = key[i]
            pass
        opname = key.kind
        if opname.startswith("CALL_FUNCTION_VAR_KW"):
            # Python 3.5 changes the stack position of
            # *args: kwargs come after *args whereas
            # in earlier Pythons, *args is at the end
            # which simplifies things from our
            # perspective.  Python 3.6+ replaces
            # CALL_FUNCTION_VAR_KW with
            # CALL_FUNCTION_EX We will just swap the
            # order to make it look like earlier
            # Python 3.
            entry = table[key.kind]
            kwarg_pos = entry[2][1]
            args_pos = kwarg_pos - 1
            # Put last node[args_pos] after subsequent kwargs
            while node[kwarg_pos] == "kwarg" and kwarg_pos < len(node):
                # swap node[args_pos] with node[kwargs_pos]
                node[kwarg_pos], node[args_pos] = node[args_pos], node[kwarg_pos]
                args_pos = kwarg_pos
                kwarg_pos += 1
        elif opname.startswith("CALL_FUNCTION_VAR"):
            # CALL_FUNCTION_VAR's top element of the stack contains
            # the variable argument list, then comes
            # annotation args, then keyword args.
            # In the most least-top-most stack entry, but position 1
            # in node order, the positional args.
            argc = node[-1].attr
            nargs = argc & 0xFF
            kwargs = (argc >> 8) & 0xFF
            # FIXME: handle annotation args
            if nargs > 0:
                template = ("%c(%P, ", 0, (1, nargs + 1, ", ", 100))
            else:
                template = ("%c(", 0)
            self.template_engine(template, node)

            args_node = node[-2]
            if args_node in ("pos_arg", "expr"):
                args_node = args_node[0]
            if args_node == "build_list_unpack":
                template = ("*%P)", (0, len(args_node) - 1, ", *", 100))
                self.template_engine(template, args_node)
            else:
                if len(node) - nargs > 3:
                    template = (
                        "*%c, %P)",
                        nargs + 1,
                        (nargs + kwargs + 1, -1, ", ", 100),
                    )
                else:
                    template = ("*%c)", nargs + 1)
                self.template_engine(template, node)
            self.prec = p
            self.prune()
        elif (
            opname.startswith("CALL_FUNCTION_1")
            and opname == "CALL_FUNCTION_1"
            or not re.match(r"\d", opname[-1])
        ):
            n0 = node[0][0] if node[0] == "arg" else node[0]
            template = "(\n%+%|%c%-\n)(%p)" if n0[0] == "lambda_body" else "%c(%p)"
            self.template_engine(
                (template, (0, ("expr", "arg")), (1, PRECEDENCE["yield"] - 1)), node
            )
            self.prec = p
            self.prune()
        else:
            gen_function_parens_adjust(key, node)

        self.prec = p
        self.default(node)

    self.n_call = n_call
    def n_call_ex_kw2(node):
        """Handle CALL_FUNCTION_EX 2  (have KW) but with
        BUILD_{MAP,TUPLE}_UNPACK_WITH_CALL"""

        assert node[1] == "build_tuple_unpack_with_call"
        value = self.format_pos_args(node[1])
        if value == "":
            fmt = "%c(%p)"
        elif isinstance(value, tuple):
            str_value = str(value)[1:-1]
            if len(value) == 1:
                # There is a comma at the end
                fmt = "%%c(%s %%p)" % str_value
            else:
                fmt = "%%c(%s, %%p)" % str_value
        else:
            fmt = "%%c(%s, %%p)" % value

        self.template_engine(
            (fmt, (0, "expr"), (2, "build_map_unpack_with_call", 100)), node
        )

        self.prune()

    self.n_call_ex_kw2 = n_call_ex_kw2

    def call_ex_kw3(node):
        """Handle CALL_FUNCTION_EX 1 (have KW) but without
        BUILD_MAP_UNPACK_WITH_CALL"""
        self.preorder(node[0])
        self.write("(")

        value = self.format_pos_args(node[1][0])
        if value == "":
            pass
        elif isinstance(value, tuple):
            str_value = str(value)[1:-1]
            if len(value) == 1:
                # There is a comma at the end
                fmt = "%%c(%s %%p)," % str_value
            else:
                fmt = "%%c(%s, %%p)," % str_value
            self.template_engine(
                (fmt, (0, "expr"), (2, "build_map_unpack_with_call", 100)), node
                )
        else:
            self.write(value)
            self.write(", ")

        self.write("*")
        self.preorder(node[1][1])
        self.write(", ")

        kwargs = node[2]
        if kwargs == "expr":
            kwargs = kwargs[0]
        if kwargs == "expr" and kwargs[0] != "dict":
            self.call36_dict(kwargs)
        else:
            self.write("**")
            self.preorder(kwargs)
        self.write(")")
        self.prune()

    self.n_call_ex_kw3 = call_ex_kw3

    def n_list_afor(node):
        if len(node) == 2:
            # list_afor ::= get_iter list_afor
            self.comprehension_walk_newer(node, 0)
        else:
            list_iter_index = 2 if node[2] == "list_iter" else 3
            self.template_engine(
                (
                    " async for %[1]{%c} in %c%[1]{%c}",
                    (1, "store"),
                    (0, "get_aiter"),
                    (list_iter_index, "list_iter"),
                ),
                node,
            )
        self.prune()

    self.n_list_afor = n_list_afor

    def n_set_afor(node):
        if len(node) == 2:
            self.template_engine(
                (" async for %[1]{%c} in %c", (1, "store"), (0, "get_aiter")), node
            )
        else:
            self.template_engine(
                " async for %[1]{%c} in %c%c",
                (1, "store"),
                (0, "get_aiter"),
                (2, "set_iter"),
            )
        self.prune()

    self.n_set_afor = n_set_afor

    # def n_set_comp(node):
    #     self.write("{")
    #     self.comprehension_walk_newer(node, iter_index=1, collection_node=0)
    #     self.prune()
    #     self.write("}")

    # self.n_set_comp = n_set_comp

    def n_formatted_value_debug(node):
        p = self.prec
        self.prec = 100

        formatted_value = node[1]
        value_equal = node[0].attr
        assert formatted_value.kind.startswith("formatted_value")
        old_in_format_string = self.in_format_string
        self.in_format_string = formatted_value.kind
        format_value_attr = node[-1]

        post_str = ""
        if node[-1] == "BUILD_STRING_3":
            post_load_str = node[-2]
            post_str = self.traverse(post_load_str, indent="")
            post_str = strip_quotes(post_str)

        if format_value_attr == "FORMAT_VALUE_ATTR":
            attr = format_value_attr.attr
            if attr & 4:
                fmt = strip_quotes(self.traverse(node[3], indent=""))
                attr_flags = attr & 3
                if attr_flags:
                    conversion = "%s:%s" % (
                        FSTRING_CONVERSION_MAP.get(attr_flags, ""),
                        fmt,
                    )
                else:
                    conversion = ":%s" % fmt
            else:
                conversion = FSTRING_CONVERSION_MAP.get(attr, "")
            f_str = "f%s" % escape_string(
                "{%s%s}%s" % (value_equal, conversion, post_str)
            )
        else:
            f_conversion = self.traverse(formatted_value, indent="")
            # Remove leaving "f" and quotes
            conversion = strip_quotes(f_conversion[1:])
            f_str = "f%s" % escape_string(f"{value_equal}{conversion}" + post_str)

        self.write(f_str)
        self.in_format_string = old_in_format_string

        self.prec = p
        self.prune()

    self.n_formatted_value_debug = n_formatted_value_debug

    def n_suite_stmts_return(node):
        if len(node) > 1:
            assert len(node) == 2
            self.template_engine(
                ("%c\n%|return %c", (0, ("_stmts", "suite_stmts")), (1, "expr")), node
            )
        else:
            self.template_engine(("%|return %c", (0, "expr")), node)
        self.prune()

    self.n_suite_stmts_return = n_suite_stmts_return
