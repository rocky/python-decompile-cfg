# FIXME: We don't have statements in yet.
# These are an accumulation of lambda expressions involving all of the varied kinds of
# non-list comprehensions.
# They were culled from all lambda's on my disk under Python 3.8.

# we can turn this into a self-checking program when we do.
# """This program is self-checking!"""

# NOTE: Formatting may be weird because we want the additional line numbers
# in debugging.

# fmt: off
lambda f: (yield from f())

# From sympy/integrals/manualintegrate.py
lambda integrand, symbol: (
    {a
     for a
     in integrand()})

# From sympy/polys/matrices/sdm.py:
lambda n, ddm: {j
                for j
                in n
                if ddm}

lambda i, ddm: {ddm[i][j]
                for j
                in range(5)
                if ddm[i][j]}

# Generator
lambda getrow: ((i, getrow(i))
                for i
                in range(10))

lambda irows: {i
               for i, row
               in irows
               if row}
