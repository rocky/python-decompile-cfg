from decompile_ng.parsers.p310.full import  Python310Parser
from decompile_ng.parsers.p310.lambda_expr import  Python310LambdaParser
from decompile_ng.parsers.parse_heads import (
    PythonParserEval,
    PythonParserExpr,
    PythonParserLambda,
    PythonParserSingle,
)

# These classes are here just to get parser doc-strings for the
# various classes inherited properly.
class Python310ParserSingle(Python310Parser, PythonParserSingle):
    pass


class Python310ParserLambda(Python310LambdaParser, PythonParserLambda):
    pass


class Python310ParserEval(Python310LambdaParser, PythonParserEval):
    pass


class Python310ParserExpr(Python310LambdaParser, PythonParserExpr):
    pass
