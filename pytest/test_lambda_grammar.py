from decompile_cfg.main import decompile
from decompile_cfg.parsers.p3_8.lambda_expr import Python3_8LambdaParser


def test_grammar():
    p = Python3_8LambdaParser()
    # p.dump_grammar()
    p.check_grammar()


def test_lambda_expr():
    x = lambda x, y: (
        "0" <= x <= "9" and "a" <= y <= "f"
    )
    decompile(x.__code__, compile_mode="lambda")


if __name__ == "__main__":
    test_lambda_expr()
    test_grammar()
