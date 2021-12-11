from decompile_ng.parsers.p310.lambda_expr import Python310LambdaParser
from decompile_ng.main import decompile

def test_grammar():
    p = Python310LambdaParser()
    # p.dump_grammar()
    p.check_grammar()

def test_lambda_expr():
    x = lambda x, y: '0' <= x <= '9' and 'a' <= y <= 'f'
    decompile(x.__code__, compile_mode="lambda")


if __name__ == "__main__":
    test_lambda_expr()
    test_grammar()
