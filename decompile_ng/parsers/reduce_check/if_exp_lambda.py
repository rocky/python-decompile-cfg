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
def if_exp_lambda_ok(
    self, lhs: str, n: int, rule, ast, tokens: list, first: int, last: int
) -> bool:
    """
    Returns True if we can't find any reason to disallow an "if_exp_lambda" reduction.
    """

    # for i in range(first, last, 1):
    #    print(tokens[i])
    # print(ast)
    # print(rule)
    # print("XXX", first, last)
    # condition_expr = ast[0]
    # print(condition_expr)
    then_expr = ast[3]
    assert (
        then_expr == "expr"
    ), f'Expecting child 3 (then expression) to be "expr"; got {then_expr}"'
    return_value = ast[4]
    assert (
        return_value == "RETURN_VALUE"
    ), f"expecting child 4 to be a RETURN_VALUE; got {ast[4]}"
    return then_expr.first_child().basic_block == return_value.basic_block
