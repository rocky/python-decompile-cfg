#  Copyright (c) 2019-2023 Rocky Bernstein
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

"""
Common decompile_cfg parser routines. From the outside, of the module
you'll usually import a call something here, such as:
* get_python_parser().parse(), or
* python_parser() which does the above

Note however all of this is imported from the __init__ module
"""

import sys

from xdis import iscode
from xdis.version_info import PYTHON_VERSION_TRIPLE, IS_PYPY
from spark_parser import DEFAULT_DEBUG as PARSER_DEFAULT_DEBUG
from decompile_cfg.parsers.p3_8.heads import (
    Python3_8ParserLambda,
    Python3_8ParserEval,
    Python3_8ParserExec,
    Python3_8ParserExpr,
    Python3_8ParserSingle,
)

from decompile_cfg.parsers.p3_9.heads import (
    Python3_9ParserLambda,
    Python3_9ParserEval,
    Python3_9ParserExec,
    Python3_9ParserExpr,
    Python3_9ParserSingle,
)

from decompile_cfg.parsers.p3_9pypy.heads import (
    PyPy3_9ParserEval,
    PyPy3_9ParserExec,
    PyPy3_9ParserExpr,
    PyPy3_9ParserLambda,
    PyPy3_9ParserSingle,
)

from decompile_cfg.parsers.p3_10.heads import (
    Python3_10ParserLambda,
    Python3_10ParserEval,
    Python3_10ParserExec,
    Python3_10ParserExpr,
    Python3_10ParserSingle,
)

from decompile_cfg.show import maybe_show_asm


def parse(p, tokens, customize, is_lambda):
    was_lambda = p.is_lambda
    p.is_lambda = is_lambda
    p.customize_grammar_rules(tokens, customize)
    ast = p.parse(tokens)
    p.is_lambda = was_lambda
    #  p.cleanup()
    return ast


def get_python_parser(
    version, debug_parser=PARSER_DEFAULT_DEBUG, compile_mode="exec", is_pypy=False
):
    """Returns parser object for Python version 3.8 depending on the
    parameters passed.  *compile_mode* is either "exec", "eval",
    "eval_expr", or "single" or "lambda".

    * "lambda" is for the grammar that can appear in lambda statements.
    * "eval_expr" is for grammar "expr" kinds of expressions - this is a smaller kind of
       "eval" that users only grammar inside lambdas.
    * "eval" is for Python eval() kinds of expressions or eval compile mode
    * "exec" is for Python exec() kind of expresssions, or exec compile mode
    * "single" is python compile "single" compile mode

    See https://docs.python.org/3/library/functions.html#compile for an
    explanation of the different modes.

    """

    # FIXME: there has to be a better way...
    # We could do this as a table lookup, but that would force us
    # in import all of the parsers all of the time. Perhaps there is
    # a lazy way of doing the import?

    version = version[:2]
    if version == (3, 8):

        if compile_mode == "exec":
            p = Python3_8ParserExec(debug_parser=debug_parser)
        elif compile_mode == "single":
            p = Python3_8ParserSingle(debug_parser=debug_parser)
        elif compile_mode == "lambda":
            p = Python3_8ParserLambda(debug_parser=debug_parser)
        elif compile_mode == "eval":
            p = Python3_8ParserEval(debug_parser=debug_parser)
        elif compile_mode == "expr":
            p = Python3_8ParserExpr(debug_parser=debug_parser)
        else:
            p = Python3_8ParserSingle(debug_parser=debug_parser)

    elif version == (3, 9):
        if is_pypy:
            if compile_mode == "exec":
                p = PyPy3_9ParserExec(debug_parser=debug_parser)
            elif compile_mode == "single":
                p = PyPy3_9ParserSingle(debug_parser=debug_parser)
            elif compile_mode == "lambda":
                p = PyPy3_9ParserLambda(debug_parser=debug_parser)
            elif compile_mode == "eval":
                p = PyPy3_9ParserEval(debug_parser=debug_parser)
            elif compile_mode == "expr":
                p = PyPy3_9ParserExpr(debug_parser=debug_parser)
            else:
                p = PyPy3_9ParserSingle(debug_parser=debug_parser)
        else:
            if compile_mode == "exec":
                p = Python3_9ParserExec(debug_parser=debug_parser)
            elif compile_mode == "single":
                p = Python3_9ParserSingle(debug_parser=debug_parser)
            elif compile_mode == "lambda":
                p = Python3_9ParserLambda(debug_parser=debug_parser)
            elif compile_mode == "eval":
                p = Python3_9ParserEval(debug_parser=debug_parser)
            elif compile_mode == "expr":
                p = Python3_9ParserExpr(debug_parser=debug_parser)
            else:
                p = Python3_9ParserSingle(debug_parser=debug_parser)

    elif version == (3, 10):

        if compile_mode == "exec":
            p = Python3_10ParserExec(debug_parser=debug_parser)
        elif compile_mode == "single":
            p = Python3_10ParserSingle(debug_parser=debug_parser)
        elif compile_mode == "lambda":
            p = Python3_10ParserLambda(debug_parser=debug_parser)
        elif compile_mode == "eval":
            p = Python3_10ParserEval(debug_parser=debug_parser)
        elif compile_mode == "expr":
            p = Python3_10ParserExpr(debug_parser=debug_parser)
        else:
            p = Python3_10ParserSingle(debug_parser=debug_parser)

    else:
        raise RuntimeError(f"Unsupported Python version {version}")

    p.version = version
    # p.dump_grammar() # debug
    return p


