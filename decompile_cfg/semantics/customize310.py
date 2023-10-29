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
Isolate Python 3.10 version-specific semantic actions here.
"""

########################
# Python 3.10 changes
#######################

from spark_parser.ast import GenericASTTraversalPruningException
from decompile_cfg.semantics.consts import (
    PRECEDENCE,
    TABLE_DIRECT,
)


def customize_for_version3_10(self):
    # Note there are async dictionary expressions are like await expr's
    # the below is just the default version
    TABLE_DIRECT.update(
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
                (0, ("branch_op", "or_return")),
            ),
            "or_return": (
                "%c",
                (0, "or"),
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
