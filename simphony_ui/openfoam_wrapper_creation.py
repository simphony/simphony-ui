import numpy as np
from simphony.engine import openfoam_file_io, openfoam_internal
from simphony.core.cuba import CUBA


def create_openfoam_wrapper(openfoam_settings):
    """ Creates the Openfoam wrapper setup from the settings as provided
    by the model object

    Parameters
    ----------
    openfoam_settings : OpenfoamModel
        The traited model describing the openfoam parameters

    Returns
    -------
    openfoam_wrapper : Wrapper
        an instance of the appropriate Wrapper object, properly configured.
    """

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

    velocity_BC = {}
    velocity_BC['inlet'] = get_boundary_condition_description(
            inlet_BC.velocity_boundary_condition)
    velocity_BC['outlet'] = get_boundary_condition_description(
            outlet_BC.velocity_boundary_condition)
    velocity_BC['walls'] = get_boundary_condition_description(
            walls_BC.velocity_boundary_condition)
    velocity_BC['frontAndBack'] = get_boundary_condition_description(
            front_and_back_BC.velocity_boundary_condition)
    openfoam_wrapper.BC[CUBA.VELOCITY] = velocity_BC

    pressure_BC = {}
    pressure_BC['inlet'] = get_boundary_condition_description(
            inlet_BC.pressure_boundary_condition)
    pressure_BC['outlet'] = get_boundary_condition_description(
            outlet_BC.pressure_boundary_condition)
    pressure_BC['walls'] = get_boundary_condition_description(
            walls_BC.pressure_boundary_condition)
    pressure_BC['frontAndBack'] = get_boundary_condition_description(
            front_and_back_BC.pressure_boundary_condition)
    openfoam_wrapper.BC[CUBA.PRESSURE] = pressure_BC

    return openfoam_wrapper


def get_boundary_condition_description(bc):
    """
    Function which return the proper object defining the
    boundary condition for the Openfoam wrapper

    Parameters
    ----------
    bc : BoundaryConditionModel
        The boundary condition model

    Returns
    -------
        A description of the boundary condition respecting the
        Openfoam wrapper expected input

    Raises
    ------
        If bc.type doesn't have a proper value
    """
    if bc.type == 'none':
        return None
    elif bc.type == 'zeroGradient' or bc.type == 'empty':
        return bc.type
    elif bc.type == 'fixedGradient':
        # The shape of the fixed gradient is (1, 3)
        return bc.type, bc.fixed_gradient[0].tolist()
    elif bc.type == 'fixedValue':
        if type(bc.fixed_value) == np.ndarray:
            return bc.type, bc.fixed_value[0].tolist()
        else:
            return bc.type, bc.fixed_value
    raise ValueError(
        '{} is not a possible boundary condition type'.format(bc.type))
