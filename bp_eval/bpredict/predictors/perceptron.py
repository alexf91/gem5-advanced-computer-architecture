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
Perceptron predictor suitable for hardware implementation. Only relies on
saturating integer arithmetic.
"""

__all__ = ('PerceptronPredictor', 'LocalPerceptronPredictor')

import numpy as np
from ..basepredictor import BasePredictor


class Perceptron(object):
    """Implementation of a perceptron with optional clipping."""
    def __init__(self, length, threshold=1.0, clip=np.infty):
        self._weights = np.zeros(length + 1)
        self._weights[0] = 1.0
        self._threshold = threshold
        self._clip = clip

    def predict(self, history):
        """Get a prediction based on the history."""
        hist = np.concatenate(([1], history))
        return np.dot(self._weights, hist) >= 0

    def update(self, history, taken):
        """Update the perceptron once the output of a branch is known.
        :param taken: -1 if the branch was not taken and 1 if it was taken.
        """
        hist = np.concatenate(([1], history))
        y = np.dot(self._weights, hist)
        if np.sign(y) != np.sign(taken) or abs(y) < self._threshold:
            diff = self._weights + taken * hist
            self._weights = np.clip(diff, -self._clip, self._clip)


class PerceptronPredictor(BasePredictor):
    """A perceptron predictor with optional support for a speculative history.
    If speculation is enabled, the predictor tracks its predictions and uses
    them for further predictions. The weights are only updated when the outcome
    of a branch is known.
    """
    def __init__(self, nperceptrons, histlength, threshold=1.0, clip=np.infty,
                 speculative=False):
        super(PerceptronPredictor, self).__init__()
        self._nperceptrons = nperceptrons
        self._histlength = histlength
        self._globalhistory = np.zeros(histlength)

        self._table = [Perceptron(histlength, threshold=threshold, clip=clip)
                            for _ in range(nperceptrons)]

        # The predictor tracks predictions not yet commited (update not called)
        # and bases speculative predictions based on this temporary history.
        # Assume that the speculative history is unbounded for simplicity.
        self._speculative = speculative
        self._spechistory = []

    def lookup(self, tid, branch_addr, bp_history):
        index = self._get_index(branch_addr)

        hist = self._globalhistory
        if self._speculative:
            temphist = np.concatenate((self._globalhistory, self._spechistory))
            hist = temphist[-self._histlength:]

        p =  self._table[index].predict(hist)

        if self._speculative:
            self._spechistory.append(1 if p else -1)

        return p

    def btb_update(self, tid, branch_addr, bp_history):
        """Set the outcome of the last speculative prediction to not taken."""
        if bp_history['conditional'] and self._speculative:
            self._spechistory[-1] = -1

    def squash(self, tid, bp_history):
        """Squashing starts at the tip of the current path, so we remove the
        last element from the speculative history.
        """
        # TODO: This is only called for the MinorCPU?
        if bp_history['conditional'] and self._speculative:
            self._spechistory.pop()

    def update(self, tid, branch_addr, taken, bp_history, squashed):
        # Ignore the squashed update call or unconditional branches
        if squashed or not bp_history['conditional']:
            return

        index = self._get_index(branch_addr)
        t = 1 if taken else -1
        self._table[index].update(self._globalhistory, t)

        if self._speculative:
            self._spechistory.pop(0)

        self._globalhistory = np.roll(self._globalhistory, -1)
        self._globalhistory[-1] = t

    def _get_index(self, branch_addr):
        return ((branch_addr // 4) % len(self._table))


class LocalPerceptronPredictor(BasePredictor):
    """A perceptron predictor using the local branch history with optional
    support for a speculative history.
    If speculation is enabled, the predictor tracks its predictions and uses
    them for further predictions. The weights are only updated when the outcome
    of a branch is known.
    """
    def __init__(self, nperceptrons, histlength, threshold=1.0, clip=np.infty,
                 speculative=False):
        super(LocalPerceptronPredictor, self).__init__()
        self._nperceptrons = nperceptrons
        self._histlength = histlength
        self._histories = [np.zeros(histlength) for _ in range(nperceptrons)]

        self._table = [Perceptron(histlength, threshold=threshold, clip=clip)
                            for _ in range(nperceptrons)]

        # The predictor tracks predictions not yet commited (update not called)
        # and bases speculative predictions based on this temporary history.
        # Assume that the speculative history is unbounded for simplicity.
        self._speculative = speculative
        self._spechistory = [[] for _ in range(nperceptrons)]

    def lookup(self, tid, branch_addr, bp_history):
        index = self._get_index(branch_addr)

        hist = self._histories[index]
        if self._speculative:
            temphist = np.concatenate((hist, self._spechistory[index]))
            hist = temphist[-self._histlength:]

        p =  self._table[index].predict(hist)

        if self._speculative:
            self._spechistory[index].append(1 if p else -1)

        return p

    def btb_update(self, tid, branch_addr, bp_history):
        """Set the outcome of the last speculative prediction to not taken."""
        if bp_history['conditional'] and self._speculative:
            index = self._get_index(branch_addr)
            self._spechistory[index][-1] = -1

    def squash(self, tid, bp_history):
        """Squashing starts at the tip of the current path, so we remove the
        last element from the speculative history.
        """
        # TODO: This is only called for the MinorCPU?
        if bp_history['conditional'] and self._speculative:
            index = self._get_index(branch_addr)
            self._spechistory[index].pop()

    def update(self, tid, branch_addr, taken, bp_history, squashed):
        # Ignore the squashed update call or unconditional branches
        if squashed or not bp_history['conditional']:
            return

        index = self._get_index(branch_addr)
        t = 1 if taken else -1
        self._table[index].update(self._histories[index], t)

        if self._speculative:
            self._spechistory[index].pop(0)

        self._histories[index] = np.roll(self._histories[index], -1)
        self._histories[index][-1] = t

    def _get_index(self, branch_addr):
        return ((branch_addr // 4) % len(self._table))
