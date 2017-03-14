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
from simphony_ui.couple_openfoam_liggghts import compute_drag_force


class TestCalculation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app_parameters = Application()

        project_dir = \
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.app_parameters.openfoam_settings.input_file = \
            os.path.join(
                os.path.join(project_dir, 'openfoam'),
                'openfoam_input.txt'
            )
        cls.app_parameters.liggghts_settings.input_file = \
            os.path.join(
                os.path.join(project_dir, 'liggghts'),
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


class TestForceComputation(unittest.TestCase):

    def setUp(self):
        self.radius = 0.02
        self.rel_velo = [1.2, 5.2, 0.2]
        self.viscosity = 0.0062
        self.density = 1005.2
        self.force_type = None

    def test_stokes(self):
        self.force_type = 'Stokes'
        force = compute_drag_force(
            self.force_type,
            self.radius,
            self.rel_velo,
            self.viscosity,
            self.density
        )
        self.assertListEqual(
            force.tolist(),
            [
                0.0028048139211249673,
                0.012154193658208192,
                0.00046746898685416123
            ]
        )

    def test_dala(self):
        self.force_type = 'Dala'
        force = compute_drag_force(
            self.force_type,
            self.radius,
            self.rel_velo,
            self.viscosity,
            self.density
        )
        self.assertListEqual(
            force.tolist(),
            [
                1.7406892534402443,
                7.542986764907726,
                0.29011487557337406
            ]
        )

    def test_coul(self):
        self.force_type = 'Coul'
        force = compute_drag_force(
            self.force_type,
            self.radius,
            self.rel_velo,
            self.viscosity,
            self.density
        )
        self.assertListEqual(
            force.tolist(),
            [
                1.3010027654950582,
                1.3010027654950582,
                1.3010027654950582
            ]
        )

    def test_unknown_force(self):
        self.force_type = 'Coucou heho'
        with self.assertRaises(ValueError):
            compute_drag_force(
                self.force_type,
                self.radius,
                self.rel_velo,
                self.viscosity,
                self.density
            )
