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


def list_if_not_seems_ok(
    self, lhs: str, n: int, rule, tree, tokens: list, first: int, last: int
) -> bool:
    """
    Returns True if "list_if_not" reduction seems okay.
    """

    # for i in range(first, last, 1):
    #    print(tokens[i])
    # print(tree)
    # print(rule)
    list_iter = tree[2]
    assert list_iter == "list_iter"
    # Since this is an "not" we must have something that doesn't assume a binary operation
    # like a "list_if_or".
    return list_iter[0].kind in ("lc_body", "comp_if_not", "list_if_not")
