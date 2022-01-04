#!/usr/bin/env python
import sys
if len(sys.argv) != 2:
    print("Usage: compile-file.py *Python-file*")
    sys.exit(1)
source = sys.argv[1]

assert source.endswith('.py')
basename = source[:-3]

from xdis.version_info import version_tuple_to_str
version = version_tuple_to_str(end=2)
bytecode = "%s-%s.pyc" % (basename, version)

import py_compile
print("compiling %s to %s" % (source, bytecode))
py_compile.compile(source, bytecode, source)
import os
os.system(f"../decompile_cfg/bin/decompile.py {bytecode}")
