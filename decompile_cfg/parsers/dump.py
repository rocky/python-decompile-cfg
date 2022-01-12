#  Copyright (c) 2021-2022 Rocky Bernstein
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
"""Common grammar dump and check routine"""

def dump_and_check(p, version: tuple, modified_tokens: set, start_set: set={}) -> None:

    p.dump_grammar()
    print("=" * 50, "\n")

    p.check_grammar(ok_start_symbols=start_set)
    from xdis.version_info import PYTHON_VERSION_TRIPLE, IS_PYPY

    if PYTHON_VERSION_TRIPLE[:2] == version:
        lhs, rhs, tokens, right_recursive, dup_rhs = p.check_sets()
        from decompile_cfg.scanner import get_scanner

        s = get_scanner(PYTHON_VERSION_TRIPLE[:2], IS_PYPY)
        modified_tokens = set(
                """JUMP_BACK CONTINUE
               LOAD_GENEXPR LOAD_ASSERT LOAD_SETCOMP LOAD_DICTCOMP LOAD_CLASSNAME
               LAMBDA_MARKER RETURN_LAST
            """.split()
        )
        print("\nModified opcodes:", modified_tokens)
        opcode_set = set(s.opc.opname).union(modified_tokens)

        pseudo_tokens = set(tokens) - opcode_set
        import re

        pseudo_tokens = set([re.sub(r"_\d+$", "", t) for t in pseudo_tokens])
        pseudo_tokens = set([re.sub("_CONT$", "", t) for t in pseudo_tokens])
        pseudo_tokens = set(pseudo_tokens) - opcode_set

        print("\nPseudo tokens:")
        print(pseudo_tokens)
        import sys

        if len(sys.argv) > 1:
            from spark_parser.spark import rule2str

            for rule in sorted(p.rule2name.items()):
                print(rule2str(rule[0]))
