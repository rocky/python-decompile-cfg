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
def comp_if_ok(
    self, lhs: str, n: int, rule, tree, tokens: list, first: int, last: int
) -> bool:
    """
    Rules for both "comp_if " and "comp_if_not".

    Returns true if the jump loop parity (true false) matches the parity on the "if"
    """


    # We need this  reduction rule to disambiguate
    # these "comp_if_not" and "comp_if". The difference is burried in the
    # sense of the jump in
    #     comp_iter -> comp_if_or -> or_parts_false_loop
    # vs.:
    #    comp_iter -> comp_if_or -> or_parts_true_loop
    #
    # If "true_loop then that goes with "comp_if_not"
    # if "false_loop"  then that goes with comp_if"
    #
    # We might be able to do this in the grammar but it is a bit
    # too pervasive and involved.

    # for i in range(first, last, 1):
    #    print(tokens[i])
    # print(tree)
    # print(rule)

    if rule[1] != ("expr", "pjump_ift", "comp_iter"):
        # We only handle RHS with the above
        return True

    comp_iter = tree[-1]
    assert comp_iter == "comp_iter"

    comp_if_or = comp_iter[0]
    if comp_if_or != "comp_if_or":
        return True

    # If "or" fails and we jump to the loop we have an "if" condition.
    if lhs == "comp_if" and comp_if_or[0].kind.endswith("true_loop"):
        return False

    # If "or" succeeds and we jump to the loop we have an "if not" condition.
    if lhs == "comp_if_not" and comp_if_or[0].kind.endswith("false_loop"):
        return False

    return True


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
