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
    liggghts_wrapper.CM[CUBA.NUMBER_OF_TIME_STEPS] = \
        liggghts_settings.num_iterations
    liggghts_wrapper.CM[CUBA.TIME_STEP] = liggghts_settings.timestep

    # Set system parameters/ conditions
    liggghts_wrapper.SP[CUBA.YOUNG_MODULUS] = [
        liggghts_settings.flow_young_modulus,
        liggghts_settings.wall_young_modulus
    ]
    liggghts_wrapper.SP[CUBA.POISSON_RATIO] = [
        liggghts_settings.flow_poisson_ratio,
        liggghts_settings.wall_poisson_ratio
    ]
    liggghts_wrapper.SP[CUBA.RESTITUTION_COEFFICIENT] = [
        liggghts_settings.flow_restitution_coefficient_flow,
        liggghts_settings.flow_restitution_coefficient_wall,
        liggghts_settings.wall_restitution_coefficient_flow,
        liggghts_settings.wall_restitution_coefficient_wall
    ]
    liggghts_wrapper.SP[CUBA.FRICTION_COEFFICIENT] = [
        liggghts_settings.flow_friction_coefficient_flow,
        liggghts_settings.flow_friction_coefficient_wall,
        liggghts_settings.wall_friction_coefficient_flow,
        liggghts_settings.wall_friction_coefficient_wall
    ]
    liggghts_wrapper.SP[CUBA.COHESION_ENERGY_DENSITY] = [
        liggghts_settings.flow_cohesion_energy_density_flow,
        liggghts_settings.flow_cohesion_energy_density_wall,
        liggghts_settings.wall_cohesion_energy_density_flow,
        liggghts_settings.wall_cohesion_energy_density_wall
    ]

    liggghts_wrapper.SP_extension[liggghts.CUBAExtension.PAIR_POTENTIALS] = [
        liggghts_settings.flow_pair_potentials,
        liggghts_settings.wall_pair_potentials
    ]

    # Set boundary conditions
    liggghts_wrapper.BC_extension[liggghts.CUBAExtension.BOX_FACES] = [
        liggghts_settings.x_wall_boundary_condition,
        liggghts_settings.y_wall_boundary_condition,
        liggghts_settings.z_wall_boundary_condition
    ]

    liggghts_wrapper.BC_extension[liggghts.CUBAExtension.FIXED_GROUP] = [
        1 if liggghts_settings.flow_particles_fixed else 0,
        1 if liggghts_settings.wall_particles_fixed else 0
    ]

    return liggghts_wrapper
