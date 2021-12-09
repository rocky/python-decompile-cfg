# FIXME: We don't have statements in yet.
# we can turn this into a self-checking program when we do.
# """This program is self-checking!"""

lambda x: 1 < x < 2
lambda x, y: 1 <= x <= 2 >= y
lambda x, y: 1 < x > 2 == 2 <= y <= 3
lambda x, y: 1 < x > 2 == 2 <= y <= 3
lambda x: "0" <= x <= "9" or "a" <= x <= "f"
lambda x, y: "0" <= x <= "9" and "a" <= y <= "f"
