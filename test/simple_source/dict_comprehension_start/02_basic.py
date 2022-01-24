# These are an accumulation of dict comprehensions.
# They were culled from all list comprehensions on my disk under Python 3.8.

# fmt: off
# From Python 3.8 sre_compile.py line 62
{i:
 tuple(j
       for j
       in t
       if i != j)
 for t
 in __file__
 for i
 in t}
