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

__all__ = ('BasePredictor', 'RecordSettings')

import enum

class RecordSettings(enum.IntEnum):
    NONE = 0
    CONDITIONAL = 1
    UNCONDITIONAL = 2
    ALL = 3


class BasePredictor(object):
    """Base class for all predictors. Manages the branch histories.
    Histories are created when the lookup or uncond_branch is called and
    deleted when squash or update without the squashed flag is called.

    :param record_trace: the branch address and taken/not-taken is recorded and
        can be accessed via the trace property.
    """

    trace = property(lambda self: self._trace)

    def __init__(self, **kwargs):
        self._base_histories = dict()
        self._base_history_cnt = 0

        self._record_trace = kwargs.get('record_trace', 0)
        self._trace = []

    def _next_key(self):
        self._base_history_cnt += 1
        return self._base_history_cnt

    def _base_lookup(self, tid, branch_addr, bp_history_index):
        assert bp_history_index == 0
        key = self._next_key()
        bp_history = dict(conditional=True, _index=key)
        self._base_histories[key] = bp_history
        pred = self.lookup(tid, branch_addr, bp_history)
        return pred or False, key

    def _base_uncond_branch(self, tid, branch_addr, bp_history_index):
        assert bp_history_index == 0
        key = self._next_key()
        bp_history = dict(conditional=False, _index=key)
        self._base_histories[key] = bp_history
        self.uncond_branch(tid, branch_addr, bp_history)
        return False, key

    def _base_btb_update(self, tid, branch_addr, bp_history_index):
        assert bp_history_index != 0
        self.btb_update(tid, branch_addr,
                        self._base_histories[bp_history_index])
        return False, bp_history_index

    def _base_update(self, tid, branch_addr, taken, bp_history_index,
                     squashed):
        assert bp_history_index != 0
        bp_history = self._base_histories[bp_history_index]

        if not squashed:
            cond = bp_history['conditional']
            record_cond = self._record_trace & RecordSettings.CONDITIONAL
            record_uncond = self._record_trace & RecordSettings.UNCONDITIONAL

            if (cond and record_cond) or (not cond and record_uncond):
                self._trace.append((branch_addr, taken))

        self.update(tid, branch_addr, taken, bp_history, squashed)
        if not squashed:
            del self._base_histories[bp_history_index]

    def _base_squash(self, tid, bp_history_index):
        assert bp_history_index != 0
        bp_history = self._base_histories[bp_history_index]
        self.squash(tid, bp_history)
        del self._base_histories[bp_history_index]

    def reset_trace(self):
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
