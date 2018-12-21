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

import hashlib

from .basepredictor import BasePredictor
from .utils import SaturatingCounter


class Local2BitPredictor(BasePredictor):
    """The number of counters is size_in_bytes * 4"""
    def __init__(self, size_in_bytes):
        super(Local2BitPredictor, self).__init__()

        ncounters = size_in_bytes * 4
        self._table = [SaturatingCounter(0, 3) for _ in range(ncounters)]

    def lookup(self, tid, branch_addr, bp_history):
        index = self._get_index(branch_addr)
        return self._table[index].value >= 2

    def update(self, tid, branch_addr, taken, bp_history, squashed):
        if squashed:
            return

        index = self._get_index(branch_addr)
        if taken:
            self._table[index].increment()
        else:
            self._table[index].decrement()

    def _get_index(self, branch_addr):
        return ((branch_addr // 4) % len(self._table))
