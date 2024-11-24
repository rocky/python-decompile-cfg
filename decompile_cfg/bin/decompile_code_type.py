#!/usr/bin/env python
# Mode: -*- python -*-
#
# Copyright (c) 2015-2016, 2018, 2020-2022, 2024
# by Rocky Bernstein <rb@dustyfeet.com>
#
import click
import os
import sys

from xdis.version_info import version_tuple_to_str
from decompile_cfg.code_fns import (
    decompile_all_fragments,
    decompile_eval,
    decompile_dict_comprehensions,
    decompile_generators,
    decompile_lambda_fns,
    decompile_list_comprehensions,
    decompile_set_comprehensions,
    decompile_single,
)
from decompile_cfg.main import decompile_file
from decompile_cfg.version import __version__

if click.__version__ >= "7.":
    case_sensitive = {"case_sensitive": False}
else:
    case_sensitive = {}

program, ext = os.path.splitext(os.path.basename(__file__))

PATTERNS = ("*.pyc", "*.pyo")


def decompile_format_type(
    code_format,
    asm: bool,
    asm_plus: bool,
    grammar: dict,
    tree,
    tree_plus,
    outfile,
    start_offset: int,
    stop_offset: int,
    files,
):
    """Decompile all code objects of a certain format."""

    version_tuple = sys.version_info[0:2]
    if not ((3, 8) <= version_tuple <= (3, 10)):
        print(
            f"Note: {program} can decompile only bytecode from up to Python 3.8"
            f"""\n\tYou have version: {version_tuple_to_str()}."""
        )

    # FIXME is there a "click" way to do this?
    if code_format is None:
        code_format = "lambda"

    if code_format == "code-fragments":
        decompile_fn = decompile_all_fragments
    elif code_format == "exec":
        decompile_fn = decompile_file
    elif code_format == "eval":
        decompile_fn = decompile_eval
    elif code_format == "generator":
        decompile_fn = decompile_generators
    elif code_format == "dict-comprehension":
        decompile_fn = decompile_dict_comprehensions
    elif code_format == "lambda":
        decompile_fn = decompile_lambda_fns
    elif code_format == "list-comprehension":
        decompile_fn = decompile_list_comprehensions
    elif code_format == "set-comprehension":
        decompile_fn = decompile_set_comprehensions
    elif code_format == "single":
        decompile_fn = decompile_single
    else:
        print(f"Unexpected code_format {code_format}")
        return 1

    # Use stdout if outfile is None
    if outfile is None:
        outfile = sys.stdout
    else:
        if os.path.isdir(outfile):
            outfile = None

    # Handle assembly options.
    if asm_plus or asm:
        asm_opt = "both" if asm_plus else "after"
    else:
        asm_opt = None

    if tree_plus:
        tree = True
    show_ast = {"before": tree, "after": tree_plus}

    success = 0
    skipped = 0
    skipped = 0
    total = 0
    for filename in files:
        print(f"total: {total}, success: {success}")
        try:
            if os.path.isdir(filename):
                for subdir, _, files in os.walk(filename):
                    for filename in files:
                        filepath = subdir + os.sep + filename
                        if (
                            filepath.endswith(".pyc")
                            or filepath.endswith(".py")
                            or filepath.endswith(".pyo")
                        ):
                            succeeded = decompile_fn(
                                filepath,
                                outfile,
                                showasm=asm_opt,
                                showgrammar=grammar,
                                showast=show_ast,
                                start_offset=start_offset,
                                stop_offset=stop_offset,
                            )
                            print()
                            if succeeded:
                                success += 1
                            elif succeeded is None:
                                skipped += 1
                            success += 1
                            total += 1
            elif os.path.exists(filename) and not os.path.islink(filename):
                if (
                    filename.endswith(".pyc")
                    or filename.endswith(".py")
                    or filename.endswith(".pyo")
                    or os.path.isdir(filename)
                ):
                    succeeded = decompile_fn(
                        filename,
                        outfile,
                        showasm=asm_opt,
                        showgrammar=grammar,
                        showast=show_ast,
                        start_offset=start_offset,
                        stop_offset=stop_offset,
                    )
                    print()
                    if succeeded:
                        success += 1
                    elif succeeded is None:
                        skipped += 1
                    total += 1
            else:
                print(f"Can't read {filename}; skipping", file=outfile)
                skipped += 1
                total += 1
                pass
            pass
        # except RuntimeError:  # uncomment out and comment out below to see traceback
        except RuntimeError:
            print("Failure")
            print(sys.exc_info()[1])
            total += 1
        pass
    print(f"total: {total}, success: {success}, skipped: {skipped}")
    return


@click.command()
@click.option(
    "--format",
    "-F",
    "code_format",
    type=click.Choice(
        [
            "code-fragments",
            "dict-comprehension",
            "exec",
            "eval",
            "single",
            "generator",
            "lambda",
            "list-comprehension",
            "set-comprehension",
        ],
        **case_sensitive,
    ),
)
@click.version_option(version=__version__)
@click.option("--asm/--no-asm", "-a", default=False)
@click.option("--asm++/--no-asm++", "-A", "asm_plus", default=False)
@click.option("--grammar/--no-grammar", "-g", default=False)
@click.option("--tree/--no-tree", "-t", default=False)
@click.option("--tree++/--no-tree++", "-T", "tree_plus", default=False)
@click.option(
    "--output",
    "-o",
    "outfile",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, writable=True, resolve_path=True
    ),
    required=False,
)
@click.option(
    "--start-offset",
    "start_offset",
    default=0,
    help="start decompilation at offset; default is 0 or the starting offset.",
)
@click.version_option(version=__version__)
@click.option(
    "--stop-offset",
    "stop_offset",
    default=-1,
    help="stop decomplation when seeing an offset greater or equal to this; default is "
    "-1 which indicates no stopping point.",
)
@click.argument("files", nargs=-1, type=click.Path(readable=True), required=True)
def main(
    code_format,
    asm: bool,
    asm_plus: bool,
    grammar,
    tree,
    tree_plus,
    outfile,
    start_offset: int,
    stop_offset: int,
    files,
):
    """Decompile all code objects of a certain format."""
    decompile_format_type(
        code_format,
        asm,
        asm_plus,
        grammar,
        tree,
        tree_plus,
        outfile,
        start_offset,
        stop_offset,
        files,
    )
    return


if __name__ == "__main__":
    main()
