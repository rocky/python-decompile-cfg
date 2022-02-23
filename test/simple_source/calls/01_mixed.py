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
