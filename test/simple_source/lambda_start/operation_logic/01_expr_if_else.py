# FIXME: We don't have statements in yet.
# These are an accumulation of lambda expressions involving IfExp (and not comprehensions)
# They were culled from all lambda's on my disk under Python 3.8.

# NOTE: Formatting may be weird because we want the additional line numbers
# in debugging.

# we can turn this into a self-checking program when we do.
# """This program is self-checking!"""

# fmt: off
lambda a, b, c: a if c else b
lambda a: False if not a else True

lambda x: 1 if x < 2 else 3

# IfExp with a "not"
lambda x: 1 + (
    2 if not
    x
    else 4)


# From 3.10 fontTools/subset/__init__.py. The else [] uses a BUILD_LIST_0
lambda glyphs, c, r: (
    [r]
    if r
    in glyphs
    else []
    )

lambda glyphs, c, r: (
    glyphs if c else (set(glyphs) if r == 0 else set())
)

# From numpy/core/tests/test_umath.py
lambda n, d, fo: (
    0 if d == 0 or (n and n == fo.min and d == -1) else n//d
    )


# From somewhere in numpy. Note the parenthesis are optional
# I put them in for clarity
lambda m, n, d, fo: (
    0
    if
    d or
    (n and m
     and fo)
    else n)


# Simplication of the above... Note the parenthesis again are optional
# I put them in for clarity.
lambda m, n, d, fo: d or (
    n and m and d
    )

# Simplified from numpy/core/tests/test_simd.py which
# has a wealth of lambda's.
lambda v: v + 0.5 if v else v + -0.5

lambda v: int(
    v +
    (0.5
     if v >= 0
     else -0.5))

lambda n: True if n >= 95 and n & 1 else False

lambda e1, e2, a, b, c: (
      a if e1 else b if e2 else c
 )

lambda p: p if p else ''.join(
    c for c in range(5)
    )

# From virtualenv/discovery/windows/__init__.py

lambda i: tuple(-1
                if j is None
                else j
                for j
                in i) + (
                    1
                    if
                    i else 0,)


# # From test/test_os.py
lambda p: p.startswith(
    b'x'
    if isinstance(p,bytes)
    else 'y')
