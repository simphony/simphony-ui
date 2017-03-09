from traits.api import HasStrictTraits, Int, Float, Enum, Array, File, Bool
from traitsui.api import View, Item, VGroup, HGroup


class LiggghtsModel(HasStrictTraits):
    """ The model of Liggghts input parameters """

    #: The duration of a step of computation.
    timestep = Float(1e-6)

    #: The number of iterations in the simulation.
    num_iterations = Int(10)

    #: The input file used for liggghts.
    input_file = File()

    boundary_condition_x = Enum('periodic', 'fixed', 'shrink-wrapped')
    boundary_condition_y = Enum('periodic', 'fixed', 'shrink-wrapped')
    boundary_condition_z = Enum('periodic', 'fixed', 'shrink-wrapped')

    flow_particles_fixed = Bool(False)
    wall_particles_fixed = Bool(True)

    young_modulus = Array(Float, (2,), [2.e4, 2.e4])
    poisson_ratio = Array(Float, (2,), [0.45, 0.45])
    restitution_coefficient = Array(Float, (4,), [0.95, 0.95, 0.95, 0.95])
    friction_coefficient = Array(Float, (4,), [0.0, 0.0, 0.0, 0.0])
    cohesion_energy_density = Array(Float, (4,), [0.0, 0.0, 0.0, 0.0])

    pair_potentials_1 = Enum('repulsion', 'cohesion')
    pair_potentials_2 = Enum('repulsion', 'cohesion')

    traits_view = View(
        VGroup(
            Item(name='timestep'),
            Item(name='num_iterations', label='Number of iterations'),
            '_',
            Item(name='input_file'),
            '_',
            HGroup(
                Item(name='boundary_condition_x', show_label=False),
                Item(name='boundary_condition_y', show_label=False),
                Item(name='boundary_condition_z', show_label=False),
                label='Boundary conditions'
            ),
            '_',
            Item(name='flow_particles_fixed'),
            Item(name='wall_particles_fixed'),
            '_',
            Item(name='young_modulus'),
            Item(name='poisson_ratio'),
            Item(name='restitution_coefficient'),
            Item(name='friction_coefficient'),
            Item(name='cohesion_energy_density'),
            HGroup(
                Item(name='pair_potentials_1', show_label=False),
                Item(name='pair_potentials_2', show_label=False),
                label='Pair potentials'
            ),
        )
    )

    def _boundary_condition_y_default(self):
        return 'fixed'

    def _pair_potentials_2_default(self):
        return 'cohesion'
