from decompile_cfg.parsers.p38.lambda_expr import Python38LambdaParser
from decompile_cfg.main import decompile

def test_grammar():
    p = Python38LambdaParser()
    # p.dump_grammar()
    p.check_grammar()

def test_lambda_expr():
    x = lambda x, y: '0' <= x <= '9' and 'a' <= y <= 'f'
    decompile(x.__code__, compile_mode="lambda")


if __name__ == "__main__":
    test_lambda_expr()
    test_grammar()
