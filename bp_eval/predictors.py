class DummyPredictor(object):
    def __init__(self):
        self.addresses = set()

    def lookup(self, tid, branch_addr, bp_history):
        """Returns a tuple of the prediction and the new bp_history key."""
        self.addresses.add(branch_addr)
        return True, 0

    def btbUpdate(self, tid, branch_addr, bp_history):
        """Returns the new bp_history key (in a tuple)."""
        self.addresses.add(branch_addr)
        return 0,

    def uncondBranch(self, tid, pc, bp_history):
        """Returns the new bp_history key (in a tuple)."""
        return 0,

    def update(self, tid, branch_addr, taken, bp_history, squashed):
        """Returns nothing."""
        self.addresses.add(branch_addr)
        return None

    def squash(self, tid, bp_history):
        """Returns nothing."""
        return None

    def print_statistics(self):
        print('DummyPredictor:')
        print('    number_of_addresses = %d' % len(self.addresses))



class SaturatingCounter(object):
    def __init__(self):
        self.cnt = 0

    def up(self):
        self.cnt = min(self.cnt + 1, 3)

    def down(self):
        self.cnt = max(self.cnt - 1, 0)

    def msb(self):
        return bool(self.cnt & 0x02)


class Local2Bit(object):
    def __init__(self, size_in_bytes):
        ncounters = size_in_bytes * 4
        self.table = [SaturatingCounter() for _ in range(ncounters)]
        self.cnt = 0

    def lookup(self, tid, branch_addr, bp_history):
        """Returns a tuple of the prediction and the new bp_history key."""
        assert bp_history == 0
        idx = (branch_addr >> 2) % len(self.table)
        pred = self.table[idx].msb()
        return pred, 0

    def btbUpdate(self, tid, branch_addr, bp_history):
        """UNUSED. Returns the new bp_history key (in a tuple)."""
        assert bp_history == 0
        return 0,

    def uncondBranch(self, tid, pc, bp_history):
        """UNUSED. Returns the new bp_history key (in a tuple)."""
        assert bp_history == 0
        return 0,

    def update(self, tid, branch_addr, taken, bp_history, squashed):
        """Returns nothing."""
        assert bp_history == 0
        if squashed:
            return None

        idx = (branch_addr >> 2) % len(self.table)
        if taken:
            self.table[idx].up()
        else:
            self.table[idx].down()

        return None

    def squash(self, tid, bp_history):
        """UNUSED. Returns nothing."""
        assert bp_history == 0
        return None

    def print_statistics(self):
        print('Local2Bit: No stats')
