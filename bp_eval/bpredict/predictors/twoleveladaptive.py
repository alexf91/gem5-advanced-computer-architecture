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

__all__ = ('TwoLevelAdaptiveTrainingPredictor', )

from ..basepredictor import BasePredictor


class TwoLevelAdaptiveTrainingPredictor(BasePredictor):
    """Predictor with two tables:
        * Per address history register table (PHRT), which is indexed by the
          branch address and stores the history of the branch.
        * Global pattern table, which is indexed by the content of the content
          of the PHRT and contains 2-bit counters.

        Size in bits: (2 * 2**histlength) + (phrtsize * histlength)
    """
    def __init__(self, phrtsize, histlength, **kwargs):
        """
        :param phrtsize: Number of entries in the PHRT.
        :param histlength: Length of the local history registers
        """
        super(TwoLevelAdaptiveTrainingPredictor, self).__init__(**kwargs)

        self._phrtsize = phrtsize
        self._phrt = [0 for _ in range(phrtsize)]
        self._mask = 2**histlength - 1
        self._gpt = [0 for _ in range(2**histlength)]

    def lookup(self, tid, branch_addr, bp_history):
        phrt_index = self._get_index(branch_addr)
        gpt_index = self._phrt[phrt_index]

        # Store the index for the counter we used for later. We need it to
        # update the correct counter when we know the outcome of the branch.
        bp_history['gpt_index'] = gpt_index

        return self._gpt[gpt_index] >= 2

    def update(self, tid, branch_addr, taken, bp_history, squashed):
        # Ignore the squashed update call or unconditional branches
        if squashed or not bp_history['conditional']:
            return

        # Get the GPT entry we used earlier and update it.
        gpt_index = bp_history['gpt_index']
        if taken:
            self._gpt[gpt_index] = min(self._gpt[gpt_index] + 1, 3)
        else:
            self._gpt[gpt_index] = max(self._gpt[gpt_index] - 1, 0)

        # Update the PHRT for the branch address
        index = self._get_index(branch_addr)
        self._phrt[index] = ((self._phrt[index] << 1) | taken) & self._mask

    def _get_index(self, branch_addr):
        return ((branch_addr // 4) % self._phrtsize)
