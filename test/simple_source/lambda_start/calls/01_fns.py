# FIXME: We don't have statements in yet.
# we can turn this into a self-checking program when we do.
# """This program is self-checking!"""
lambda: globals()
lambda: locals()
lambda d=b'': 5

# Numpy code has a rich source of lamddas
lambda x: func(mapdomain(x, window, domain), *args)
lambda func, *args, **kw: func(*args, **kw)
lambda self, *args, **kw: func(self, *args, **kw)
lambda s: int(s or -999)
lambda *paths: join(*((sep,)+paths))
