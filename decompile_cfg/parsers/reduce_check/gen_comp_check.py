#  Copyright (c) 2023 Rocky Bernstein
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

def gen_comp_ok(
    self, lhs: str, n: int, rule, tree, tokens: list, first: int, last: int
) -> bool:
    """
    Returns True if gen_comp_func is valid.

    Basically ensures that the instruction before is not a "BUILD_xxx_0"
    """

    # print("XXX", first, last)
    # for i in range(first, last, 1):
    #     print(tokens[i])
    # print(rule)

    return tokens[first - 1].kind not in (
        "BUILD_LIST_0",
        "BUILD_MAP_0",
        "BUILD_SET_0"
    )
