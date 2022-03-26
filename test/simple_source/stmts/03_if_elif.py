# We have a lot of trouble getting if regions correct.
# This tests that by trying subtle variations.

"""This program is self-checking!"""

# ifstmt and ifelsesmt using with "pass".
# The # "ifsmt" and "ifelsesmt" "then" jump should  exactly
# to the corresponding "endifs".

y = 2
if __name__:
    if __file__:
        pass
    elif __name__:
        pass

y = 1

# Test that the y = 1 assignemnt did not get put somewhere inside the ifstmt or ifelsestmt above.
assert y == 1

y = 2
if __name__:
    if __file__:
        pass
    elif __name__:
        y = 1

# Test that the y = 1 assignemnt got put inside the ifelsestmt above.
assert y == 2

y = 2
if not __name__:
    if __file__:
        pass
    elif __name__:
        pass
    y = 1

# Test that the y = 1 assignemnt got put inside the ifstmt above.
assert y == 2

# Now try with "assert" which introduces "raise" via an "assert" statement
y = 1
if __name__:
    if __file__:
        assert True
    elif __name__:
        assert False
y = 2
assert y == 2
