# Tests custom added grammar rule:
#   expr ::= expr {expr}^n CALL_FUNCTION_n
# which in the specific case below is:
#   expr ::= expr expr expr CALL_FUNCTION_2

"""This program is self-checking!"""
assert globals()
assert max(1, 2) == 2
assert max(1, 2, 3) == 3

assert min(*[1,2,3]) == 1
assert min(*[1,2,3], *[0, 10, 20]) == 0

#   call_stmt ::= expr POP_TOP
#   build_list ::= expr expr BUILD_LIST_2
#   kwarg ::= LOAD_CONST expr
#   call_function ::= expr expr kwarg kwarg CALL_FUNCTION

assert sorted([1,2], reverse=True, key=None)

assert (lambda x: x.keys())(dict(zip(range(4), range(4)))) == set(range(4))


# Adapted from decompyle's test_appyEquiv.py

def kwfunc(**kwargs):
    return(kwargs.items())


def argsfunc(*args):
    return(args)


def argsfunc(*args):
    return(args)

def no_apply(*args, **kwargs):
    return args, kwargs

def args_kwargs_test(*args, **kwargs):
    assert argsfunc(34) == (34,)
    assert argsfunc(*args) == (1, 2, 4, 8)
    assert argsfunc(34, *args) == (34, 1, 2, 4, 8)
    assert not kwfunc(**{})
    assert dict(kwfunc(x = 11, **{})) == {"x": 11}
    assert no_apply(*args, **kwargs) == ((1, 2, 4, 8), {'a': 2, 'b': 3, 'c': 5})
    assert no_apply(34, *args, **kwargs) == ((34, 1, 2, 4, 8), {'a': 2, 'b': 3, 'c': 5})
    assert no_apply(x = 11, *args, **kwargs) == ((1, 2, 4, 8), {'x': 11, 'a': 2, 'b': 3, 'c': 5})
    assert no_apply(34, x = 11, *args, **kwargs) == ((34, 1, 2, 4, 8), {'x': 11, 'a': 2, 'b': 3, 'c': 5})
    assert no_apply(42, 34, x = 11, *args, **kwargs) == ((42, 34, 1, 2, 4, 8), {'x': 11, 'a': 2, 'b': 3, 'c': 5})

args_kwargs_test(1, 2, 4, 8, a = 2, b = 3, c = 5)
