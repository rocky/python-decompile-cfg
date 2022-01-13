# FIXME: We don't have statements in yet.
# These are an accumulation of lambda expressions involving all of the varied kinds of
# list comprehensions.
# They were culled from all lambda's on my disk under Python 3.8.

# we can turn this into a self-checking program when we do.
# """This program is self-checking!"""

# NOTE: Formatting may be weird because we want the additional line numbers
# in debugging.

# fmt: off
lambda x: [
    i
    for i
    in x]

lambda n: [
    i * i
    for i
    in range(n)
    ]

lambda n: [
    i * i
    for i in range(n)
    if n]

lambda n: [
    b
    for b
    in (0, 1, 2, 3)] if (
        __name__ == "__main__"
        ) else 5

# Variable "i" is not bound, so this is handled as a closure.
lambda n: [
    i * i
    for i
    in range(n)
    if n]

lambda unichr, p: ''.join(
    unichr(c)
    for c in range(ord(p[0]),
                   ord(p[1])
                   + 1))

lambda p: p if not isinstance(p,
                              list) else ''.join(
                                  ord(c) for c in range(ord(p[0]),
                                                        ord(p[1])
                                                        + 1))
# From numpy/core/tests/test_simd.py
lambda data: [
    x
    for
    i, x in
    data]

# From py3_test_grammar.py
lambda x : [
    2 < x
    for x in [
        -1, 3, 0
        ]]


# From sympy/codegen/fnodes.py
lambda args, use_rename : tuple(
    *[arg
      if isinstance(arg, use_rename)
      else
      use_rename(*arg)
      for arg
      in args])
