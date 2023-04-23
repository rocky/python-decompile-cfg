"""
All of the specific kinds of canned parsers for Python 3.8

These are derived from "compile-modes" but we have others that
can be used to parse common part of a larger grammar.

For example:
* a basic-block expression (no branching)
* an unadorned expression (no POP_TOP needed afterwards)
* A non-compound statement
"""
from decompile_cfg.parsers.p3_8.full import Python3_8ParserFull
from decompile_cfg.parsers.p3_8.lambda_expr import Python3_8LambdaParser
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

# Make sure to list Python3_8... classes first so we prefer to inherit methods from that first.
# In particular methods like reduce_is_invalid() need to come from there rather than
# a more generic place.


class Python3_8ParserEval(Python3_8LambdaParser, PythonParserEval):
    def __init__(self, debug_parser):
        PythonParserEval.__init__(self, debug_parser)


class Python3_8ParserExec(Python3_8ParserFull, PythonParserExec):
    def __init__(self, debug_parser):
        PythonParserExec.__init__(self, debug_parser)


class Python3_8ParserExpr(Python3_8ParserFull, PythonParserExpr):
    def __init__(self, debug_parser):
        PythonParserExpr.__init__(self, debug_parser)


# Understand: Python3_8LambdaParser has to come before PythonParserLambda or we get a
# MRO failure
class Python3_8ParserLambda(Python3_8LambdaParser, PythonParserLambda):
    def __init__(self, debug_parser):
        PythonParserLambda.__init__(self, debug_parser)


# These classes are here just to get parser doc-strings for the
# various classes inherited properly and start_symbols set properly.
class Python3_8ParserSingle(Python3_8ParserFull, PythonParserSingle):
    def __init__(self, debug_parser):
        PythonParserSingle.__init__(self, debug_parser)
