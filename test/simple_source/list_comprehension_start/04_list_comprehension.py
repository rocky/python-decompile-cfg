# FIXME: We don't have statements in yet.
# These are an accumulation of lambda expressions involving all of the varied kinds of
# list comprehensions.
# They were culled from all lambda's on my disk under Python 3.8.

# we can turn this into a self-checking program when we do.
# """This program is self-checking!"""

# NOTE: Formatting may be weird because we want the additional line numbers
# in debugging.
ary = [1, 2, 3]
n = 10

# fmt: off
[
 i
 for i
 in ary]

[
 i * i
 for i
 in range(n)
 ]

[
 i * i
 for i in range(n)
 if n]

[
 b
 for b
 in (0, 1, 2, 3)] if (
     __name__ == "__main__"
     ) else 5

[i * i
 for i
     in range(n)
     if n]

''.join(
    ord(c)
    for c in range(0, 2)
                   + 1)

# From numpy/core/tests/test_simd.py
[
    b
    for
    i, b in
    ary]

# From py3_test_grammar.py
[
 2 < x
 for x in [
     -1, 3, 0
     ]]


# From sympy/codegen/fnodes.py
tuple(
    *[arg
      if isinstance(n, int)
      else
      ord(*arg)
      for arg
      in ary])
