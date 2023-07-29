lambda a: not a

lambda a, b: a and b
lambda a, b, c: a and b and c
lambda a, b, c, d:  a and b and c and d
lambda a, b, c, d, e:  a and b and c and d and e

# lambda a, b: a or b
# lambda a, b, c: a or b or c
# lambda a, b, c, d:  a or b or c or d

# Mixed and/or
# lambda a, b, c:  (a and b) or c
# lambda a, b, c:  a and (b or c)

# lambda a, b, c:  (a or b) and c
# lambda a, b, c:  a or (b and c)

# Mixed and/not

# lambda a, b, c:  a and b and not c
# lambda a, b, c:  a and b or not c

# lambda a, b, c:  a or b and not c
# lambda a, b, c:  a or b or not c
