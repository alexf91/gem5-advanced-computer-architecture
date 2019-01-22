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

__all__ = ('MultiHybridPredictor', )

from ..basepredictor import BasePredictor


class MultiHybridPredictor(BasePredictor):
    """A meta-predictor combining multiple other predictors using 2-bit
    counters. For each predictor and address, a two-bit counter is maintained
    and the output of a predictor with a counter value of 3 is chosen. Ties
    are broken by choosing the predictor with the lowest index.
    For the sub-predictors, all methods are called, independent of the
    chosen prediction.
    """
    def __init__(self, predictors, ncounters, **kwargs):
        super(MultiHybridPredictor, self).__init__(**kwargs)

        self._preds = predictors
        self._npreds = len(predictors)
        self._table = [[3 for _ in range(self._npreds)]
                                    for _ in range(ncounters)]

    def lookup(self, tid, branch_addr, bp_history):
        # Create the histories for the sub-predictors. We copy them to get
        # all the additional information from the base predictor. A shallow
        # copy should be enough.
        hists = [bp_history.copy() for _ in range(self._npreds)]
        bp_history['histories'] = hists

        index = self._get_index(branch_addr)

        predictions = []
        for i, pred in enumerate(self._preds):
            p = pred.lookup(tid, branch_addr, bp_history['histories'][i])
            predictions.append(p)

        # Keep track of the predictions. We need this later to update the
        # counters.
        bp_history['predictions'] = predictions

        for i in range(self._npreds):
            if self._table[index][i] == 3:
                return predictions[i]

        assert False

    def uncond_branch(self, tid, branch_addr, bp_history):
        # Create the histories for the sub-predictors. We copy them to get
        # all the additional information from the base predictor. A shallow
        # copy should be enough.
        hists = [bp_history.copy() for _ in range(self._npreds)]
        bp_history['histories'] = hists
        bp_history['predictions'] = [True for _ in range(self._npreds)]

        for i, pred in enumerate(self._preds):
            pred.uncond_branch(tid, branch_addr, bp_history['histories'][i])


    def btb_update(self, tid, branch_addr, bp_history):
        for i, pred in enumerate(self._preds):
            pred.btb_update(tid, branch_addr, bp_history['histories'][i])

    def update(self, tid, branch_addr, taken, bp_history, squashed):
        for i, pred in enumerate(self._preds):
            hist = bp_history['histories'][i]
            pred.update(tid, branch_addr, taken, hist, squashed)

        # Don't do anything on a squashed-update. This method will be called
        # later with squashed = False. Do not update any counters for
        # unconditional branches.
        if squashed or not bp_history['conditional']:
            return

        # Update strategy:
        # * If a counter had the value 3 and was correct, then the counters of
        #   all predictors with a wrong prediction is decreased.
        # * Otherwise, the counters of all correct predictors are increased.
        index = self._get_index(branch_addr)
        predictions = bp_history['predictions']
        counters = self._table[index]

        if any([c == 3 and p == taken for c, p in zip(counters, predictions)]):
            # At least one predictor was correct, so decrement the incorrect
            # ones.
            for i, p in enumerate(predictions):
                if p != taken:
                    counters[i] = max(0, counters[i] - 1)

        else:
            # No predictor with count == 3 was correct, so we increment the
            # counters of the correct ones.
            for i, p in enumerate(predictions):
                if p == taken:
                    counters[i] = min(3, counters[i] + 1)

        assert any([c == 3 for c in counters])


    def squash(self, tid, bp_history):
        for i, pred in enumerate(self._preds):
            pred.squash(tid, bp_history['histories'][i])

    def _get_index(self, branch_addr):
        return ((branch_addr // 4) % len(self._table))
