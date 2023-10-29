# NOTE: Formatting may be weird because we want the additional line numbers
# in debugging.

# fmt: off

# Here we test the various form of function signatures and funtion calls

# No args
lambda: 1

# positional args
lambda a: a
lambda a, b: a + b

# default values
lambda a, b=b'': a + b
lambda s=b'': s

lambda f, *args: f(args)
lambda func, *args, **kw: func(args, *args, **kw)

lambda func, *args, **kw: func(**kw)

lambda no_apply, *args, **kwargs: no_apply(*args, **kwargs)
lambda no_apply2, *args, **kwargs: no_apply2(1, *args, **kwargs)
lambda no_apply3, *args, **kwargs: no_apply3(1, 2, *args, **kwargs)
lambda no_apply4, *args, **kwargs: no_apply4(x = 11, *args, **kwargs)
lambda no_apply5, *args, **kwargs: no_apply5(34, x = 11, *args, **kwargs)
lambda no_apply6, *args, **kwargs: no_apply6(42, 34, x = 11, *args, **kwargs)
lambda func, *args, **kw: func(*args, **kw)
lambda self, *args, **kw: func(self, *args, **kw)


lambda func, *args, **kw: func(*args,
                                **kw)

lambda self, *args, **kw: func(self,
                               *args,
                               **kw)
