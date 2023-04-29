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

from decompile_cfg.semantics.consts import PRECEDENCE, TABLE_DIRECT


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
        star_args = None if first_child == "BUILD_TUPLE_0" else node[1]

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
