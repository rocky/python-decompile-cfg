#!/usr/bin/env python
# emacs-mode: -*-python-*-

"""
test_pythonlib.py -- compile, decompile, and verify Python libraries

Usage-Examples:

  # decompile, and verify the first 100 python 3.9 byte-compiled files
  test_pythonlib.py --3.9 --syntax-verify

  # Same as above longer decompile up to 2100
  test_pythonlib.py --3.9 --syntax-verify --max=2100

  # Same as above but compile the base set first
  test_pythonlib.py --3.9 --syntax-verify --max=2100 --compile

  # decompile, and verify the first 100 python 3.9 byte-compiled files
  # but stop on the first error
  test_pythonlib.py --3.9 --first-error


Adding own test-trees:

Step 1) Edit this file and add a new entry to 'test_options', eg.
  test_options['mylib'] = ('/usr/lib/mylib', PYOC, 'mylib')
Step 2: Run the test:
  test_pythonlib.py --mylib	  # decompile 'mylib'
  test_pythonlib.py --mylib --syntax-verify # decompile verify 'mylib'
"""

import getopt
import os
import py_compile
import shutil
import sys
import tempfile
import time

from xdis.version_info import PYTHON_VERSION_TRIPLE
from decompile_cfg.main import main
from fnmatch import fnmatch


def get_srcdir():
    filename = os.path.normcase(os.path.dirname(__file__))
    return os.path.realpath(filename)


src_dir = get_srcdir()


# ----- configure this for your needs

lib_prefix = "/usr/lib"
# lib_prefix = [src_dir, '/usr/lib/', '/usr/local/lib/']

target_base = tempfile.mkdtemp(prefix="py-dis-")

PY = ("*.py",)
PYC = ("*.pyc",)
PYO = ("*.pyo",)
PYOC = ("*.pyc", "*.pyo")

test_options = {
    # name:   (src_basedir, pattern, output_base_suffix, python_version)
    "test": ("test", PYC, "test"),
}

for vers in ("3.8", "3.9", "3.10"):
    bytecode = f"bytecode_{vers}"
    key = f"bytecode-{vers}"
    test_options[key] = (bytecode, PYC, bytecode, vers)
    bytecode = f"bytecode_{vers}_run"
    key = f"bytecode-{vers}/run"
    test_options[key] = (bytecode, PYC, bytecode, vers)
    key = f"{vers}"
    pythonlib = f"python{vers}"
    if isinstance(vers, float) and vers >= 3.0:
        pythonlib = os.path.join(pythonlib, "__pycache__")
    test_options[key] = (os.path.join(lib_prefix, pythonlib), PYOC, pythonlib, vers)

# -----


def help():
    print(
        """Usage-Examples:

  # compile, decompile and verify short tests for Python 3.8:
  test_pythonlib.py --bytecode-3.8 --syntax-verify --compile

  # decompile all of Python's installed lib files
  test_pythonlib.py --3.8
"""
    )
    sys.exit(1)


def do_tests(src_dir, obj_patterns, target_dir, opts):
    def file_matches(files, root, basenames, patterns):
        files.extend(
            [
                os.path.normpath(os.path.join(root, n))
                for n in basenames
                for pat in patterns
                if fnmatch(n, pat)
            ]
        )

    files = []

    if opts["compile_type"] == "lambda":
        src_dir += "/code-fragment/lambda"
    elif opts["compile_type"] == "dict-comprehension":
        src_dir += "/code-fragment/dict-comprehension"
    elif opts["compile_type"] == "generator":
        src_dir += "/code-fragment/generator"
    elif opts["compile_type"] == "list-comprehension":
        src_dir += "/code-fragment/list-comprehension"
    elif opts["compile_type"] == "set-comprehension":
        src_dir += "/code-fragment/set-comprehension"
    elif opts["compile_type"] == "run":
        src_dir += "/run"
    else:
        src_dir += "/exec"

    # Change directories so use relative rather than
    # absolute paths. This speeds up things, and allows
    # main() to write to a relative-path destination.
    cwd = os.getcwd()
    os.chdir(src_dir)

    if opts["do_compile"]:
        compiled_version = opts["compiled_version"]
        if compiled_version and PYTHON_VERSION_TRIPLE != compiled_version:
            print(
                "Not compiling: desired Python version is %s but we are running %s"
                % (compiled_version, PYTHON_VERSION_TRIPLE),
                file=sys.stderr,
            )
        else:
            for root, dirs, basenames in os.walk(src_dir):
                file_matches(files, root, basenames, PY)
                for sfile in files:
                    py_compile.compile(sfile)
                    pass
                pass
            files = []
            pass
        pass

    for root, dirs, basenames in os.walk("."):
        # Turn root into a relative path
        dirname = root[2:]  # 2 = len('.') + 1
        file_matches(files, dirname, basenames, obj_patterns)

    if not files:
        print(
            "Didn't come up with any files to test! Try with --compile?",
            file=sys.stderr,
        )
        exit(1)

    os.chdir(cwd)
    files.sort()

    if opts["start_with"]:
        try:
            start_with = files.index(opts["start_with"])
            files = files[start_with:]
            print(">>> starting with file", files[0])
        except ValueError:
            pass

    print(time.ctime())
    print("Source directory: ", src_dir)
    print("Output directory: ", target_dir)
    try:
        _, _, failed_files, failed_verify = main(
            src_dir,
            target_dir,
            files,
            [],
            do_verify=opts["do_verify"],
            stop_on_first_error=opts["stop_on_first_error"],
        )
        if failed_files != 0:
            sys.exit(2)
        elif failed_verify:
            parent_dir = os.path.dirname(target_dir)
            print(f"Verify failed, keeping {parent_dir}")
            sys.exit(3)

    except (KeyboardInterrupt, OSError):
        print()
        sys.exit(1)
    if test_opts["rmtree"]:
        parent_dir = os.path.dirname(target_dir)
        print(f"Everything good, removing {parent_dir}")
        shutil.rmtree(parent_dir)


