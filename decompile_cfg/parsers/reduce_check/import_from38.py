#  Copyright (c) 2022 Rocky Bernstein
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


def import_from38_ok(
    self, lhs: str, n: int, rule, tree, tokens: list, first: int, last: int
) -> bool:
    """
    Returns True if we can't find any reason to disallow an "import_from38" reduction.
    """
    importlist38 = tree[3]
    alias38 = importlist38[0]
    if importlist38 == "importlist38" and alias38 == "alias38":
        store = alias38[1]
        assert store == "store"
        return alias38[0].attr == store[0].attr
    return True
