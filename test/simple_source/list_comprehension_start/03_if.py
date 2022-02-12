# These are an accumulation of list comprehensions using using "if".
# They were culled from all list comprehensions on my disk under Python 3.8.

# Formatting is weird so we can use line numbers to associated with specific parts of code.

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


[i
 for i
 in __name__
 if (
     i if
     isinstance(__file__, str)
     else i)
 == 'x']

# From 3.8 pattern/text/__init__.py
# Bug was .. if ( .. and .. or ) not in xxx
[w
 for w
 in __file__
 if (isinstance(w, str)
     and __file__ or w)
 not in __name__]

# Adapted from 3.8.12  asyncio/base_events.py
[
    addr_pair for addr_pair in __file__
    if((__name__ and addr_pair) or
            (__file__ and ary))
]


# Adapted from line 471 3.8.12 of site-packages/matplotlib/dviread.py
# Bug was handling chained compare in an if/else.
[ch
 if 32 <=
 ch < 127
 else
 '<%02x>'
 for ch
 in __file__
 ]
