"""
All of the specific kinds of canned parsers for Python 3.10

These are derived from "compile-modes" but we have others that
can be used to parse common part of a larger grammar.

For example:
* a basic-block expression (no branching)
* an unadorned expression (no POP_TOP needed afterwards)
* A non-compound statement
"""
from decompile_ng.parsers.p310.full import Python310Parser
from decompile_ng.parsers.p310.lambda_expr import Python310LambdaParser
from decompile_ng.parsers.parse_heads import (
    PythonParserEval,
    PythonParserExec,
    PythonParserExpr,
    PythonParserLambda,
    PythonParserSingle,
    # FIXME: add
    # PythonParserSimpleStmt
    # PythonParserStmt
)


class Python310ParserEval(PythonParserEval, Python310LambdaParser):
    def __init__(self, debug_parser):
        PythonParserEval.__init__(self, debug_parser)


class Python310ParserExec(PythonParserExec, Python310Parser):
    def __init__(self, debug_parser):
        PythonParserExec.__init__(self, debug_parser)


class Python310ParserExpr(PythonParserExpr, Python310Parser):
    def __init__(self, debug_parser):
        PythonParserExpr.__init__(self, debug_parser)


# Understand: Python310LambdaParser has to come before PythonParserLambda or we get a
# MRO failure
class Python310ParserLambda(Python310LambdaParser, PythonParserLambda):
    def __init__(self, debug_parser):
        PythonParserLambda.__init__(self, debug_parser)


# These classes are here just to get parser doc-strings for the
# various classes inherited properly and start_symbols set properly.
class Python310ParserSingle(Python310Parser, PythonParserSingle):
    def __init__(self, debug_parser):
        PythonParserSingle.__init__(self, debug_parser)
