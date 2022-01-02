# FIXME: We don't have statements in yet.
# we can turn this into a self-checking program when we do.
# """This program is self-checking!"""

# Simple list commprehensions

# Add line spacing to assist in seeing which parts go where
# in assembly and code

lambda x: [
    i
    for i
    in x]

lambda n: [
    i * i
    for i
    in range(n)
    ]

lambda n: [
    b
    for b
    in (0, 1, 2, 3)] if (
        __name__ == "__main__"
        ) else 5

# Variable "i" is not bound, so this is handled as a closure.
lambda n: [
    i * i
    for i
    in range(n)
    if n]

lambda p: ''.join(unichr(c) for c in range(ord(p[0]), ord(p[1]) + 1))

lambda p: p if not isinstance(p, ParseResults) else ''.join(unichr(c) for c in range(ord(p[0]), ord(p[1]) + 1))
