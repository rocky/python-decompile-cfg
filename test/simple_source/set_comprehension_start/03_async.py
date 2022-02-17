# These are an accumulation of set comprehensions using "async" or "await.
# They were adapted from list comprehensions under Python 3.8.

# From Python 3.8 tqdm/asyncio.py
# Note we need to add the "async def" for this list comprehension

# fmt: off

# Line 1860 of Python 3.8.12 test/test_coroutines.py

async def run_dict():
 return {i + 1 async for i in [10, 20]}


# # Adapted from line 1890 of Python 3.8.12/ test/test_coroutines.py
# # Problem was hooking in top-level return_expr_lambda hooking into genexpr_func_async

# async def run_set():
#     return {
#         i
#         async
#         for i
#         in [10, 20]
#         if i >
#         10
#         }

# async def gather(cls, *fs, loop=None, timeout=None, total=None, **tqdm_kwargs):
#     {await f
#      for f in
#      cls.as_completed(
#          loop=loop,
#          total=total,
#          **tqdm_kwargs)}


# # From Python 3.8 test/test_asyncgen.py
# async def arange(n):
#     {i
#      async
#      for i
#      in range(10)
#      }

# # From Python 3.8 test/test_coroutines.py

# async def make_brange(n):
#     return {i * 2
#             async
#             for i
#             in range(20)}

# # We were not parsing the "if" as one unit.
# async def run_list():
#     return {i
#             async for i
#             in range(5)
#             if 0 <
#             i <
#             4}

# # FIXME - formatting "async for" is not correct
# # Another "if" parsing problem
# async def run_list2():
#     return {i + 1
#         for pair in
#         ([10, 20], [30, 40])
#         if pair > 10
#         async
#         for i in
#         ord(pair)
#         if i > 30}


# async def run_list3():
#     return {i
#             async for i
#             in range(5)
#             if 0 <
#             i <
#             4}

# # Adapted from line 2071 of 3.8.12 lib/python3.8/test/test_coroutines.py
# # The bug was in the iterator tgt[0] which needs a
# # store_subscript rule.
# async def run_list4(tgt):
#     return {0
#             async for
#             tgt[0] in
#             __file__
#             }
