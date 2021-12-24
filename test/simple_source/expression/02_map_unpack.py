# Python 3.5+ PEP 448 - Additional Unpacking Generalizations for dictionaries

# FIXME: We don't have statements in yet.
# we can turn this into a self-checking program when we do.
# """This program is self-checking!"""
lambda: {**{}}
lambda: {**{'a': 1, 'b': 2}}
lambda: {**{'x': 1}, **{'y': 2}}
lambda c, d: {**{c: 1, d: 2}}
lambda w: (*w, *w)


# {'c': 1, {'d': 2}, **{'e': 3}}
# [*[]]
# FIXME: assert deparsing is incorrect for:
# {**{}, **{}}
# assert {} == {**{}, **{}, **{}}

# {**{}, **{}, **{}}
# assert {} == {**{}, **{}, **{}}
