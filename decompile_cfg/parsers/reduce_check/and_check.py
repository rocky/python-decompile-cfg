#  Copyright (c) 2022 Rocky Bernstein
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

from decompile_cfg.scanners.tok import Token

# FIXME: this probably applies to lots of rules. Figure out a good name.
def and_ok(
    self, lhs: str, n: int, rule, ast, tokens: list, first: int, last: int
) -> bool:
    """
    Returns True if we can't find any reason to disallow an "if_exp_lambda" reduction.
    """

    # print("XXX", first, last)
    # for i in range(first, last, 1):
    #     print(tokens[i])
    # print(rule)

    if rule == ("and1", ("and_parts", "expr")):
        # Make sure jump at the end of and_parts jumps right after "expr"
        and_parts = ast[0]
        pop_jump_if_false = and_parts.last_child()
        if  pop_jump_if_false != "POP_JUMP_IF_FALSE":
            return True

        expr_node = ast[-1]
        expr_child = expr_node[0]
        if isinstance(expr_child, Token):
            last_offset = expr_child.offset
        elif expr_child == "branch_op":
            while tokens[last].optype == "pseudo":
                last -= 1
            last_offset = tokens[last].offset
        else:
            last_offset = ast[-1].last_child().offset

        i = self.offset2inst_index[last_offset]
        return pop_jump_if_false.attr > last_offset

    # print("XXX", tokens[first].basic_block, tokens[last-1].basic_block)
    return True
    # return tokens[first].basic_block == tokens[last-1].basic_block
