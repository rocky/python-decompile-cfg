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
"""
Isolate Python 3.9 version-specific semantic actions here.
"""

########################
# Python 3.9 changes
#######################

from decompile_cfg.parsers.treenode import SyntaxTree
from decompile_cfg.semantics.consts import INDENT_PER_LEVEL, PRECEDENCE, TABLE_DIRECT
from decompile_cfg.semantics.helper import flatten_list


def customize_for_version3_9(self):
    # fmt: off
    PRECEDENCE["call_ex_3_9"] = 1
    PRECEDENCE["and2"]       = PRECEDENCE["and"]
    # fmt: on

    TABLE_DIRECT.update(
        {
            "and2": (
                "%p and %p",
                (0, ("and_parts_jifop", "and_parts_jifops"), PRECEDENCE["and"]),
                (2, ("and", "expr"), PRECEDENCE["and"]),
            ),
        }
    )

    def n_call_ex_3_9(node):
        """Handle CALL_FUNCTION_EX when there are positional arguments"""

        # Format call function name
        call_fn_name = node[0]
        self.preorder(call_fn_name)
        self.write("(")

        star_args = node[2]

        star_star_kwargs = None

        # Format positional args
        positional_args = node[1]
        self.template_engine(("%P", (0, -1, ", ", 100)), positional_args)
        trailing_comma = False

        # Format keyword args if it exists
        keyword_args = node[-4]
        if keyword_args[0] != "BUILD_MAP_0":
            self.write(", ")
            self.call36_dict(keyword_args)
            self.write(", ")
            trailing_comma = True

        # Format *args if it exists
        if star_args is not None:
            if trailing_comma is False:
                self.write(", ")
            self.write("*")
            self.preorder(star_args)
            trailing_comma = False

        # Format **kwargs if it exists

        CALL_FUNCTION_EX = node[-1]
        assert CALL_FUNCTION_EX == "CALL_FUNCTION_EX"

        # If the lowest bit of the flags of CALL_FUNCTION_EX (node[-1])
        # are set the there is a mapping object containing additional
        # keyword object.
        if CALL_FUNCTION_EX.attr & 1:
            star_star_kwargs = node[-3]

        if star_star_kwargs:
            if not trailing_comma:
                self.write(", ")
            self.write("**")
            self.preorder(star_star_kwargs)

        self.write(")")
        self.prune()

    self.n_call_ex_3_9 = n_call_ex_3_9

    def call_ex0_3_9(node):
        """Handle CALL_FUNCTION_EX when there are no positional arguments"""
        # Format call function name
        call_fn_name = node[0]
        self.preorder(call_fn_name)
        self.write("(")

        seen_arg = False
        first_child = node[1].first_child()
        if self.version < (3, 10):
            star_args = None if first_child == "BUILD_TUPLE_0" else node[1]
        else:
            star_args = (
                None
                if first_child == "LOAD_CONST" and first_child.attr == tuple()
                else node[1]
            )

        star_star_kwargs = None

        # Format keyword args if it exists
        keyword_args = node[-4]
        if keyword_args[0] != "BUILD_MAP_0":
            self.call36_dict(keyword_args)
            self.write(", ")

        # Format *args if it exists
        if star_args is not None:
            if seen_arg:
                self.write(", ")
            self.write("*")
            self.preorder(star_args)
            seen_arg = True

        # Format **kwargs if it exists

        CALL_FUNCTION_EX = node[-1]
        assert CALL_FUNCTION_EX == "CALL_FUNCTION_EX"

        # If the lowest bit of the flags of CALL_FUNCTION_EX (node[-1])
        # are set the there is a mapping object containing additional
        # keyword object.
        if CALL_FUNCTION_EX.attr & 1:
            star_star_kwargs = node[-3]

        if star_star_kwargs:
            if seen_arg:
                self.write(", ")
            self.write("**")
            self.preorder(star_star_kwargs)

        self.write(")")
        self.prune()

    self.n_call_ex0_3_9 = call_ex0_3_9

    def call_ex1_3_9(node):
        """
        Handle CALL_FUNCTION_EX when there positional arguments and no keyword arguments
        """

        # Format call function name
        call_fn_name = node[0]
        self.preorder(call_fn_name)
        self.write("(")

        seen_arg = False
        star_args = node[2]

        star_star_kwargs = None

        # Format positional args
        seen_arg = True
        positional_args = node[1]
        self.template_engine(("%P", (0, -1, ", ", 100)), positional_args)

        # Format *args if it exists
        if star_args is not None:
            if seen_arg:
                self.write(", ")
            self.write("*")
            self.preorder(star_args)
            seen_arg = True

        # Format **kwargs if it exists

        CALL_FUNCTION_EX = node[-1]
        assert CALL_FUNCTION_EX == "CALL_FUNCTION_EX"

        # If the lowest bit of the flags of CALL_FUNCTION_EX (node[-1])
        # are set the there is a mapping object containing additional
        # keyword object.
        if CALL_FUNCTION_EX.attr & 1:
            star_star_kwargs = node[-3]

        if star_star_kwargs:
            if seen_arg:
                self.write(", ")
            self.write("**")
            self.preorder(star_star_kwargs)

        self.write(")")
        self.prune()

    self.n_call_ex1_3_9 = call_ex1_3_9

    def n_list(node: SyntaxTree):
        """
        prettyprint a dict, list, set or tuple.
        """
        p = self.prec

        if len(node) == 1:
            lastnode = node[0]
            flat_elems = []
        else:
            self.prec = PRECEDENCE["yield"] - 1
            lastnode = node.pop()
            flat_elems = flatten_list(node)

        lastnodetype = lastnode.kind

        if lastnodetype.startswith("BUILD_LIST") or lastnodetype == "expr":
            self.write("[")
            endchar = "]"

        elif lastnodetype.startswith("BUILD_SET"):
            self.write("{")
            endchar = "}"

        elif lastnodetype.startswith("BUILD_TUPLE") or node == "tuple":
            # Tuples can appear places that can NOT
            # have parenthesis around them, like array
            # subscripts. We check for that by seeing
            # if a tuple item is some sort of slice.
            no_parens = False
            for n in node:
                if n == "arg":
                    n = n[0]
                if n == "expr" and n[0].kind.startswith("slice"):
                    no_parens = True
                    break
                pass
            if no_parens:
                endchar = ""
            else:
                self.write("(")
                endchar = ")"
                pass

        elif lastnodetype == "list_unpack":
            if lastnode[-1].attr == 1:
                # LIST_EXTEND says there is item in the expr art of lastnode.
                expr = lastnode[1]
                assert expr == "expr"
                value = self.traverse(expr)
                if value.startswith("(") and value.endswith(")"):
                    # Change tuple delimiters from [...] to (...)
                    value = f"[{value[1:-1]}]"
                    self.write(value)
                    endchar = ""
                elif value.startswith("[") and value.endswith("]"):
                    self.write(value)
                    endchar = ""
                else:
                    raise TypeError("Internal Error: not implemented yet")

            else:
                self.write("[")
                endchar = "]"
                raise TypeError("Internal Error: not implemented yet")
        elif lastnodetype.startswith("ROT_TWO"):
            self.write("(")
            endchar = ")"

        elif lastnodetype == "LIST_EXTEND":
            if node[0] == "expr":
                node = node[0]
            flat_elems = []
            constant_node = node[0]
            if constant_node == "constant" and isinstance(constant_node[0].attr, tuple):
                self.write("[")
                endchar = "]"
                self.write(", ".join(str(i) for i in constant_node[0].attr))
            else:
                raise TypeError(
                    "Internal Error: n_build_list expects list, tuple, set, or unpack, "
                    "or LIST_EXTEND"
                )
        else:
            raise TypeError(
                "Internal Error: n_build_list expects list, tuple, set, or unpack, "
                "or LIST_EXTEND"
            )

        self.indent_more(INDENT_PER_LEVEL)
        sep = ""
        for elem in flat_elems:
            if elem in ("ROT_THREE", "EXTENDED_ARG"):
                continue
            assert elem in (
                "expr",
                "arg",
                "list",
                "lists",
                "branch_op",
                "constant",
                "LOAD_CONST",
            )
            line_number = self.line_number
            value = self.traverse(elem)
            if line_number != self.line_number:
                sep += "\n" + self.indent + INDENT_PER_LEVEL[:-1]
            else:
                if sep != "":
                    sep += " "
            self.write(sep, value)
            sep = ","
        if lastnodetype.startswith("BUILD_TUPLE") and lastnode.attr == 1:
            self.write(",")
        self.write(endchar)
        self.indent_less(INDENT_PER_LEVEL)
        self.prec = p
        self.prune()
        return

    self.n_set = self.n_build_set = self.n_tuple = self.n_list = n_list

    def n_tuple_list_starred(node: SyntaxTree):
        lists = node[1]
        assert lists == "lists"
        last_sep = "*"
        for elem in lists:
            self.write(last_sep)
            value = self.traverse(elem)
            if value.startswith("(") and value.endswith(")"):
                # Change tuple delimiters from [...] to (...)
                value = f"[{value[1:-1]}]"
            self.write(value)
            last_sep = ", *"
        self.prune()
    self.n_tuple_list_starred  = n_tuple_list_starred