def python_parser(
    co,
    version: str = PYTHON_VERSION_TRIPLE,
    out=sys.stdout,
    showasm=False,
    parser_debug=PARSER_DEFAULT_DEBUG,
    compile_mode="exec",
    is_pypy=False,
    is_lambda=False,
):
    """
    Parse a code object to an abstract syntax tree representation.

    :param version:         The Python version this code is from, as a tuple, e.g.
                            (3, 8), or (3, 8, 0).
    :param co:              The code object to parse.
    :param out:             File like object to write the output to.
    :param showasm:         Flag which determines whether the disassembled and
                            ingested code is written to sys.stdout or not.
    :param parser_debug:    dict containing debug flags for the spark parser.

    :return: Abstract syntax tree representation of the code object.
    """

    assert iscode(co)
    from decompile_cfg.scanner import get_scanner

    scanner = get_scanner(version, is_pypy)
    tokens, customize = scanner.ingest(co)
    maybe_show_asm(showasm, tokens)

    # For heavy grammar debugging
    # parser_debug = {'rules': True, 'transition': True, 'reduce' : True,
    #                 'showstack': 'full'}
    p = get_python_parser(
        version, parser_debug, compile_mode=compile_mode, is_pypy=IS_PYPY
    )

    # FIXME: have p.insts update in a better way
    # modularity is broken here
    p.insts = scanner.insts
    p.offset2inst_index = scanner.offset2inst_index
    p.opc = scanner.opc

    return parse(p, tokens, customize, is_lambda)


if __name__ == "__main__":

    def parse_test(co) -> None:
        from xdis.version_info import IS_PYPY

        testing = lambda x, y: "0" <= x <= "9" and "a" <= y <= "f"

        ast = python_parser(
            testing.__code__,
            showasm=True,
            compile_mode="lambda",
            is_pypy=IS_PYPY,
            is_lambda=True,
        )
        print(ast)
        print("=" * 30)

        test_expr = lambda x, y: x + 1

        # parser_debug = {
        #     "rules": True,
        #     "transition": False,
        #     "reduce": True,
        #     "errorstack": None,
        #     "context": True,
        #     "dups": False,
        #     }

        ast = python_parser(
            test_expr.__code__,
            showasm=True,
            compile_mode="single",
            is_pypy=IS_PYPY,
            is_lambda=False,
        )
        print(ast)
        print("-" * 30)

        ast = python_parser(
            test_expr.__code__,
            showasm=True,
            compile_mode="expr",
            is_pypy=IS_PYPY,
            is_lambda=False,
            # parser_debug=parser_debug,
        )

        print(ast)
        print("+" * 30)
        return

    parse_test(parse_test.__code__)
