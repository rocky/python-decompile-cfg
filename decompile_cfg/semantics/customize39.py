#  Copyright (c) 2019-2022 by Rocky Bernstein
#
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
"""
Isolate Python 3.9 version-specific semantic actions here.
"""

########################
# Python 3.9 changes
#######################

from decompile_cfg.semantics.consts import PRECEDENCE


def customize_for_version39(self, version):

    PRECEDENCE["call_ex_39"] = 1

    # Customized hack for now.
    def call_ex_39(node):
        """Handle CALL_FUNCTION_EX {1 or 2}"""
        self.preorder(node[0])
        self.write("(")
        # Handle positional arguments
        # FIXME this probably is not right
        # Do need to add ", " between entries?
        self.preorder(node[1])
        # HACK single dictionary for now.
        self.write("**")
        self.preorder(node[3])
        self.write(")")
        self.prune()

    self.n_call_ex_39 = call_ex_39
