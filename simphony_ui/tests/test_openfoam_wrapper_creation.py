"""
Tests Openfoam wrapper creation
"""

import unittest
from simphony.engine import openfoam_file_io, openfoam_internal
from simphony.core.cuba import CUBA
from simphony_ui.openfoam_wrapper_creation import create_openfoam_wrapper
from simphony_ui.openfoam_model import OpenfoamModel


class TestOpenfoamWrapperCreation(unittest.TestCase):

    def setUp(self):
        self.openfoam_model = OpenfoamModel()

    def test_is_wrapper(self):
        self.assertIsInstance(
            create_openfoam_wrapper(self.openfoam_model),
            openfoam_internal.Wrapper
        )
        self.openfoam_model.mode = 'io'
        self.assertIsInstance(
            create_openfoam_wrapper(self.openfoam_model),
            openfoam_file_io.Wrapper
        )

    def test_mesh_name(self):
        self.openfoam_model.mesh_name = 'coucou'
        self.assertEqual(
            create_openfoam_wrapper(self.openfoam_model).CM[CUBA.NAME],
            'coucou'
        )

    def test_timestep(self):
        self.openfoam_model.timestep = 1.02e-5
        self.assertEqual(
            create_openfoam_wrapper(self.openfoam_model).SP[CUBA.TIME_STEP],
            1.02e-5
        )

    def test_num_iterations(self):
        self.openfoam_model.num_iterations = 56
        self.assertEqual(
            create_openfoam_wrapper(self.openfoam_model).SP[
                CUBA.NUMBER_OF_TIME_STEPS],
            56
        )

    def test_density(self):
        self.openfoam_model.density = 1005.0
        self.assertEqual(
            create_openfoam_wrapper(self.openfoam_model).SP[
                CUBA.DENSITY],
            1005.0
        )

    def test_viscosity(self):
        self.openfoam_model.viscosity = 1.5e-3
        self.assertEqual(
            create_openfoam_wrapper(self.openfoam_model).SP[
                CUBA.DYNAMIC_VISCOSITY],
            1.5e-3
        )

    def test_velocity_boundary_conditions(self):
        self.assertDictEqual(
            create_openfoam_wrapper(self.openfoam_model).BC[
                CUBA.VELOCITY],
            {
                'inlet': 'zeroGradient',
                'outlet': 'zeroGradient',
                'walls': ('fixedValue', [0, 0, 0]),
                'frontAndBack': 'empty'
            }
        )

    def test_pressure_boundary_conditions(self):
        self.assertDictEqual(
            create_openfoam_wrapper(self.openfoam_model).BC[
                CUBA.PRESSURE],
            {
                'inlet': ('fixedValue', 0.008),
                'outlet': ('fixedValue', 0.0),
                'walls': 'zeroGradient',
                'frontAndBack': 'empty'
            }
        )
