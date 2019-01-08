#
# Copyright 2018 Alexander Fasching
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""
Sample implementation of the local 2-bit predictor provided by gem5.
"""

__all__ = ('Local2BitPredictor', )

from ..basepredictor import BasePredictor


class Local2BitPredictor(BasePredictor):
    """A predictor with local histories and 2-bit counters."""
    def __init__(self, ncounters, **kwargs):
        super(Local2BitPredictor, self).__init__(**kwargs)

        self._ncounters = ncounters
        self._table = [3 for _ in range(ncounters)]

    def lookup(self, tid, branch_addr, bp_history):
        index = self._get_index(branch_addr)
        return self._table[index] >= 2

    def update(self, tid, branch_addr, taken, bp_history, squashed):
        # Ignore the squashed update call or unconditional branches
        if squashed or not bp_history['conditional']:
            return

        index = self._get_index(branch_addr)
        if taken:
            self._table[index] = min(self._table[index] + 1, 3)
        else:
            self._table[index] = max(self._table[index] - 1, 0)

    def _get_index(self, branch_addr):
        return ((branch_addr // 4) % self._ncounters)
