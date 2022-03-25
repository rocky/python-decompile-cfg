"""This program is self-checking!"""

# We use line breaks to assist marking bytecode sections
# fmt: off
a = (
    "True" if (
    __name__ == "__main__"
    ) else (
        False)
    )

assert a == "True"
