import pytest
from xdis.version_info import PYTHON_VERSION_TRIPLE
from decompile_cfg.main import decompile
from decompile_cfg.parsers.p3_8.lambda_expr import Python3_8LambdaParser
from decompile_cfg.parsers.p3_9.lambda_expr import Python3_9LambdaParser
from decompile_cfg.parsers.p3_10.lambda_expr import Python3_10LambdaParser


def test_grammar():
    for parse_fn in (
        Python3_8LambdaParser,
        Python3_9LambdaParser,
        Python3_10LambdaParser,
    ):
        p = parse_fn()
        # p.dump_grammar()
        p.check_grammar()

@pytest.mark.skipif(PYTHON_VERSION_TRIPLE >= (3, 10),
                    reason="Decompiler not finished yet for 3.10")
def test_lambda_expr():
    x = lambda x, y: ("0" <= x <= "9")  # noqa
    # x = lambda x, y: (  # noqa
    #     "0" <= x <= "9" and "a" <= y <= "f"
    # )
    decompile(x.__code__, compile_mode="lambda")


if __name__ == "__main__":
    test_lambda_expr()
    test_grammar()
