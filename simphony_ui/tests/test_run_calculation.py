"""
Tests
"""

import os
import tempfile
import unittest
from mock import Mock
from simphony.core.cuds_item import CUDSItem
from simphony.core.cuba import CUBA
from simphony_ui.global_parameters_model import GlobalParametersModel
from simphony_ui.openfoam_model.openfoam_model import OpenfoamModel
from simphony_ui.liggghts_model.liggghts_model import LiggghtsModel
from simphony_ui.tests.test_utils import cleanup_garbage
from simphony_ui.couple_openfoam_liggghts import compute_drag_force
from simphony_ui.couple_openfoam_liggghts import run_calc


class TestCalculation(unittest.TestCase):
    # This test class only runs the calculation once

    @classmethod
    def setUpClass(cls):
        cls.global_settings = GlobalParametersModel()
        cls.openfoam_settings = OpenfoamModel()
        cls.liggghts_settings = LiggghtsModel()
        cls.event_lock = Mock()
        cls.event_lock.wait = Mock()
        cls.event_lock.clear = Mock()

        cls.openfoam_settings.input_file = os.path.join(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'fixtures'
            ),
            'openfoam_input.txt'
        )
        cls.liggghts_settings.input_file = os.path.join(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'fixtures'
            ),
            'liggghts_input.dat'
        )

        temp_dir = tempfile.mkdtemp()
        with cleanup_garbage(temp_dir):
            cls.openfoam_settings.output_path = temp_dir

            def callback(*args):
                pass

            cls.datasets = run_calc(
                cls.global_settings,
                cls.openfoam_settings,
                cls.liggghts_settings,
                callback,
                event_lock=cls.event_lock
            )
            super(TestCalculation, cls).setUpClass()

    def test_output(self):
        self.assertTrue(os.path.exists(
            os.path.join(
                self.openfoam_settings.output_path, 'mesh'
            )
        ))

    def test_event_lock(self):
        self.assertTrue(self.event_lock.wait.called)
        self.assertTrue(self.event_lock.clear.called)

    def test_nb_entities(self):
        self.assertEqual(self.datasets[1].count_of(CUDSItem.PARTICLE), 200)
        self.assertEqual(self.datasets[1].count_of(CUDSItem.BOND), 0)

        self.assertEqual(self.datasets[0].count_of(CUDSItem.CELL), 15744)
        self.assertEqual(self.datasets[0].count_of(CUDSItem.FACE), 63448)
        self.assertEqual(self.datasets[0].count_of(CUDSItem.EDGE), 0)
        self.assertEqual(self.datasets[0].count_of(CUDSItem.POINT), 32432)

    def test_velocity(self):
        mesh_dataset = self.datasets[0]
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
