"""
Tests
"""

import unittest
import simphony_ui.couple_CFDDEM as cfd_dem


class CFD_DEM(unittest.TestCase):

    def test_run(self):
        try:
            cfd_dem.main()
        except:
            self.fail('Error when running the main script')
