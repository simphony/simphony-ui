"""
Tests
"""

import unittest
import simphony_ui.couple_CFDDEM as cfd_dem
import shutil
import os


class TestCfeDem(unittest.TestCase):

    def setUp(self):
        self.output_dir = 'test_mesh'

    def test_output(self):
        cfd_dem.main()
        self.assertTrue(os.path.exists(self.output_dir))

    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)