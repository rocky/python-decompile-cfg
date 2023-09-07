#!/usr/bin/env python
# Mode: -*- python -*-
#
# Copyright (c) 2015-2017, 2019-2023 by Rocky Bernstein
# Copyright (c) 2000-2002 by hartmut Goebel <h.goebel@crazy-compilers.com>
#

import os
import sys

import click
from xdis.version_info import version_tuple_to_str

from decompile_cfg.main import main, status_msg
from decompile_cfg.version import __version__

case_sensitive = {"case_sensitive": False}
program = "decompile_cfg"


def usage():
    print(__doc__)
    sys.exit(1)


@click.command()
@click.option("--asm/--no-asm", "-a", default=False)
@click.option("--asm++/--no-asm++", "-A", "asm_plus", default=False)
@click.option("--grammar/--no-grammar", "-g", "show_grammar", default=False)
@click.option("--tree/--no-tree", "-t", default=False)
@click.option("--tree++/--no-tree++", "-T", "tree_plus", default=False)
@click.option(
    "--verify",
    type=click.Choice(["run", "syntax"]),
    default=None,
)
@click.option(
    "--recurse/--no-recurse",
    "-r",
    "recurse_dirs",
    default=False,
)
@click.option(
    "--output",
    "-o",
    "outfile",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, writable=True, resolve_path=True
    ),
    required=False,
)
@click.version_option(version=__version__)
@click.option(
    "--start-offset",
    "start_offset",
    default=0,
    help="start decomplation at offset; default is 0 or the starting offset.",
)
@click.option(
    "--stop-offset",
    "stop_offset",
    default=-1,
    help="stop decomplation when seeing an offset greater or equal to this; default is "
    "-1 which indicates no stopping point.",
)
@click.argument("files", nargs=-1, type=click.Path(readable=True), required=True)
def main_bin(
    asm: bool,
    asm_plus: bool,
    show_grammar,
    tree: bool,
    tree_plus: bool,
    verify,
    recurse_dirs,
    start_offset: int,
    stop_offset: int,
    outfile, files
):
    """
    Python byecode decompiler for CPython 3.8..3.10 bytecode
    """
    version_tuple = sys.version_info[0:2]
    if not ((3, 8) <= version_tuple <= (3, 10)):
        print(
            f"Note: {program} can decompile only bytecode from Python 3.8 to 3.10"
            f"""\n\tYou have version: {version_tuple_to_str()}."""
        )

    out_base = None
    source_paths = []
    # timestamp = False
    # timestampfmt = "# %Y.%m.%d %H:%M:%S %Z"
    pyc_paths = files

    # expand directory if specified
    if recurse_dirs:
        expanded_files = []
        for f in pyc_paths:
            if os.path.isdir(f):
                for root, _, dir_files in os.walk(f):
                    for df in dir_files:
                        if df.endswith(".pyc") or df.endswith(".pyo"):
                            expanded_files.append(os.path.join(root, df))
        pyc_paths = expanded_files

    # argl, commonprefix works on strings, not on path parts,
    # thus we must handle the case with files in 'some/classes'
    # and 'some/cmds'
    src_base = os.path.commonprefix(pyc_paths)
    if src_base[-1:] != os.sep:
        src_base = os.path.dirname(src_base)
    if src_base:
        sb_len = len(os.path.join(src_base, ""))
        pyc_paths = [f[sb_len:] for f in pyc_paths]

    if not pyc_paths and not source_paths:
        print("No input files given to decompile", file=sys.stderr)

    # Use stdout if outfile is None
    if outfile is not None:
        if os.path.isdir(outfile):
            out_base = outfile
            outfile = None
        elif len(pyc_paths) > 1:
            out_base = outfile
            outfile = None

    # Handle assembly options.
    if asm_plus or asm:
        asm_opt = "both"  if asm_plus else "after"
    else:
        asm_opt = None

    # if timestamp:
    #     print(time.strftime(timestampfmt))

    show_ast = {"before": tree or tree_plus, "after": tree_plus}
    result = main(
        src_base,
        out_base,
        pyc_paths,
        source_paths,
        outfile,
        showasm=asm_opt,
        showgrammar=show_grammar,
        showast=show_ast,
        do_verify=verify,
        start_offset=start_offset,
        stop_offset=stop_offset,
    )
    try:
        if len(pyc_paths) > 1:
            mess = status_msg(verify, *result)
            print("# " + mess)
            pass
    except ImportError as e:
        print(str(e))
        sys.exit(2)
    except (KeyboardInterrupt):
        pass

    # if timestamp:
    #     print(time.strftime(timestampfmt))

    return


if __name__ == "__main__":
    main_bin()
