#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Glances - An eye on your system
#
# Copyright (C) 2019 Nicolargo <nicolas@nicolargo.com>
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

"""Glances unitary tests suite."""

import time
import unittest

from glances.main import GlancesMain
from glances.stats import GlancesStats
from glances import __version__
from glances.globals import WINDOWS, LINUX
from glances.outputs.glances_bars import Bar
from glances.thresholds import GlancesThresholdOk
from glances.thresholds import GlancesThresholdCareful
from glances.thresholds import GlancesThresholdWarning
from glances.thresholds import GlancesThresholdCritical
from glances.thresholds import GlancesThresholds
from glances.plugins.glances_plugin import GlancesPlugin
from glances.compat import subsample, range

# Global variables
# =================


# Init Glances core
core = GlancesMain()

# Init Glances stats
stats = GlancesStats(config=core.get_config(),
                     args=core.get_args())

# Unitest class
# ==============
print('Unitary tests for Glances %s' % __version__)


class TestGlances(unittest.TestCase):
    """Test Glances class."""

    def setUp(self):
        """The function is called *every time* before test_*."""
        print('\n' + '=' * 78)

    def test_000_update(self):
        """Update stats (mandatory step for all the stats).

        The update is made twice (for rate computation).
        """
        print('INFO: [TEST_000] Test the stats update function')
        try:
            stats.update()
        except Exception as e:
            print('ERROR: Stats update failed: %s' % e)
            self.assertTrue(False)
        time.sleep(1)
        try:
            stats.update()
        except Exception as e:
            print('ERROR: Stats update failed: %s' % e)
            self.assertTrue(False)

        self.assertTrue(True)

    def test_001_plugins(self):
        """Check mandatory plugins."""
        plugins_to_check = ['system', 'cpu', 'load', 'mem', 'memswap', 'network', 'diskio', 'fs', 'irq', 'cloudadmin_version']
        print('INFO: [TEST_001] Check the mandatory plugins list: %s' % ', '.join(plugins_to_check))
        plugins_list = stats.getPluginsList()
        for plugin in plugins_to_check:
            self.assertTrue(plugin in plugins_list)

    def test_002_cloudadmin_version(self):
        """Check SYSTEM plugin."""
        stats_to_check = ['version']
        print('INFO: [TEST_002] Check SYSTEM stats: %s' % ', '.join(stats_to_check))
        stats_grab = stats.get_plugin('cloudadmin_version').get_raw()
        for stat in stats_to_check:
            # Check that the key exist
            self.assertTrue(stat in stats_grab, msg='Cannot find key: %s' % stat)
        print('INFO: CLOUDADMIN VERSION version: %s' % stats_grab)

if __name__ == '__main__':
    unittest.main()
