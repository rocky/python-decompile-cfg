# Copyright (C) 2025 Rocky Bernstein <rocky@gnu.org>
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
"""decompile-cfg packaging information"""

# To the extent possible we make this file look more like a
# configuration file rather than code like setup.py. I find putting
# configuration stuff in the middle of a function call in setup.py,
# which for example requires commas in between parameters, is a little
# less elegant than having it here with reduced code, albeit there
# still is some room for improvement.

import os.path as osp

# Things that change more often go here.
copyright = """
Copyright (C) 2025 Rocky Bernstein <rb@dustyfeet.com>.
"""

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Topic :: Software Development :: Debuggers",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

# The rest in alphabetic order
author = "Rocky Bernstein"
author_email = "rb@dustyfeet.com"
entry_points = {
    "console_scripts": [
        "decompile-cfg=decomple_cfg.bin.decompile:main_bin",
        "decompile-cfg-code=decompile_cfg.bin.decompile_code_type:main",
        "decompile-cfg-tokenize=decompile_cfg.bin.decompile_tokens:main",
    ]
}
ftp_url = None
install_requires = [
    "click",
    "python-control-flow",
    "spark-parser >= 1.8.9, < 1.9.2",
    "xdis >= 6.1.1, < 6.3"
    ]

license = "GPL3"
mailing_list = "python-debugger@googlegroups.com"
modname = "decompile_cfg"
py_modules = []
short_desc = "Python cross-version byte-code decompiler"
web = "https://github.com/rocky/python-decompile3/"

# tracebacks in zip files are funky and not debuggable
zip_safe = True


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


srcdir = get_srcdir()


def read(*rnames):
    return open(osp.join(srcdir, *rnames)).read()


# Get info from files; set: long_description and VERSION
long_description = read("README.rst") + "\n"
__version__ = "should have been set in version.py"
exec(read("decompile_cfg/version.py"))
