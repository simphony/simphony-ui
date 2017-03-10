from simphony.engine import liggghts
from simphony.core.cuba import CUBA


def create_liggghts_wrapper(liggghts_settings):
    """ Creates the liggghts wrapper setup from the settings as provided
    by the model object

    Parameters
    ----------
    liggghts_settings : LiggghtsModel
        The traited model describing the liggghts parameters

    Returns
    -------
    liggghts_wrapper : LiggghtsWrapper
        an instance of a LiggghtsWrapper, properly configured.
    """
    liggghts_wrapper = liggghts.LiggghtsWrapper(use_internal_interface=True)

    # Set Computational method parameters

    # Set system parameters/ conditions

    # Set boundary conditions

    return liggghts_wrapper
