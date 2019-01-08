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

__all__ = ('Combining2BitPredictor', )

from ..basepredictor import BasePredictor


class Combining2BitPredictor(BasePredictor):
    """A meta-predictor combining two other predictors using 2-bit counters.
    For the sub-predictors, all methods are called, independent of the
    chosen prediction.
    """
    def __init__(self, pred_a, pred_b, ncounters, init=0, **kwargs):
        super(Combining2BitPredictor, self).__init__(**kwargs)

        self._pred_a = pred_a
        self._pred_b = pred_b
        self._table = [init for _ in range(ncounters)]

    def lookup(self, tid, branch_addr, bp_history):
        # Create the histories for the sub-predictors. We copy them to get
        # all the additional information from the base predictor. A shallow
        # copy should be enough.
        hist_a = bp_history.copy()
        hist_b = bp_history.copy()
        bp_history['A'] = hist_a
        bp_history['B'] = hist_b

        index = self._get_index(branch_addr)

        pa = self._pred_a.lookup(tid, branch_addr, bp_history['A'])
        pb = self._pred_b.lookup(tid, branch_addr, bp_history['B'])

        # Keep track of the predictions. We need this later to update the
        # counters.
        bp_history['pa'] = pa
        bp_history['pb'] = pb

        if self._table[index] < 2:
            return pa
        else:
            return pb

    def uncond_branch(self, tid, branch_addr, bp_history):
        # Create the histories for the sub-predictors. We copy them to get
        # all the additional information from the base predictor. A shallow
        # copy should be enough.
        hist_a = bp_history.copy()
        hist_b = bp_history.copy()
        bp_history['A'] = hist_a
        bp_history['B'] = hist_b

        # The counter won't change in this case, so we could just add a flag
        # indicating that the branch was unconditional.
        bp_history['pa'] = True
        bp_history['pb'] = True

        self._pred_a.uncond_branch(tid, branch_addr, bp_history['A'])
        self._pred_b.uncond_branch(tid, branch_addr, bp_history['B'])

    def btb_update(self, tid, branch_addr, bp_history):
        self._pred_a.btb_update(tid, branch_addr, bp_history['A'])
        self._pred_b.btb_update(tid, branch_addr, bp_history['B'])

    def update(self, tid, branch_addr, taken, bp_history, squashed):
        self._pred_a.update(tid, branch_addr, taken, bp_history['A'], squashed)
        self._pred_b.update(tid, branch_addr, taken, bp_history['B'], squashed)

        # Don't do anything on a squashed-update. This method will be called
        # later with squashed = False. We do not ignore unconditional branches
        # here, because a sub-predictor might use them.
        if squashed:
            return

        pa = bp_history['pa']
        pb = bp_history['pb']

        index = self._get_index(branch_addr)
        if pa == taken and pb != taken:
            # The first one is correct, so we decrement the counter
            self._table[index] = max(self._table[index] - 1, 0)
        elif pa != taken and pb == taken:
            # Second one is correct, so we increment the counter
            self._table[index] = min(self._table[index] + 1, 3)
        else:
            # Both correct or incorrect. Counter doesn't change
            assert pa == pb

    def squash(self, tid, bp_history):
        self._pred_a.squash(tid, bp_history['A'])
        self._pred_b.squash(tid, bp_history['B'])

    def _get_index(self, branch_addr):
        return ((branch_addr // 4) % len(self._table))
