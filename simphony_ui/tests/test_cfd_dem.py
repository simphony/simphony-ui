"""
Tests
"""

import os
import shutil
import tempfile
import unittest
import simphony_ui.couple_CFDDEM as cfd_dem
from simphony.core.cuds_item import CUDSItem
from simphony.core.cuba import CUBA


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

    def test_nb_entities(self):
        dataset1 = self.dem_wrapper.get_dataset(
            self.dem_wrapper.get_dataset_names()[0])
        self.assertEqual(dataset1.count_of(CUDSItem.PARTICLE), 200)
        self.assertEqual(dataset1.count_of(CUDSItem.BOND), 0)

        dataset2 = self.cfd_wrapper.get_dataset(
            self.cfd_wrapper.get_dataset_names()[0])
        self.assertEqual(dataset2.count_of(CUDSItem.CELL), 15744)
        self.assertEqual(dataset2.count_of(CUDSItem.FACE), 63448)
        self.assertEqual(dataset2.count_of(CUDSItem.EDGE), 0)
        self.assertEqual(dataset2.count_of(CUDSItem.POINT), 32432)

    def test_velovity(self):
        dataset = self.cfd_wrapper.get_dataset(
            self.cfd_wrapper.get_dataset_names()[0])
        avg_velo = 0.0
        for cell in dataset.iter_cells():
            avg_velo += cell.data[CUBA.VELOCITY][0]
        avg_velo = avg_velo/dataset.count_of(CUDSItem.CELL)
        self.assertAlmostEqual(avg_velo, 0.00151286)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_dir)
