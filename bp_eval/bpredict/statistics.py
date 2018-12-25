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

from collections import namedtuple
import re

__all__ = ('Statistics', )

Entry = namedtuple('Entry', ['name', 'values', 'description'])

class Statistics(object):
    """Access to gem5 results."""
    rows = property(lambda self: self._rows)

    def __init__(self, statstr):
        self._rows = (self._convert_row(r) for r in statstr.split('\n'))
        self._rows = list(filter(None, self._rows))

    def find(self, pattern):
        return [row for row in self.rows if re.findall(pattern, row.name)]

    def _convert_row(self, row):
        try:
            firstpart, comment = row.split('#')
            comment = comment.strip()

            name, valstr = firstpart.split(maxsplit=1)
            values = tuple(self._convert_value(s) for s in valstr.split())

            return Entry(name, values, comment)

        except ValueError:
            return None

    def _convert_value(self, s):
        s = s.strip()
        if s.endswith('%'):
            return float(s[:-1]) / 100

        try:
            return int(s)
        except ValueError:
            return float(s)

    def __iter__(self):
        for row in self.rows:
            yield row

