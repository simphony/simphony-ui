from traits.api import HasStrictTraits, Int, Float, Enum, File, Bool
from traitsui.api import View, Item, VGroup, HGroup


class LiggghtsModel(HasStrictTraits):
    """ The model of Liggghts input parameters """

    # Computational method parameters
    #: The duration of a step of computation.
    timestep = Float(1e-6)

    #: The number of iterations in the simulation.
    num_iterations = Int(10)

    #: The input file used for liggghts.
    input_file = File()

    # Boundary conditions parameters
    x_wall_boundary_condition = Enum('periodic', 'fixed')
    y_wall_boundary_condition = Enum('periodic', 'fixed')
    z_wall_boundary_condition = Enum('periodic', 'fixed')

    flow_particles_fixed = Bool(False)
    wall_particles_fixed = Bool(True)

    # System parameters/ conditions
    # Flow particles parameters
    flow_young_modulus = Float(2.e4)
    flow_poisson_ratio = Float(0.45)
    flow_restitution_coefficient_flow = Float(0.95)
    flow_restitution_coefficient_wall = Float(0.95)
    flow_friction_coefficient_flow = Float(0.0)
    flow_friction_coefficient_wall = Float(0.0)
    flow_cohesion_energy_density_flow = Float(0.0)
    flow_cohesion_energy_density_wall = Float(0.0)

    flow_pair_potentials = Enum('repulsion', 'cohesion')

    # Wall particles parameters
    wall_young_modulus = Float(2.e4)
    wall_poisson_ratio = Float(0.45)
    wall_restitution_coefficient_wall = Float(0.95)
    wall_restitution_coefficient_flow = Float(0.95)
    wall_friction_coefficient_wall = Float(0.0)
    wall_friction_coefficient_flow = Float(0.0)
    wall_cohesion_energy_density_wall = Float(0.0)
    wall_cohesion_energy_density_flow = Float(0.0)

    wall_pair_potentials = Enum('repulsion', 'cohesion')

    traits_view = View(
        VGroup(
            VGroup(
                Item(name='timestep'),
                Item(name='num_iterations', label='Number of iterations'),
                '_',
                Item(name='input_file'),
                label='Computational method parameters',
                show_border=True
            ),
            VGroup(
                HGroup(
                    Item(
                        name='x_wall_boundary_condition',
                        label='X Wall'
                    ),
                    Item(
                        name='y_wall_boundary_condition',
                        label='Y Wall'
                    ),
                    Item(
                        name='z_wall_boundary_condition',
                        label='Z Wall'
                    ),
                ),
                '_',
                Item(name='flow_particles_fixed'),
                Item(name='wall_particles_fixed'),
                label='Boundary conditions',
                show_border=True
            ),
            VGroup(
                VGroup(
                    Item(
                        name='flow_young_modulus',
                        label='Young\'s modulus'
                    ),
                    Item(
                        name='flow_poisson_ratio',
                        label='Poisson\'s ratio'
                    ),
                    VGroup(
                        Item(
                            name='flow_restitution_coefficient_flow',
                            label='with flow particles'
                        ),
                        Item(
                            name='flow_restitution_coefficient_wall',
                            label='with wall particles'
                        ),
                        label='Restitution Coefficient',
                    ),
                    VGroup(
                        Item(
                            name='flow_friction_coefficient_flow',
                            label='with flow particles'
                        ),
                        Item(
                            name='flow_friction_coefficient_wall',
                            label='with wall particles'
                        ),
                        label='Friction Coefficient',
                    ),
                    VGroup(
                        Item(
                            name='flow_cohesion_energy_density_flow',
                            label='with flow particles'
                        ),
                        Item(
                            name='flow_cohesion_energy_density_wall',
                            label='with wall particles'
                        ),
                        label='Cohesion energy density'
                    ),
                    Item(name='flow_pair_potentials'),
                    label='Flow particles parameters',
                    show_border=True
                ),
                VGroup(
                    Item(
                        name='wall_young_modulus',
                        label='Young\'s modulus'
                    ),
                    Item(
                        name='wall_poisson_ratio',
                        label='Poisson\'s ratio'
                    ),
                    VGroup(
                        Item(
                            name='wall_restitution_coefficient_wall',
                            label='with wall particles'
                        ),
                        Item(
                            name='wall_restitution_coefficient_flow',
                            label='with flow particles'
                        ),
                        label='Restitution Coefficient'
                    ),
                    VGroup(
                        Item(
                            name='wall_friction_coefficient_wall',
                            label='with wall particles'
                        ),
                        Item(
                            name='wall_friction_coefficient_flow',
                            label='with flow particles'
                        ),
                        label='Friction Coefficient'
                    ),
                    VGroup(
                        Item(
                            name='wall_cohesion_energy_density_wall',
                            label='with wall particles'
                        ),
                        Item(
                            name='wall_cohesion_energy_density_flow',
                            label='with flow particles'
                        ),
                        label='Cohesion energy density'
                    ),
                    Item(name='wall_pair_potentials'),
                    label='Wall particles parameters',
                    show_border=True
                ),
                label='System parameters/ conditions',
                show_border=True
            )
        )
    )

    def _y_wall_boundary_condition_default(self):
        return 'fixed'

    def _wall_pair_potentials_default(self):
        return 'cohesion'
