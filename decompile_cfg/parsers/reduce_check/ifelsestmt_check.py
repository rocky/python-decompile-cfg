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

def ifelsestmt_ok(
    self, lhs: str, n: int, rule, tree, tokens: list, first: int, last: int
) -> bool:

    # print("XXX", first, last, rule)
    # for t in range(first, last): print(tokens[t])
    # print("="*40)

    # first_offset = tokens[first].off2int()

    if rule[1][2:4] == ("jf_bb_end_start", "else_suite"):

        jf_bb_end_start = tree[2]
        assert jf_bb_end_start == "jf_bb_end_start"

        # Chek that the branch at the end of the "then" goes to "endif"
        then_endif_offset = jf_bb_end_start[0].attr

        if then_endif_offset != tokens[last].offset:
            return False

    return True
