# FIXME: We don't have statements in yet.
# These are an accumulation of lambda expressions involving all of the varied kinds of
# variable parameters.
# They were culled from all lambda's on my disk under Python 3.8.

# NOTE: Formatting may be weird because we want the additional line numbers
# in debugging.

# we can turn this into a self-checking program when we do.
# """This program is self-checking!"""

def func(*args, **kwargs):
    pass

# fmt: off
lambda: globals()
lambda: locals()
lambda d=b'': 5

lambda func, *args, **kw: 5

lambda func, *args, **kw: func(**kw)

lambda no_apply, *args, **kwargs: no_apply(*args, **kwargs)
lambda no_apply, *args, **kwargs: no_apply(1, *args, **kwargs)
lambda no_apply, *args, **kwargs: no_apply(1, 2, *args, **kwargs)
lambda no_apply, *args, **kwargs: no_apply(x = 11, *args, **kwargs)
lambda no_apply, *args, **kwargs: no_apply(34, x = 11, *args, **kwargs)
lambda no_apply, *args, **kwargs: no_apply(42, 34, x = 11, *args, **kwargs)
lambda func, *args, **kw: func(*args, **kw)
lambda self, *args, **kw: func(self, *args, **kw)


lambda func, *args, **kw: func(*args,
                               **kw)

lambda self, *args, **kw: func(self,
                               *args,
                               **kw)


# Numpy code has a rich source of lamddas
lambda x: func(mapdomain(x,
                         window,
                         domain),
               *args)

lambda func, *args, **kw: func(*args,
                               **kw)

lambda self, *args, **kw: func(self,
                               *args,
                               **kw)

lambda s: int(s or -999)

lambda *paths: join(*((sep,)+paths))

# From numpy/polynomial/chebyshev.py
lambda x: func(
    pu(x, window, domain),
    *args)

# From pint/registry.py
lambda x, case_sensitive, values, eval_token: eval_token(
    x,
    case_sensitive=case_sensitive,
    **values)
