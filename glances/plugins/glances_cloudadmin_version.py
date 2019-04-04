# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Pawel Gieniec <pawel@cloudadmin.io>
#
# Glances is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Glances is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Now (current date) plugin."""

__version__ = '1.0.0'

from glances.plugins.glances_plugin import GlancesPlugin


class Plugin(GlancesPlugin):
    """Plugin to get the current date/time.

    stats is (string)
    """

    def __init__(self, args=None):
        """Init the plugin."""
        super(Plugin, self).__init__(args=args)

        # We want to display the stat in the curse interface
        self.display_curse = False
        self.stats = {}
        self.version = ''

    def reset(self):
        """Reset/init the stats."""
        self.stats = {}

    def update(self):
        """Update current date/time."""
        # Had to convert it to string because datetime is not JSON serializable

        self.stats['cloudadmin_version'] = __version__

        return self.stats