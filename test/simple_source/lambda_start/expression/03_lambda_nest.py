# From Python 3.8 line 447 of site-packages/nltk/tgrep.py

# NOTE: Formatting may be weird because we want the additional line numbers
# in debugging.

# fmt: off
def _istree(obj):
    return 5

(
    lambda i: lambda n, m=None: (
        _istree(n)
        and bool(list(n))
        and 0 <= i
        < len(n)
        and ord(n)
        )
        )(10)


[(lambda a, b:
  [a for
   i in
   b])(
       j)
 for j in
 (1,2,3)
 ]
