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


# FIXME: this probably applies to lots of rules. Figure out a good name.
def or_check(
    self, lhs: str, n: int, rule, ast, tokens: list, first: int, last: int
) -> bool:

    # for i in range(first, last, 1):
    #     print(tokens[i])
    # print(ast)
    # print("DOMS", tokens[first].dominator.bb.number, tokens[last].dominator.bb.number)
    while tokens[first] != "DOM_START":
        first += 1
    while tokens[last+1] != "DOM_START":
        last += 1
    return tokens[first].dominator == tokens[last].dominator
