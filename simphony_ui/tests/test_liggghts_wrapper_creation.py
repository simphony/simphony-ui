"""
Tests Liggghts wrapper creation
"""

import unittest
from simphony.engine import liggghts
from simphony.core.cuba import CUBA
from simphony_ui.liggghts_model import LiggghtsModel
from simphony_ui.liggghts_wrapper_creation import create_liggghts_wrapper


class TestLiggghtsWrapperCreation(unittest.TestCase):

    def setUp(self):
        self.liggghts_model = LiggghtsModel()

    def test_is_wrapper(self):
        self.assertIsInstance(
            create_liggghts_wrapper(self.liggghts_model),
            liggghts.LiggghtsWrapper
        )

    def test_num_iterations(self):
        self.liggghts_model.num_iterations = 123
        self.assertEqual(
            create_liggghts_wrapper(self.liggghts_model).CM[
                CUBA.NUMBER_OF_TIME_STEPS],
            123
        )

    def test_timestep(self):
        self.liggghts_model.timestep = 0.2356
        self.assertEqual(
            create_liggghts_wrapper(self.liggghts_model).CM[
                CUBA.TIME_STEP],
            0.2356
        )

    def test_boundary_conditions(self):
        self.liggghts_model.x_wall_boundary_condition = 'periodic'
        self.liggghts_model.y_wall_boundary_condition = 'periodic'
        self.liggghts_model.z_wall_boundary_condition = 'fixed'
        self.assertListEqual(
            create_liggghts_wrapper(self.liggghts_model).BC_extension[
                liggghts.CUBAExtension.BOX_FACES],
            ['periodic', 'periodic', 'fixed']
        )

        self.liggghts_model.flow_particles_fixed = True
        self.liggghts_model.wall_particles_fixed = False
        self.assertListEqual(
            create_liggghts_wrapper(self.liggghts_model).BC_extension[
                liggghts.CUBAExtension.FIXED_GROUP],
            [1, 0]
        )
