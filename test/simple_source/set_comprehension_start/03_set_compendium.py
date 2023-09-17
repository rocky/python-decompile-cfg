# These are adapted from set comprehensions found when byte compiling the
# entire set of 3.8 installed packages on my disk.
# Many examples come from packages like sympy or numpy

#fmt; off

x = {"abc", "def", "ghi"}
{
 e
 for e
 in
 x
}

{
 e
 for e
 in
 x
 if e == "abc"
}

{
 e
 for e
 in
 x
 if
 e.startswith("a") or e.startswith("d")
}

{
 e
 for e
 in
 x
 if (
     e.startswith("a")
     or e.startswith("d")
     or e.startswith("g")
 )
 }

async def run_set(foo):
    return {
        i
        async
        for i
        in foo
        }

# Line 1860 of Python 3.8.12 test/test_coroutines.py
async def run_dict():
 return {i+1
     async for
     i in
     [10, 20]}

{ e
  for e
  in
  __file__
  if
  a and b and c
}


# Line 1414 of 3.8.12 numpy/distutils/ccompiler_opt.py
{t for n in __file__ for t in ord(n)}

# Start here
# # Line 1278 of 3.8.12 sympy/solvers/solvers.py
# {tuple([s[ki] for ki in k]) for s in solution}

# # Line 3887 of 3.8.12 test/test_typing.py

# {
#     k for k, v in vars(typing).items()
#     # explicitly exported, not a thing with __module__
#     if k in __file__ or (
#         # avoid private names
#         not k.startswith('_') and
#         # avoid things in the io / re typing submodules
#         k not in typing.io.__all__ and
#         k not in typing.re.__all__ and
#         k not in {'io', 're'} and
#         # there's a few types and metaclasses that aren't exported
#         not k.endswith(('Meta', '_contra', '_co')) and
#         not k.upper() == k and
#         # but export all things that have __module__ == 'typing'
#         getattr(v, '__module__', None) == typing.__name__
#     )
# }

# # With "not" fails on decompyle3
# {
#     k for k, v in typing
#     if k in __file__ or (
#         k and
#         hasattr(v, '__module__')
#     )
# }

# # Without "not" succeeds on decompyle3
# {
#     k for k, v in typing
#     if k in __file__ or (
#         not k and
#         hasattr(v, '__module__')
#     )
# }
