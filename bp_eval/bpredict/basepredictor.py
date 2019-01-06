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

__all__ = ('BasePredictor', )


class BasePredictor(object):
    """Base class for all predictors. Manages the branch histories.
    Histories are created when the lookup or uncond_branch is called and
    deleted when squash or update without the squashed flag is called.

    :param record_trace: if set to True, the branch address and taken/not-taken
        is recorded and can be accessed via the trace property.
    """

    trace = property(lambda self: self._trace)

    def __init__(self, **kwargs):
        self._histories = dict()
        self._history_cnt = 0

        self._trace = [] if kwargs.get('record_trace', False) else None

    def _next_key(self):
        self._history_cnt += 1
        return self._history_cnt

    def _base_lookup(self, tid, branch_addr, bp_history_index):
        assert bp_history_index == 0
        bp_history = dict()
        key = self._next_key()
        self._histories[key] = bp_history
        pred = self.lookup(tid, branch_addr, bp_history)
        return pred or False, key

    def _base_uncond_branch(self, tid, branch_addr, bp_history_index):
        assert bp_history_index == 0
        bp_history = dict()
        key = self._next_key()
        self._histories[key] = bp_history
        self.uncond_branch(tid, branch_addr, bp_history)
        return False, key

    def _base_btb_update(self, tid, branch_addr, bp_history_index):
        assert bp_history_index != 0
        self.btb_update(tid, branch_addr, self._histories[bp_history_index])
        return False, bp_history_index

    def _base_update(self, tid, branch_addr, taken, bp_history_index,
                     squashed):
        assert bp_history_index != 0
        bp_history = self._histories[bp_history_index]
        if self._trace is not None and not squashed:
            self._trace.append((branch_addr, taken))
        self.update(tid, branch_addr, taken, bp_history, squashed)
        if not squashed:
            del self._histories[bp_history_index]

    def _base_squash(self, tid, bp_history_index):
        assert bp_history_index != 0
        bp_history = self._histories[bp_history_index]
        self.squash(tid, bp_history)
        del self._histories[bp_history_index]

    def reset_trace(self):
        if self.trace is not None:
            self.trace = []

    ###########################################################################
    # The following methods should be overridden.                             #
    ###########################################################################

    def lookup(self, tid, branch_addr, bp_history):
        return True

    def uncond_branch(self, tid, branch_addr, bp_history):
        pass

    def btb_update(self, tid, branch_addr, bp_history):
        pass

    def update(self, tid, branch_addr, taken, bp_history, squashed):
        pass

    def squash(self, tid, bp_history):
        pass
