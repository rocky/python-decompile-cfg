# These are adapted from set comprehensions found when byte compiling the
# entire set of 3.8 installed packages on my disk.
# Many examples come from packages like sympy or numpy
# RUNNABLE!

"""This program is self-checking!"""

#fmt; off

x = {"abc", "def", "ghi"}
assert {
    e
    for e
    in
    x
    } == x

assert {
    e
    for e
    in
    x
    if e == "abc"
} == {"abc"}


assert {
    e
    for e
    in
    x
    if
    e.startswith("a") or e.startswith("d")
} == {"abc", "def"}

assert {
    e
    for e
    in
    x
    if (
        e.startswith("a")
        or e.startswith("d")
        or e.startswith("g")
        )
} == x


assert {
    e
    for e
    in
    x
    if
    e.startswith("a") and e.endswith("c")
} == {"abc"}


# assert {
#     e
#     for e
#     in
#     x
#     if
#     e.startswith("a") and e.endswith("c") and e == "abc"
# } == {"abc"}

assert {i for pair in
     [[10, 20], [30, 40]]
         for i in
         pair} == [40, 10, 20, 30]
