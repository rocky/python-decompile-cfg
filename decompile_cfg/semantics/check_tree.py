#  Copyright (c) 2019, 2022 Rocky Bernstein
#
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
"""
Python parse tree checker.

Our rules sometimes give erroneous results. Until we have perfect rules,
This checker will catch mistakes in decompilation we've made.

FIXME idea: extend parsing system to do same kinds of checks or nonterminal
before reduction and don't reduce when there is a problem.
"""

def is_loop_node(node) -> bool:
    return (
        node.kind.startswith("while")
        or node.kind.startswith("async_for")
        or node.kind.startswith("for")
    )


def checker(tree, in_loop: bool, errors, loop_node=None) -> None:
    """
    Check subtree for sanity:
       - breaks/continue outside of loops.
       - augmented assigns inside an expression

    Mark loop nodes and whether they contain a "break"
    statement not nested in some other loop.
    Loops without a "break" will  be considered for removal of
    the "else" clause if that exists. For example
    "for ... else ..." can be turned into "for ..."
    In Python 3.8 and higher code for these can be identical.
    """

    if tree is None:
        return

    tree.is_loop_node = is_loop_node(tree)
    if tree.is_loop_node:
        loop_node = tree
        loop_node.has_break = False

    in_loop = tree.is_loop_node or (
        tree.kind.startswith("while")
        or tree.kind.startswith("async_for")
        or tree.kind.startswith("for")
    )
    if tree.kind in ("aug_assign1", "aug_assign2") and tree[0][0] == "and":
        text = str(tree)
        error_text = (
            "\n# improper augmented assigment (e.g. +=, *=, ...):\n#\t"
            + "\n# ".join(text.split("\n"))
            + "\n"
        )
        errors.append(error_text)

    for node in tree:
        if node.kind in ("continue", "break"):
            if node.kind == "break":
                loop_node.has_break = True
            if not in_loop:
                text = str(node)
                error_text = "\n# not in loop:\n#\t" + "\n# ".join(text.split("\n"))
                errors.append(error_text)
        if hasattr(node, "__repr1__"):
            checker(node, in_loop, errors, loop_node)
