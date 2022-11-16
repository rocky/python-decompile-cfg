#  Copyright (c) 2019, 2021-2022 by Rocky Bernstein
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
"""Python 3.10 bytecode decompiler scanner.

Does some token massaging of xdis-disassembled instructions to make
things easier for decompilation.

This sets up opcodes Python's 3.9.
"""

# bytecode verification, verify(), uses JUMP_OPs from here
from xdis.opcodes import opcode_38 as opc

from decompile_cfg.scanners.scanner38 import Scanner38Base

# bytecode verification, verify(), uses JUMP_OPS from here
JUMP_OPs = opc.JUMP_OPS


class Scanner39(Scanner38Base):
    def __init__(self, show_asm=None, debug=False, is_pypy=False):
        Scanner38Base.__init__(self, (3, 9), show_asm, is_pypy)
        self.debug = debug
        return

    pass

    # def ingest(self, bytecode, classname=None, code_objects={}, show_asm=None) -> tuple:
    #     """
    #     Create "tokens" the bytecode of an Python code object. See doc in parent class.
    #     """
    #     tokens, customize = super(Scanner39, self).ingest(
    #         bytecode, classname, code_objects, show_asm
    #     )


if __name__ == "__main__":
    from xdis.version_info import PYTHON_VERSION_TRIPLE, version_tuple_to_str

    if PYTHON_VERSION_TRIPLE[:2] == (3, 9):
        import inspect

        co = inspect.currentframe().f_code  # type: ignore
        tokens, customize = Scanner39().ingest(co)
        for t in tokens:
            print(t.format())
        pass
    else:
        print(
            f"Need to be Python 3.9 to demo; I am version {version_tuple_to_str()}."
        )
