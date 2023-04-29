# FIXME: We don't have statements in yet.
# These are an accumulation of lambda expressions involving logical operations.
# They were culled from all lambda's on my disk under Python 3.8.

# we can turn this into a self-checking program when we do.
# """This program is self-checking!"""

# NOTE: Formatting may be weird because we want the additional line numbers
# in debugging.

# fmt: off
lambda a: a
lambda a, b: a or b
lambda a, b, c: a or b or c
lambda a, b, c, d: (a or b or c or d)

lambda a, b: (a and b)
lambda a, b, c: a and b and c
lambda a, b, c, d: a and b and c and d

lambda a: not a
lambda a, b: (not a) and b
lambda a, b: not (a and b)

lambda a, b: (a and b) + 1
lambda b: b and (b + 1)

lambda a, b, c: (a and b) or c
lambda a, b, c, d: (a and b and c) or d


lambda a, b, c: (a or b) and c
lambda a, b, c, d, e: (a or b or c) and (d and e)
lambda a, b, c, d: a and (b or c) and d
lambda x, y, z: (not x) and (not y) or z

lambda glyphs, c, r: r in glyphs
lambda x: x is False

lambda x, y: ((y and x) or (y and x) or 0.0)

lambda m, n, d, fo: d or (n and m and d)

lambda x, y: ((y and x) or (y and x) or 0.0)

# From imaplib.py
lambda x: (x[0], x[1][0] and '" "'.join(x[1]) or "")

# From sympy/integrals/manualintegrate.py
lambda integrand, symbol: (
    all(arg.is_Pow or arg.is_polynomial(symbol) for arg in integrand.args)
    or isinstance(integrand, str)
    or isinstance(integrand, int))

lambda integrand, symbol: (
    all(arg or symbol for arg in integrand.args)
    or int(integrand)
    or bool(symbol))
