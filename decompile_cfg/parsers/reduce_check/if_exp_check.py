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
def if_exp_ok(
    self, lhs: str, n: int, rule, tree, tokens: list, first: int, last: int
) -> bool:
    """
    Returns True if we can't find any reason to disallow an "if_exp_lambda" reduction.
    """

    # for i in range(first, last, 1):
    #    print(tokens[i])
    # print(tree)
    # print(rule)
    if tree[0].kind.startswith("if_exp_jump_"):
        tree = tree[0]

    test_pji = tree[1]
    assert test_pji.kind.startswith("POP_JUMP_IF_")
    orelse_expr = tree[6]
    assert orelse_expr == "expr"

    # Make "if" test conditional jump goes to the "orelse" location.
    if test_pji.attr != orelse_expr.first_child().offset:
        return False

    body_expr = tree[3]
    assert body_expr == "expr"

    if body_expr[0] == "branch_op":

        # Make sure all jumps in body_expr don't jump into
        # the middle of the orelse part.
        offset = body_expr.first_child().offset
        jump_forward = tree[4]
        assert jump_forward == "JUMP_FORWARD"
        jf_offset = jump_forward.offset
        last_offset = tokens[last].offset
        i = self.offset2inst_index[offset]
        inst = self.insts[i]

        while inst.offset < jf_offset:
            if inst.optype == "jabs" and jf_offset <= inst.argval <= last_offset:
                return False
            i += 1
            inst = self.insts[i]
            pass
        pass
    return True
