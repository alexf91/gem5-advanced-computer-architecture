class DummyPredictor(object):
    def __init__(self):
        pass

    def lookup(self, tid, branch_addr, bp_history):
        """Returns a tuple of the prediction and the new bp_history key."""
        return True, 0

    def btbUpdate(self, tid, branch_addr, bp_history):
        """Returns the new bp_history key (in a tuple)."""
        return 0,

    def uncondBranch(self, tid, pc, bp_history):
        """Returns the new bp_history key (in a tuple)."""
        return 0,

    def update(self, tid, branch_addr, taken, bp_history, squashed):
        """Returns nothing."""
        return None

    def squash(self, tid, bp_history):
        """Returns nothing."""
        return None
