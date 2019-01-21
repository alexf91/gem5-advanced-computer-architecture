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

__all__ = ('GSkewPredictor', )

from ..basepredictor import BasePredictor


class HashFunctions(object):
    def __init__(self, n):
        self.n = n
        self.mask = 2**n - 1

    def H(self, v):
        top = (v ^ (v >> (self.n - 1))) & 0x01
        return (top << (self.n - 1)) | (v >> 1)

    def Hinv(self, v):
        bot = (v ^ (v << 1)) >> (self.n - 1)
        return ((v << 1) | bot) & self.mask

    def h1(self, addr, ghr):
        return self.H(addr) ^ self.Hinv(ghr) ^ ghr

    def h2(self, addr, ghr):
        return self.H(addr) ^ self.Hinv(ghr) ^ addr

    def h3(self, addr, ghr):
        return self.Hinv(addr) ^ self.H(ghr) ^ ghr


class GSkewPredictor(BasePredictor):
    """2-bit counters indexed by different hashing functions and a majority
    voter.
    The hash functions take the branch address and the global history as an
    argument.
    """
    def __init__(self, histlength, hash_fncs=None, **kwargs):
        super(GSkewPredictor, self).__init__(**kwargs)

        self._histlength = histlength
        if hash_fncs is None:
            hf = HashFunctions(histlength)
            hash_fncs = [hf.h1, hf.h2, hf.h3]
        self._hash_fncs = hash_fncs
        self._npreds = len(hash_fncs)

        self._tables = [[3 for _ in range(2**histlength)] for _ in hash_fncs]
        self._ghr = 0
        self._mask = 2**histlength - 1

    def lookup(self, tid, branch_addr, bp_history):
        predictions = []
        for i, hash_fnc in enumerate(self._hash_fncs):
            index = hash_fnc(branch_addr & self._mask, self._ghr)
            predictions.append(self._tables[i][index] >= 2)

        return sum(predictions) >= self._npreds / 2

    def update(self, tid, branch_addr, taken, bp_history, squashed):
        if squashed:
            return

        for i, hash_fnc in enumerate(self._hash_fncs):
            index = hash_fnc(branch_addr & self._mask, self._ghr)
            if taken:
                self._tables[i][index] = min(self._tables[i][index] + 1, 3)
            else:
                self._tables[i][index] = max(self._tables[i][index] - 1, 0)

        self._ghr = ((self._ghr << 1) | taken) & self._mask
