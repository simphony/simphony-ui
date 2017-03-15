"""
Tests Liggghts wrapper creation
"""

import os
import unittest

from simphony.core.cuba import CUBA
from simphony.core.cuds_item import CUDSItem
from simphony.engine import liggghts
from simphony_ui.liggghts_model.liggghts_model import LiggghtsModel

from simphony_ui.liggghts_model.liggghts_wrapper_creation import (
    create_liggghts_wrapper, create_liggghts_datasets)


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

    def test_young_modulus(self):
        self.liggghts_model.flow_young_modulus = 0.003
        self.liggghts_model.wall_young_modulus = 0.523
        self.assertListEqual(
            create_liggghts_wrapper(self.liggghts_model).SP[
                CUBA.YOUNG_MODULUS],
            [0.003, 0.523]
        )

    def test_poisson_ratio(self):
        self.liggghts_model.flow_poisson_ratio = 0.003
        self.liggghts_model.wall_poisson_ratio = 0.526
        self.assertListEqual(
            create_liggghts_wrapper(self.liggghts_model).SP[
                CUBA.POISSON_RATIO],
            [0.003, 0.526]
        )

    def test_restitution_coefficient(self):
        self.liggghts_model.flow_restitution_coefficient_flow = 0.56
        self.liggghts_model.flow_restitution_coefficient_wall = 0.23
        self.liggghts_model.wall_restitution_coefficient_flow = 1.56
        self.liggghts_model.wall_restitution_coefficient_wall = 1.23
        self.assertListEqual(
            create_liggghts_wrapper(self.liggghts_model).SP[
                CUBA.RESTITUTION_COEFFICIENT],
            [0.56, 0.23, 1.56, 1.23]
        )

    def test_friction_coefficient(self):
        self.liggghts_model.flow_friction_coefficient_flow = 0.128
        self.liggghts_model.flow_friction_coefficient_wall = 0.129
        self.liggghts_model.wall_friction_coefficient_flow = 1.56
        self.liggghts_model.wall_friction_coefficient_wall = 1.23
        self.assertListEqual(
            create_liggghts_wrapper(self.liggghts_model).SP[
                CUBA.FRICTION_COEFFICIENT],
            [0.128, 0.129, 1.56, 1.23]
        )

    def test_cohesion_energy_density(self):
        self.liggghts_model.flow_cohesion_energy_density_flow = 0.56
        self.liggghts_model.flow_cohesion_energy_density_wall = 0.23
        self.liggghts_model.wall_cohesion_energy_density_flow = 1.1256
        self.liggghts_model.wall_cohesion_energy_density_wall = 1.1254
        self.assertListEqual(
            create_liggghts_wrapper(self.liggghts_model).SP[
                CUBA.COHESION_ENERGY_DENSITY],
            [0.56, 0.23, 1.1256, 1.1254]
        )

    def test_pair_potentials(self):
        self.liggghts_model.flow_pair_potentials = 'cohesion'
        self.liggghts_model.wall_pair_potentials = 'repulsion'
        self.assertListEqual(
            create_liggghts_wrapper(self.liggghts_model).SP_extension[
                liggghts.CUBAExtension.PAIR_POTENTIALS],
            ['cohesion', 'repulsion']
        )


class TestLiggghtsDatasetsCreation(unittest.TestCase):

    def setUp(self):
        self.liggghts_model = LiggghtsModel()
        project_dir = \
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.liggghts_model.input_file = \
            os.path.join(
                os.path.join(project_dir, 'liggghts_model'),
                'liggghts_input.dat'
            )

        self.liggghts_wrapper = create_liggghts_wrapper(self.liggghts_model)

    def test_flow_dataset(self):
        flow_dataset, _ = create_liggghts_datasets(self.liggghts_model)
        self.assertEqual(flow_dataset.count_of(CUDSItem.PARTICLE), 200)
        self.assertEqual(flow_dataset.count_of(CUDSItem.BOND), 0)
