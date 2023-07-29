# From 3.8.12 line 1010 site-packages/pip/_vendor/pyparsing/helpers.py (pip 22.0.3)

# fmt: off
# Bug was that "and" or "or" causes block break in return_expr_lambda:
# expr <jumps here> RETURN

# lambda: (
#     (__file__
#      and
#      None)
#     if
#     __name__
#     else
#     None)

# lambda: (
#     (__file__
#      or
#      None)
#     if
#     __name__
#     else
#     None)

lambda n: True if (
    n >= 95
    and
    n & 1) else (
        False
        )
