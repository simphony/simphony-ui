"""
Tests Openfoam wrapper creation
"""

import unittest
import os
import tempfile
import shutil
from traits.api import Float, Enum
from simphony.engine import openfoam_file_io, openfoam_internal
from simphony.core.cuba import CUBA
from simphony_ui.openfoam_wrapper_creation import (
    create_openfoam_mesh, create_openfoam_wrapper,
    get_boundary_condition_description)
from simphony_ui.openfoam_model import OpenfoamModel
from simphony_ui.openfoam_boundary_conditions import (
    BoundaryConditionModel)
from simphony_ui.tests.test_utils import cleanup_garbage


class BoundaryConditionTest(BoundaryConditionModel):

    type = Enum(
        'none', 'empty', 'zeroGradient',
        'fixedGradient', 'fixedValue', 'coucou')

    fixed_value = Float()


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


class TestGetBoundaryConditions(unittest.TestCase):

    def setUp(self):
        self.boundary_condition = BoundaryConditionTest()

    def test_none(self):
        self.boundary_condition.type = 'none'
        self.assertEqual(
            get_boundary_condition_description(self.boundary_condition),
            None
        )

    def test_zero_gradient(self):
        self.boundary_condition.type = 'zeroGradient'
        self.assertEqual(
            get_boundary_condition_description(self.boundary_condition),
            'zeroGradient'
        )

    def test_empty(self):
        self.boundary_condition.type = 'empty'
        self.assertEqual(
            get_boundary_condition_description(self.boundary_condition),
            'empty'
        )

    def test_fixedGradient(self):
        self.boundary_condition.type = 'fixedGradient'
        self.boundary_condition.fixed_gradient = [[36, 23, 12]]
        self.assertTupleEqual(
            get_boundary_condition_description(self.boundary_condition),
            ('fixedGradient', [36, 23, 12])
        )

    def test_fixed_value(self):
        self.boundary_condition.type = 'fixedValue'
        self.boundary_condition.fixed_value = 36
        self.assertTupleEqual(
            get_boundary_condition_description(self.boundary_condition),
            ('fixedValue', 36)
        )

    def test_raise(self):
        self.boundary_condition.type = 'coucou'
        with self.assertRaises(ValueError):
            get_boundary_condition_description(self.boundary_condition)


class CustomOpenfoamModel(OpenfoamModel):

    mesh_type = Enum('block', 'quad', 'coucou')


class TestOpenfoamMeshCreation(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        with cleanup_garbage(self.temp_dir):
            self.openfoam_model = CustomOpenfoamModel()
            self.openfoam_model.output_path = self.temp_dir
            self.openfoam_model.mesh_name = 'test_mesh'
            self.openfoam_model.input_file = os.path.join(
                os.path.dirname(os.path.dirname(
                    os.path.abspath(__file__))),
                'openfoam_input.txt'
            )

    def test_block_mesh_creation(self):
        openfoam_wrapper = create_openfoam_wrapper(self.openfoam_model)
        create_openfoam_mesh(openfoam_wrapper, self.openfoam_model)

    def test_quad_mesh_creation(self):
        self.openfoam_model.mesh_type = 'quad'
        openfoam_wrapper = create_openfoam_wrapper(self.openfoam_model)
        create_openfoam_mesh(openfoam_wrapper, self.openfoam_model)

    def test_unknown_mesh_type(self):
        self.openfoam_model.mesh_type = 'coucou'
        openfoam_wrapper = create_openfoam_wrapper(self.openfoam_model)
        with self.assertRaises(ValueError):
            create_openfoam_mesh(openfoam_wrapper, self.openfoam_model)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
