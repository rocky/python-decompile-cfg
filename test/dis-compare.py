#!/usr/bin/env python
# Mode: -*- python -*-
#
# Copyright (c) 2015, 2021 by Rocky Bernstein <rb@dustyfeet.com>
#
from __future__ import print_function


import dis, os.path

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

program =  os.path.basename(__file__)

__doc__ = """
Usage: %s [OPTIONS]... FILE

""" % program

usage_short = "Usage: %s [OPTIONS]... FILE" % program

import decompile_ng
from decompile_ng import check_python_version
from decompile_ng.disas import disco
from xdis.version_info import version_tuple_to_str

def inst_fmt(inst):
    if inst.starts_line:
        return '\n%4d  %6s\t%-17s %r' % (inst.starts_line, inst.offset, inst.opname,
                                         inst.argrepr)
    else:
        return '      %6s\t%-17s %r' % (inst.offset, inst.opname, inst.argrepr)

    print
    return

def compare_ok(version, co):
    out  = StringIO()
    if version in (2.6, 2.7):
        print("Doesn't work on %d\n yet"  %  version)
        # dis.disco(co)
        return True

    bytecode = dis.Bytecode(co)

    disco(version, co, out)
    got_lines = out.getvalue().split("\n")[2:]
    i = 0
    good_lines = "\n".join([inst_fmt(inst) for inst in bytecode]).split("\n")
    for good_line in good_lines:
        if '\tCOME_FROM         ' in got_lines[i]:
            i += 1

        if got_lines[i] != good_line:
            print('line %d %s' % (i+1, ('=' * 30)))
            print(good_line)
            print("vs %s" % ('-' * 10))
            print(got_lines[i])
            return False
        i += 1
    return True

check_python_version(program)

# if len(sys.argv) != 2:
#     print(usage_short, file=sys.stderr)
#     sys.exit(1)

# filename = sys.arv[1]
def get_srcdir():
    filename = os.path.normcase(os.path.dirname(__file__))
    return os.path.realpath(filename)

src_dir = get_srcdir()
os.chdir(src_dir)

files = [
    'if',
    'ifelse',
    # 'keyword',
    ]

for base in files:
    filename = f"bytecode_{version_tuple_to_str()}/{base}s.pyc"
    version, timestamp, magic_int, co = decompile_ng.load_module(filename)
    ok = True

    if type(co) == list:
        for con in co:
            ok = compare_ok(version, con)
            if not ok: break
    else:
        ok = compare_ok(version, co)
    if ok:
        print("Disassembly of %s checks out!" % filename)
    else:
        print("Disassembly of %s mismatches." % filename)
        break
