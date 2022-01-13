# FIXME: We don't have statements in yet.
# These are an accumulation of lambda expressions involving logical operations.
# They were culled from all lambda's on my disk under Python 3.8.

# we can turn this into a self-checking program when we do.
# """This program is self-checking!"""

# NOTE: Formatting may be weird because we want the additional line numbers
# in debugging.

# fmt: off
lambda A: A @ 1
lambda x, y: x * y

lambda a:  1e300 * a * 1e300
lambda b: -1e300 * b * 1e300

lambda a, b, c, d:  a | b & c ^ d

lambda:  len(__file__) / 2
lambda x: 5j + x

lambda x: (ord(str[0]) +
           (ord(str[1]) << 8) +
           (ord(str[2]) << 16) +
           (ord(str[3]) << 24))

lambda a: a // 2
lambda b: b ** 5 // 3.0
lambda c: c / 3 % 6
