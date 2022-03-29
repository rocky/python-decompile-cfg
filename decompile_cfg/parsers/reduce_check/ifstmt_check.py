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

def ifstmt_ok(
    self, lhs: str, n: int, rule, tree, tokens: list, first: int, last: int
) -> bool:

    # print("XXX", first, last, rule)
    # for t in range(first, last): print(tokens[t])
    # print("="*40)

    # first_offset = tokens[first].off2int()

    if rule[1][0] == "testexpr":

        testexpr = tree[0]
        assert testexpr == "testexpr"

        testexpr_end = testexpr.last_child()

        if not isinstance(testexpr_end, Token):
            # No branch at end, so not an "ifstmt"
            return False

        # Check that the branch at the end of the "then" goes to "endif"
        then_endif_offset = testexpr_end.attr

        # print(f"XXX then jump: {then_endif_offset}, tokens[last] offset: {tokens[last].offset}")
        if then_endif_offset != tokens[last].offset:
            # print("XXX", first, last, rule)
            # for t in range(first, last): print(tokens[t])
            # print("="*40)
            return False

    return True
