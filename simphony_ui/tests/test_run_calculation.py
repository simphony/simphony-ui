"""
Tests
"""

import os
import tempfile
import unittest
from simphony.core.cuds_item import CUDSItem
from simphony.core.cuba import CUBA
from simphony_ui.ui import Application
from simphony_ui.tests.test_utils import cleanup_garbage


class TestCalculation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app_parameters = Application()

        cls.app_parameters.openfoam_settings.input_file = \
            os.path.join(
                os.path.dirname(os.path.dirname(
                    os.path.abspath(__file__))),
                'openfoam_input.txt'
            )
        cls.app_parameters.liggghts_settings.input_file = \
            os.path.join(
                os.path.dirname(os.path.dirname(
                    os.path.abspath(__file__))),
                'liggghts_input.dat'
            )

        temp_dir = tempfile.mkdtemp()
        with cleanup_garbage(temp_dir):
            cls.app_parameters.openfoam_settings.output_path = temp_dir
            cls.openfoam_wrapper, cls.liggghts_wrapper = \
                cls.app_parameters.run_calc()
            super(TestCalculation, cls).setUpClass()

    def test_output(self):
        self.assertTrue(os.path.exists(
            os.path.join(
                self.app_parameters.openfoam_settings.output_path,
                self.app_parameters.openfoam_settings.mesh_name)
        ))

    def test_nb_entities(self):
        flow_dataset = self.liggghts_wrapper.get_dataset(
            self.liggghts_wrapper.get_dataset_names()[0])
        self.assertEqual(flow_dataset.count_of(CUDSItem.PARTICLE), 200)
        self.assertEqual(flow_dataset.count_of(CUDSItem.BOND), 0)

        mesh_dataset = self.openfoam_wrapper.get_dataset(
            self.openfoam_wrapper.get_dataset_names()[0])
        self.assertEqual(mesh_dataset.count_of(CUDSItem.CELL), 15744)
        self.assertEqual(mesh_dataset.count_of(CUDSItem.FACE), 63448)
        self.assertEqual(mesh_dataset.count_of(CUDSItem.EDGE), 0)
        self.assertEqual(mesh_dataset.count_of(CUDSItem.POINT), 32432)

    def test_velocity(self):
        mesh_dataset = self.openfoam_wrapper.get_dataset(
            self.openfoam_wrapper.get_dataset_names()[0])
        avg_velo = 0.0
        for cell in mesh_dataset.iter_cells():
            avg_velo += cell.data[CUBA.VELOCITY][0]
        avg_velo = avg_velo/mesh_dataset.count_of(CUDSItem.CELL)
        self.assertAlmostEqual(avg_velo, 0.00151286)
