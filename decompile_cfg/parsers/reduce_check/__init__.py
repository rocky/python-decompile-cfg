"""
Here we have checks done before a grammar rule reduction for that nonterminal takes place.

These check the validity of rule reduction based on properties that aren't in
the tokens. These checks basically have full access to everything.
Optionally it can have access to the tree built for the reduction nonterminal
it checks.
"""


from decompile_cfg.parsers.reduce_check.joined_str_check import joined_str_ok

__all__ = [
    "joined_str_ok",
]
