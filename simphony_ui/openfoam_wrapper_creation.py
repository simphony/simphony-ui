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

    return openfoam_wrapper
