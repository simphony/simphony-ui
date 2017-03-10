from simphony.engine import liggghts
from simphony.core.cuba import CUBA


def create_liggghts_wrapper(liggghts_settings):
    liggghts_wrapper = liggghts.LiggghtsWrapper(use_internal_interface=True)

    # Set Computational method parameters

    # Set system parameters/ conditions

    # Set boundary conditions

    return liggghts_wrapper
