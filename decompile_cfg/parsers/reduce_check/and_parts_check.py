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

def and_parts_ok(
    self, lhs: str, n: int, rule, tree, tokens: list, first: int, last: int
) -> bool:
    """
    Returns True if we can't find any reason to disallow an "and_parts" reduction.
    """

    # print("XXX", first, last)
    # for i in range(first, last, 1):
    #     print(tokens[i])
    # print(rule)

    if lhs == "and_parts_jifop" and len(rule[1]) > 1:
        # All JUMP_IF_FALSE_OR_POP locations have to be to the same offset
        and_parts_jifop = tree[0]
        jump_if_false_or_pop1 = and_parts_jifop.last_child()
        assert jump_if_false_or_pop1 == "JUMP_IF_FALSE_OR_POP", jump_if_false_or_pop1
        and_expr = tree[1]
        assert and_expr.kind in ("and", "expr", "and_part_jifop")
        jump_if_false_or_pop2 = and_expr.last_child()
        assert jump_if_false_or_pop2 == "JUMP_IF_FALSE_OR_POP", jump_if_false_or_pop2
        return jump_if_false_or_pop1.attr == jump_if_false_or_pop1.attr
        # FIXME should we check that the jump location is not in tokes[first].offset .. tokens[last].offset?
    elif lhs == "and_parts_pjif" and len(rule[1]) > 1:
        # All POP_JUMP_IF_FALSE locations have to be to the same offset
        # FIXME: do something similar to the above
        pass

    return True
