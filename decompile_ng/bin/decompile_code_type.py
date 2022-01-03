#!/usr/bin/env python
# Mode: -*- python -*-
#
# Copyright (c) 2015-2016, 2018, 2020-2022 by Rocky Bernstein <rb@dustyfeet.com>
#
import click
import os
import sys

from decompile_ng.code_fns import decompile_list_comprehensions, decompile_lambda_fns
from decompile_ng.version import __version__

if click.__version__ >= "7.":
    case_sensitive = {"case_sensitive": False}
else:
    case_sensitive = {}

program, ext = os.path.splitext(os.path.basename(__file__))

PATTERNS = ("*.pyc", "*.pyo")


@click.command()
@click.option(
    "--format",
    "-F",
    type=click.Choice(
        ["lambda", "list-comprehension"],
        **case_sensitive
    ),
)
@click.version_option(version=__version__)
@click.argument("files", nargs=-1, type=click.Path(readable=True), required=True)
def main(format, files):
    """Decompile all code objects of a certain format.
    """

    # FIXME is there a "click" way to do this?
    if format is None:
        format = "lambda"

    if format == "lambda":
        decompile_fn = decompile_lambda_fns
    elif format == "list-comprehension":
        decompile_fn = decompile_list_comprehensions
    else:
        print(f"Unexpected format {format}")
        return 1

    success = 0
    skipped = 0
    total = 0
    for filename in files:
        print(f"total: {total}, success: {success}")
        try:
            if os.path.isdir(filename):
                for subdir, dirs, files in os.walk(filename):
                    for filename in files:
                        filepath = subdir + os.sep + filename
                        if filepath.endswith(".pyc") or filepath.endswith(".py") or filepath.endswith(".pyo"):
                            decompile_fn(filepath, sys.stdout)
                            print()
                            success += 1
                            total += 1
            elif os.path.exists(filename) and not os.path.islink(filename):
                if filename.endswith(".pyc") or filename.endswith(".py") or filename.endswith(".pyo") or os.path.isdir(filename):
                    decompile_fn(filename, sys.stdout, showasm=None, showast=False)
                    print()
                    success += 1
                    total += 1
            else:
                print(f"Can't read {filename}; skipping", file=sys.stderr)
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
    print(f"total: {total}, success: {success}")
    return


if __name__ == "__main__":
    main()
