# These are an accumulation of dict comprehensions.
# They were culled from all list comprehensions on my disk under Python 3.8.

# fmt: off

{ e:5
  for e
  in
  __file__
}

{ e:5
  for e
  in
  ("abc", "def")
}

{ e: 6
  for e
  in
  ("abc", "def")
  if
  __name__
}

{ e: 7
  for e
  in
  ("abc", "def")
  if
  __name__ or ("abc", "def")
}

{ e: 8
  for e
  in
  ("abc", "def")
  if
  __name__ or ("abc", "def") or max(("abc", "def"), __name__)
}

async def run_dict2(foo):
    return {
        i:
        8
        async
        for i
        in foo
        }

# # From Python 3.8 sre_compile.py line 62
# {i:
#  tuple(j
#        for j
#        in t
#        if i != j)
#  for t
#  in __file__
#  for i
#  in t}


# # line 36 of from Python 3.8 spacy/tests/regression/test_issue4190.py
# # The problem is in "if_not"
# {
#     k: v
#     for k, v in
#     __file__
#     if not
#     (k
#      and v)
#     }

# # Note this is the same as" if not .. if ...
# {
#     k: v
#     for k, v in
#     __file__
#     if not k
#     if v
#     }

# # line 39 or 3.8.12 dateutil/zoneinfo/__init__.py
# # problem was handling "or" in comprehension
# {
#  zl.name: zl.linkname
#  for
#  zl in __file__
#  if
#     zl.name or zl.foo}

# # Line 39 of 3.8.12 pre_commit/git.py
# # problem was handling " not (... or.. )" in comprehension
# {k: v for k, v in __file__
#  if not k.startswith('GIT_') or
#  k in {
#      'GIT_EXEC_PATH'}
# }


# # Line 1866 of 3.8.12 test/test_coroutines.py
# async def run_dict():
#     return {i + 1: i + 2 async for i in [10, 20]}

# # Line 19266 of 3.8.12 test/test_coroutines.py

# async def run_dict2():
#     {i:
#      i
#      async
#      for i in range(5)
#      if 0 <
#      i < 4}
