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

        last_child = testexpr.last_child()

        # Check that the branch at the end of the "then" goes to "endif"
        i = self.offset2inst_index[last_child.offset]
        inst = self.insts[i]

        last_inst = tokens[last]
        last_offset = last_inst.offset
        if last_inst == "BB_END":
            # We make use of the fact that in 3.6+
            # "bytecode" is "wordcode "or all instructions
            # are two bytes.
            last_offset += 2

        if inst.opname == "BB_END":
            inst = self.insts[i-1]

        if inst.optype != "jabs":
            return False
        then_endif_offset = inst.argval

        # print(f"XXX then jump: {then_endif_offset}, tokens[last] offset: {tokens[last].offset}")
        if then_endif_offset != last_offset:
            # print("XXX", first, last, rule)
            # for t in range(first, last): print(tokens[t])
            # print("="*40)
            return False

    return True
