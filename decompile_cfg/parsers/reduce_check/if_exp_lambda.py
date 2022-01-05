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
    return_expr_lambda = ast[-1]
    assert (
        return_expr_lambda == "return_expr_lambda"
    ), f'Expecting last child to be "return_expr_lambda"; got {return_expr_lambda}"'
    return return_expr_lambda.first_child().basic_block == tokens[last-1].basic_block
