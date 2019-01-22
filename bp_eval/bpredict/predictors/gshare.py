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
        self._spec = []
        self._mask = 2**histlength - 1

    def lookup(self, tid, branch_addr, bp_history):
        index = self._get_spec_index(branch_addr)
        p = self._table[index] >= 2
        self._spec.append(p)
        return p

    def btb_update(self, tid, branch_addr, bp_history):
        """Set the outcome of the last speculative prediction to not taken."""
        if bp_history['conditional']:
            self._spec[-1] = 0

    def squash(self, tid, bp_history):
        """Squashing starts at the tip of the current path, so we remove the
        last element from the speculative history.
        """
        # TODO: This is only called for the MinorCPU?
        if bp_history['conditional']:
            self._spec.pop()

    def update(self, tid, branch_addr, taken, bp_history, squashed):
        if squashed or not bp_history['conditional']:
            return

        index = self._get_index(branch_addr)
        if taken:
            self._table[index] = min(self._table[index] + 1, 3)
        else:
            self._table[index] = max(self._table[index] - 1, 0)

        self._ghr = ((self._ghr << 1) | taken) & self._mask
        self._spec.pop(0)

    def _get_index(self, branch_addr):
        return ((branch_addr // 4) ^ self._ghr) & self._mask

    def _get_spec_index(self, branch_addr):
        n = len(self._spec)
        th = sum(2**(n - i - 1) * t for i, t in enumerate(self._spec))
        ghr = ((self._ghr << n) | th) & self._mask
        return ((branch_addr // 4) ^ ghr) & self._mask
