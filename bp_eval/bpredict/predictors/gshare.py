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

__all__ = ('GSharePredictor', )

from ..basepredictor import BasePredictor


class GSharePredictor(BasePredictor):
    """2-bit counters indexed by GH^PC."""
    def __init__(self, histlength, **kwargs):
        super(GSharePredictor, self).__init__(**kwargs)

        self._histlength = histlength
        self._table = [3 for _ in range(2**histlength)]
        self._ghr = 0
        self._mask = 2**histlength - 1

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

        self._ghr = ((self._ghr << 1) | taken) & self._mask

    def _get_index(self, branch_addr):
        return ((branch_addr // 4) ^ self._ghr) & self._mask
