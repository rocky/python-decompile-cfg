"""
All of the specific kinds of canned parsers for PyPy 3.9

These are derived from "compile-modes" but we have others that
can be used to parse common part of a larger grammar.

For example:
* a basic-block expression (no branching)
* an unadorned expression (no POP_TOP needed afterwards)
* A non-compound statement
"""
from decompile_cfg.parsers.p3_9pypy.full import PyPy3_9ParserFull
from decompile_cfg.parsers.p3_9pypy.lambda_expr import PyPy3_9LambdaParser
from decompile_cfg.parsers.parse_heads import (
    PythonParserEval,
    PythonParserExec,
    PythonParserExpr,
    PythonParserLambda,
    PythonParserSingle,
    # FIXME: add
    # PythonParserSimpleStmt
    # PythonParserStmt
)

# Make sure to list Python3_9... classes first so we prefer to inherit methods from that first.
# In particular methods like reduce_is_invalid() need to come from there rather than
# a more generic place.


class PyPy3_9ParserEval(PyPy3_9LambdaParser, PythonParserEval):
    def __init__(self, debug_parser):
        PythonParserEval.__init__(self, debug_parser)


class PyPy3_9ParserExec(PyPy3_9ParserFull, PythonParserExec):
    def __init__(self, debug_parser):
        PythonParserExec.__init__(self, debug_parser)


class PyPy3_9ParserExpr(PyPy3_9ParserFull, PythonParserExpr):
    def __init__(self, debug_parser):
        PythonParserExpr.__init__(self, debug_parser)


# Understand: Python3_9LambdaParser has to come before PythonParserLambda or we get a
# MRO failure
class PyPy3_9ParserLambda(PyPy3_9LambdaParser, PythonParserLambda):
    def __init__(self, debug_parser):
        PythonParserLambda.__init__(self, debug_parser)


# These classes are here just to get parser doc-strings for the
# various classes inherited properly and start_symbols set properly.
class PyPy3_9ParserSingle(PyPy3_9ParserFull, PythonParserSingle):
    def __init__(self, debug_parser):
        PythonParserSingle.__init__(self, debug_parser)
