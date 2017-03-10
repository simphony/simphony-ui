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

    return openfoam_wrapper
