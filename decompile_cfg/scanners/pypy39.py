#  Copyright (c) 2025 by Rocky Bernstein
"""
Python PyPy 3.9 decompiler scanner.

Does some additional massaging of xdis-disassembled instructions to
make things easier for decompilation.
"""

import decompile_cfg.scanners.scanner39 as scan

# bytecode verification, verify(), uses JUMP_OPS from here
from xdis.opcodes import opcode_39pypy as opc

JUMP_OPs = opc.JUMP_OPS


# We base this off of 3.8
class ScannerPyPy39(scan.Scanner39):
    def __init__(self, show_asm):
        # There are no differences in initialization between
        # pypy 3.8 and 3.8
        scan.Scanner39.__init__(self, show_asm, is_pypy=True)
        self.version = (3, 9)
        self.opc = opc
        return
