# FIXME: We don't have statements in yet.
# we can turn this into a self-checking program when we do.
# """This program is self-checking!"""

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
