# FIXME: We don't have statements in yet.
# we can turn this into a self-checking program when we do.
# """This program is self-checking!"""

lambda a, b, c: a if c else b
lambda a: False if not a else True

# From 3.10 fontTools/subset/__init__.py. The else [] uses a BUILD_LIST_0
lambda glyphs, c, r: [r] if r in glyphs else []

lambda glyphs, c, r: (
    glyphs if c else (set(glyphs) if r == 0 else set())
)

# From somewhere in numpy. Note the parenthesis are optional
# I put them in for clarity
lambda m, n, d, fo: (0 if d or (n and m and fo) else n)


# Simplication of the above... Note the parenthesis again are optional
# I put them in for clarity.
lambda m, n, d, fo: d or (n and m and d)

# Simplified from numpy/core/tests/test_simd.py which
# has a wealth of lambda's.
lambda v: v + 0.5 if v else v + -0.5