if __name__ == "__main__":
    test_dirs = []
    checked_dirs = []
    start_with = None

    test_options_keys = list(test_options.keys())
    test_options_keys.sort()
    opts, args = getopt.getopt(
        sys.argv[1:],
        "",
        [
            "all",
            "compile",
            "coverage",
            "dict-comprehension",
            "generator",
            "lambda",
            "list-comprehension",
            "no-rm",
            "run",
            "set-comprehension",
            "start-with=",
            "first-error",
            "syntax-verify",
            "verify-run",
        ]
        + test_options_keys,
    )
    if not opts:
        help()

    test_opts = {
        "compile_type": "exec",
        "coverage": False,
        "do_compile": False,
        "do_verify": None,
        "stop_on_first_error": False,
        "rmtree": True,
        "start_with": None,
    }

    test_opts["rmtree"] = True
    for opt, val in opts:
        if opt == "--syntax-verify":
            test_opts["do_verify"] = "weak"
        elif opt == "--verify-run":
            test_opts["do_verify"] = "verify-run"
        elif opt == "--compile":
            test_opts["do_compile"] = True
        elif opt == "--lambda":
            test_opts["compile_type"] = "lambda"
        elif opt == "--dict-comprehension":
            test_opts["compile_type"] = "dict-comprehension"
        elif opt == "--generator":
            test_opts["compile_type"] = "generator"
        elif opt == "--list-comprehension":
            test_opts["compile_type"] = "list-comprehension"
        elif opt == "--run":
            test_opts["compile_type"] = "run"
        elif opt == "--set-comprehension":
            test_opts["compile_type"] = "set-comprehension"
        elif opt == "--start-with":
            test_opts["start_with"] = val
        elif opt == "--no-rm":
            test_opts["rmtree"] = False
        elif opt[2:] in test_options_keys:
            test_dirs.append(test_options[opt[2:]])
        elif opt == "--all":
            for val in test_options_keys:
                test_dirs.append(test_options[val])
        elif opt == "--coverage":
            test_opts["coverage"] = True
        elif opt in ("--first-error"):
            test_opts["stop_on_first_error"] = True
        else:
            help()
            pass
        pass

    if test_opts["coverage"]:
        os.environ["SPARK_PARSER_COVERAGE"] = (
            f"/tmp/spark-grammar-python-lib{test_dirs[0][-1]}.cover"
        )

    last_compile_version = None
    for src_dir, pattern, target_dir, compiled_version in test_dirs:
        if os.path.isdir(src_dir):
            checked_dirs.append([src_dir, pattern, target_dir])
        else:
            print(f"Can't find directory {src_dir}. Skipping", file=sys.stderr)
            continue
        last_compile_version = compiled_version
        pass

    if not checked_dirs:
        print("No directories found to check", file=sys.stderr)
        sys.exit(1)

    test_opts["compiled_version"] = last_compile_version

    for src_dir, pattern, target_dir in checked_dirs:
        target_dir = os.path.join(target_base, target_dir)
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir, ignore_errors=False)
        do_tests(src_dir, pattern, target_dir, test_opts)
