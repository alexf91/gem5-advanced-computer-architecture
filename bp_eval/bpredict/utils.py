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

__all__ = ('SaturatingCounter', 'History')


class SaturatingCounter(object):
    value = property(lambda self: self._value)

    def __init__(self, minval, maxval, init=None):
        assert init is None or minval <= init <= maxval
        self._minval = minval
        self._maxval = maxval
        self._value = init or minval

    def increment(self):
        self._value = min(self._value + 1, self._maxval)

    def decrement(self):
        self._value = max(self._value - 1, self._minval)


class History(object):
    value = property(lambda self: self._value)

    def __init__(self, length):
        self._length = length
        self._value = 0

    def update(self, taken):
        self._value = ((self._value << 1) | taken) & ((1 << self._length) - 1)
