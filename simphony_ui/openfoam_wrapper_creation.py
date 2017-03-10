import numpy as np
from simphony.engine import openfoam_file_io, openfoam_internal
from simphony.core.cuba import CUBA


def create_openfoam_wrapper(openfoam_settings):
    openfoam_wrapper = None
    openfoam_cuba_ext = None

    if openfoam_settings.mode == "internal":
        openfoam_wrapper = openfoam_internal.Wrapper()
        openfoam_cuba_ext = openfoam_internal.CUBAExt
    elif openfoam_settings.mode == "io":
        openfoam_wrapper = openfoam_file_io.Wrapper()
        openfoam_cuba_ext = openfoam_file_io.CUBAExt

    # Set Computational method parameters
    openfoam_wrapper.CM_extensions[openfoam_cuba_ext.GE] = \
        (openfoam_cuba_ext.INCOMPRESSIBLE, openfoam_cuba_ext.LAMINAR_MODEL)

    openfoam_wrapper.CM[CUBA.NAME] = openfoam_settings.mesh_name

    # Set system parameters/ conditions
    openfoam_wrapper.SP[CUBA.TIME_STEP] = openfoam_settings.timestep
    openfoam_wrapper.SP[CUBA.NUMBER_OF_TIME_STEPS] = \
        openfoam_settings.num_iterations
    openfoam_wrapper.SP[CUBA.DENSITY] = openfoam_settings.density
    openfoam_wrapper.SP[CUBA.DYNAMIC_VISCOSITY] = openfoam_settings.viscosity

    # Set boundary conditions
    openfoam_wrapper.BC[CUBA.VELOCITY] = {}
    openfoam_wrapper.BC[CUBA.PRESSURE] = {}

    inlet_BC = openfoam_settings.boundary_conditions.inlet_BC
    outlet_BC = openfoam_settings.boundary_conditions.outlet_BC
    walls_BC = openfoam_settings.boundary_conditions.walls_BC
    front_and_back_BC = openfoam_settings.boundary_conditions.front_and_back_BC

    openfoam_wrapper.BC[CUBA.VELOCITY]['inlet'] = \
        get_boundary_condition_description(
            inlet_BC.velocity_boundary_condition)
    openfoam_wrapper.BC[CUBA.VELOCITY]['outlet'] = \
        get_boundary_condition_description(
            outlet_BC.velocity_boundary_condition)
    openfoam_wrapper.BC[CUBA.VELOCITY]['walls'] = \
        get_boundary_condition_description(
            walls_BC.velocity_boundary_condition)
    openfoam_wrapper.BC[CUBA.VELOCITY]['frontAndBack'] = \
        get_boundary_condition_description(
            front_and_back_BC.velocity_boundary_condition)

    openfoam_wrapper.BC[CUBA.PRESSURE]['inlet'] = \
        get_boundary_condition_description(
            inlet_BC.pressure_boundary_condition)
    openfoam_wrapper.BC[CUBA.PRESSURE]['outlet'] = \
        get_boundary_condition_description(
            outlet_BC.pressure_boundary_condition)
    openfoam_wrapper.BC[CUBA.PRESSURE]['walls'] = \
        get_boundary_condition_description(
            walls_BC.pressure_boundary_condition)
    openfoam_wrapper.BC[CUBA.PRESSURE]['frontAndBack'] = \
        get_boundary_condition_description(
            front_and_back_BC.pressure_boundary_condition)

    return openfoam_wrapper


def get_boundary_condition_description(bc):
    if bc.type == 'zeroGradient' or bc.type == 'empty':
        return bc.type
    elif bc.type == 'fixedGradient':
        # The shape of the fixed gradient is (1, 3)
        return bc.type, bc.fixed_gradient[0].tolist()
    elif bc.type == 'fixedValue':
        if type(bc.fixed_value) == np.ndarray:
            return bc.type, bc.fixed_value[0].tolist()
        else:
            return bc.type, bc.fixed_value

    return None
