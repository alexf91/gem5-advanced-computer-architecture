#
# Copyright 2019 Alexander Fasching
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

__all__ = ('GSelectPredictor', )

from ..basepredictor import BasePredictor


class GSelectPredictor(BasePredictor):
    """2-bit counters indexed the concatenated PC and GH."""
    def __init__(self, histlength, addrlength, **kwargs):
        super(GSelectPredictor, self).__init__(**kwargs)

        self._histlength = histlength
        self._addrlength = addrlength

        self._histmask = 2**histlength - 1
        self._addrmask = 2**addrlength - 1

        self._table = [3 for _ in range(2**(histlength + addrlength))]
        self._ghr = 0

    def lookup(self, tid, branch_addr, bp_history):
        index = self._get_index(branch_addr)
        return self._table[index] >= 2

    def update(self, tid, branch_addr, taken, bp_history, squashed):
        if squashed:
            return

        index = self._get_index(branch_addr)
        if taken:
            self._table[index] = min(self._table[index] + 1, 3)
        else:
            self._table[index] = max(self._table[index] - 1, 0)

        self._ghr = ((self._ghr << 1) | taken) & self._histmask

    def _get_index(self, branch_addr):
        addrbits = (branch_addr >> 2) & self._addrmask
        return (addrbits << self._histlength) | self._ghr
