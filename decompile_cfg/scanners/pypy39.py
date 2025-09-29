<<<<<<< HEAD
#  Copyright (c) 2025 by Rocky Bernstein
=======
#  Copyright (c) 2021, 2025 by Rocky Bernstein
>>>>>>> python-3.6-to-3.10
"""
Python PyPy 3.9 decompiler scanner.

Does some additional massaging of xdis-disassembled instructions to
make things easier for decompilation.
"""

import decompile_cfg.scanners.scanner39 as scan

# bytecode verification, verify(), uses JUMP_OPS from here
from xdis.opcodes import opcode_39pypy as opc

JUMP_OPs = opc.JUMP_OPS


<<<<<<< HEAD
# We base this off of 3.8
class ScannerPyPy39(scan.Scanner39):
    def __init__(self, show_asm):
        # There are no differences in initialization between
        # pypy 3.8 and 3.8
=======
# We base this off of 3.9
class ScannerPyPy39(scan.Scanner39):
    def __init__(self, show_asm):
        # There are no differences in initialization between
        # pypy 3.9 and 3.9
>>>>>>> python-3.6-to-3.10
        scan.Scanner39.__init__(self, show_asm, is_pypy=True)
        self.version = (3, 9)
        self.opc = opc
        return
