# FIXME: We don't have statements in yet.
# These are an accumulation of lambda expressions involving logical operations.
# They were culled from all lambda's on my disk under Python 3.8.

# NOTE: Formatting may be weird because we want the additional line numbers
# in debugging.

# fmt: off
lambda A: A @ 1
lambda b: b << 2 >> 3
lambda c: 1 < c < 3
lambda d:  1e300 * d * 1e300
lambda e: -1e300 * e * 1e300
lambda x, y: x * y - 1

lambda:  len(__file__) / 2
lambda x: 5j + x

lambda x: (ord(str[0]) +
           (ord(str[1]) << 8) +
           (ord(str[2]) << 16) +
           (ord(str[3]) << 24))

lambda a: a // 2
lambda b: b ** 5 // 3.0
lambda c: c / 3 % 6
