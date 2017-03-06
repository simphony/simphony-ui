"""
Tests
"""

import unittest
import simphony_ui.couple_CFDDEM as cfd_dem
import shutil
import os
import tempfile


class TestCfeDem(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.mesh_name = 'test_mesh'

    def test_output(self):
        cfd_dem.main(self.tmp_dir, self.mesh_name)
        self.assertTrue(os.path.exists(
            os.path.join(self.tmp_dir, self.mesh_name)
        ))

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
