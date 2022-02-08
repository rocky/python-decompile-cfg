# These are adapted from list comprehensions found when byte compiling the
# entire set of 3.8 installed packages on my disk.
# Many examples come from packages like sympy or numpy

ary = [1, 2, 3]
ary2 = [6, 8, 10]
n = 10

# fmt: off
# Adapted from line 769 of 3.8.12 ntpath.py
[[c
  for c
  in ary
  if c
  and c != n]
 for s
 in {"a", "b", "c"}]

[c
 for c in ary
 if c
 and c != n
 ]

# Adapted from python3.8/functools.py
[n
 for
 n
 in __file__
 if not n
 ]

# Adapted from python3.8/lib2to3/tests/data/py3_test_grammar.py test_in_func()
[0 <
 ary
 < 3
 for ary
 in __file__
 if ary > 2
 ]

[ord(dir)
 for dir in ary
 for filename in ary2]


# Adapted from Python3.8 lib/python3.8/asyncio/base_events.py
[
    addr_pair for addr_pair in __file__
    if((__name__ and addr_pair) or
            (__file__ and ary))
]

[
     addr_pair for addr_pair in __file__
     if (addr_pair and __name__) or (addr_pair and __file__)]

[l
 for l
 in  ary
 if 2 <=
 l
 <= 8]

# Adapted from 3.8.12 line 730 pywt/_swt.py iswtn()
[{k:
  v.real
  for k, v
  in ary}
 for c
 in ary2]


[
 axis
 or axis
 >= 10
 for axis
 in ary]


# Adapted from lib/python3.8/base64.py
# Warning! check result. If it starts "y" if ... be wery wery careful
["z" if __name__
 else
   "y" if __file__
    and __name__
    else 5
 for word
   in __name__]


# Adapted from 3.8 numpy/ma/mrecords.py
[f"({','.join([str(i) for i in s])})"
 for s
 in [f
     for f
     in ary]
 ]

[f"({','.join([i for i in s])})"
  for s
  in __file__]


# Adapted from 3.8 numpy/lib/function_base.py
[n + tuple(ary2[dim] for dim in core_dims)
            for core_dims in ary2]


# Adapted from 3.8 prompt_toolkit/layout/processors.py
[
 (style,
  5 * len(ary2),
  *ary)
 for style,
 text,
 *handler
 in ary2
]


# Adapted from 3.8 scipy/_lib/_util.py
[
 p
 for p
 in ary
 if p.kind in
 [1, 2]
 ]

[0 <
 ary
 < 3
 for ary
 in __file__
 if ary > 2
 ]

 # # Adapted from 3.8 scipy/linalg/tests/test_lapack.py
# [(dtype, trans)
#  for dtype in DTYPES for trans in ['N', 'T', 'C']
#  if not (trans == 'C' and dtype in REAL_DTYPES)]

# [dtyp
#  for dtyp in __file__
#  if not (__file__
#          and dtyp)]


# # Adapted from 3.8 skiimage/filters/tests/test_thresholding.py
# [axis.texts for axis in ax if axis.texts != []]

# # Adapted from Python 3.8 tqdm/asyncio.py
# # Note we need to add the "async def" for this list comprehension
# async def gather(cls, *fs, loop=None, timeout=None, total=None, **tqdm_kwargs):
#     [await f for f in cls.as_completed(loop=loop, timeout=timeout,
#                                        total=total, **tqdm_kwargs)]


# # Adapted from Python 3.8 sympy/tensor/tensor.py __new__()
# # Warning! produces duplicate if/else

# [i for arg in args for i in (arg.args if isinstance(arg, (TensMul, Mul)) else [arg])]

# [i
#  for arg
#  in __name__
#  for i
#  in (
#      6
#      if __file__
#      else 5)
#      ]

# Adapted from 3.8 sympy/solvers/tests/test_solvers.py test_issue_8828()
[
 {tuple(i.evalf(2)
        for i
        in j)
  for j
  in R}
 for R in
 ["A", "B", "C"]
 ]

[{
  2
        for j in R}
 for R in __file__]

[10
 for
 i in ["a", "b", "c"]
 for __file__
 in i
 or (i,)
 ]

# [i for i in free if (i.name if isinstance(x, str) else i) == x]

# Adapted From 3.8 sympy/geometry/util.py
# (i.name if isinstance(x, str) else i) == x

[5
 if (
    __file__
    or __name__
    ) else 7
 ]

# # And when this is a constant?

# 5 if (
#     __file__
#     # or 6
#     ) else 7


# # Adapted from 3.8 sympy/simplify/trigsimp.py
# # [
# #  _eapply(func, ei) if (cond is None or cond(ei)) else ei
# #  for ei in e.args]

# Adapted from 3.8 matplotlib/dviread.py
# The bug was in handling chained compare (32 < ch < 127)
# inside a "if .. else".

[ch
 if 32 <= ch < 127
 else '<%02x>'
 for ch
 in __file__
 ]

# # Adapted from Python 3.8 matplotlib/tests/test_determinism.py
# [
#  subprocess.check_output(
#      [sys.executable, "-R", "-c",
#       f"from matplotlib.tests.test_determinism import _save_figure;"
#       f"_save_figure({objects!r}, {fmt!r}, {usetex})"],
#      env={**os.environ, "SOURCE_DATE_EPOCH": "946684800",
#           "MPLBACKEND": "Agg"})
#  for _ in range(3)
#  ]

# Adapted from 3.8 test/test_named_expressions.py
[(x, y, x/y)
 for x in [1, 2, 3]
 if (y := x)
 > 0]

# Adapted from Line 159 From 3.8. 12 sympy/concrete/delta.py
 # Bug was probably *() form in function call
[range(*(key, value))
 for key, value
 in [(1, 2), (3, 4)]]
