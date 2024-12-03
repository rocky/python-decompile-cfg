#  Copyright (c) 2019-2024 by Rocky Bernstein
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
Isolate Python 3.10 version-specific semantic actions here.
"""

########################
# Python 3.10 changes
#######################

from spark_parser.ast import GenericASTTraversalPruningException
from decompile_cfg.semantics.consts import (
    PRECEDENCE,
)


def customize_for_version3_10(self):
    # Note there are async dictionary expressions are like await expr's
    # the below is just the default version
    self.TABLE_DIRECT.update(
        {
            "and_parts_return":
            (
                "%p and %p",
                (0,  ("expr_jifop", "or_and_part"), PRECEDENCE["and"]),
                (1,  ("expr", "and_part"), PRECEDENCE["and"]),
            ),
            "await_expr": ("await %p", (1, PRECEDENCE["await_expr"] - 1)),
            "branch_op_return": (
                "%c",
                (0, ("and_or_return", "branch_op", "or_return")),
            ),
            # 3.10 adds NOP in node[1] so we have to use -1
            # To get at the right operand of "comp_or"
            "comp_or": (
                "%p or %p",
                (0, ("comp_or", "comp_or_part"), PRECEDENCE["or"] ),
                (-1, ("comp_or", "expr", "expr_pjit"), PRECEDENCE["or"] ),
            ),

            "or_return": (
                "%c",
                (0, "or"),
            ),
            "return_expr_stmt": (
                "%c", 0,
            ),
            "yield_from": ("yield from %c", (1, "expr")),
        }
    )

    def n_await_expr(node):
        dict_comp_async = node[1][0]
        if dict_comp_async == "dict_comp_async":
            compile_mode = self.compile_mode
            self.compile_mode = "dictcomp"
            try:
                self.n_set_comp(dict_comp_async)
            except GenericASTTraversalPruningException:
                pass
            self.compile_mode = compile_mode
        else:
            self.default(node)
        self.prune()
        return

    self.n_await_expr = n_await_expr
