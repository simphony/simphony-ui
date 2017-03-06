"""
Tests
"""

import unittest
import simphony_ui.couple_CFDDEM as cfd_dem
import shutil
import os
import tempfile


class TestCfeDem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = tempfile.mkdtemp()
        cls.mesh_name = 'test_mesh'
        cls.dem_wrapper, cls.cfd_wrapper = \
            cfd_dem.main(cls.tmp_dir, cls.mesh_name)

    def test_output(self):
        self.assertTrue(os.path.exists(
            os.path.join(self.tmp_dir, self.mesh_name)
        ))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_dir)
