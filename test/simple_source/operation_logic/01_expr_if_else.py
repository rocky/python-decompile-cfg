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
