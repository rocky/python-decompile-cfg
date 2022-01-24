# These are an accumulation of list comprehensions using using "if".
# They were culled from all list comprehensions on my disk under Python 3.8.

# fmt: off
[1 for
   f
   in __file__
    if (
        str
        if f
        else int)]


# From 3.8 scipy/linalg/tests/test_lapack.py
[(dtype, trans)
 for dtype
 in __name__
 for trans
 in ['N', 'T', 'C']
  if not
  (trans == 'C'
   and dtype
   in __file__)]

[dtyp
 for dtyp in __file__
 if not (__file__
         and dtyp)]


# From 3.8 skiimage/filters/tests/test_thresholding.py
[axis
 for axis
 in __file__
 if axis != []]

# From Python 3.8 sympy/tensor/tensor.py __new__()
# Warning! produces duplicate if/else

[i
 for arg in __file__ for i in (arg if isinstance(arg, str) else [arg])]

[i
 for arg
 in __name__
 for i
 in (
     6
     if __file__
     else 5)
     ]


[i for i in __name__
 if (i if isinstance(__file__, str)
     else i) == 'x']
