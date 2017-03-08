from traits.api import (HasStrictTraits, Int, Float, Enum, Instance,
                        Str, Directory, Array, File)
from traitsui.api import View, Item, UItem, Tabbed, VGroup, HGroup
import os
from simphony_ui.tests.local_traits import PositiveFloat, PositiveInt


class GlobalParametersModel(HasStrictTraits):
    """ The model of Global input parameters """

    num_iterations = Int(10)

    force_type = Enum('Stokes', 'Coul', 'Dala')

    traits_view = View(
        VGroup(
            Item(name='num_iterations', label='Number of iterations'),
            Item(name='force_type'),
        )
    )


class LiggghtsModel(HasStrictTraits):
    """ The model of Liggghts input parameters """

    timestep = Float(1e-6)
    num_iterations = Int(10)

    input_file = File()

    # TODO: Display min value textbox when shrink-wrapped option is used
    boundary_condition_x = Enum('periodic', 'fixed', 'shrink-wrapped')
    boundary_condition_x.default_value = 'periodic'
    boundary_condition_y = Enum('periodic', 'fixed', 'shrink-wrapped')
    boundary_condition_y.default_value = 'fixed'
    boundary_condition_z = Enum('periodic', 'fixed', 'shrink-wrapped')
    boundary_condition_z.default_value = 'periodic'

    # TODO: Checkboxes for particles fixed on the walls or not

    # TODO: Try to display arrays on only one line
    young_modulus = Array(Float, (2,), [2.e4, 2.e4])
    poisson_ratio = Array(Float, (2,), [0.45, 0.45])
    restitution_coefficient = Array(Float, (4,), [0.95, 0.95, 0.95, 0.95])
    friction_coefficient = Array(Float, (4,), [0.0, 0.0, 0.0, 0.0])
    cohesion_energy_density = Array(Float, (4,), [0.0, 0.0, 0.0, 0.0])

    # TODO: Check in the documentation if there must be more
    # possibilities in dropdowns
    pair_potentials_1 = Enum('repulsion', 'cohesion')
    pair_potentials_2 = Enum('repulsion', 'cohesion')
    pair_potentials_2.default_value = 'cohesion'

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
                # TODO: The label is not displayed properly: fix it
                label='Boundary conditions'
            ),
            '_',
            Item(name='young_modulus'),
            Item(name='poisson_ratio'),
            Item(name='restitution_coefficient'),
            Item(name='friction_coefficient'),
            Item(name='cohesion_energy_density'),
            HGroup(
                Item(name='pair_potentials_1', show_label=False),
                Item(name='pair_potentials_2', show_label=False),
                # TODO: label is not displayed properly: fix it
                label='Pair potentials'
            ),
        )
    )


class OpenfoamModel(HasStrictTraits):
    """ The model of Openfoam input parameters """

    mode = Enum('internal', 'io')

    # TODO: input_file = ???
    mesh_name = Str('mesh')
    mesh_type = Enum('block', 'quad')

    output_path = Directory(os.path.abspath(os.path.curdir))

    timestep = PositiveFloat(2.0e-4)
    num_iterations = PositiveInt(10)

    viscosity = PositiveFloat(1.0e-3)
    density = PositiveFloat(1000.0)
    delta_p = Float(0.008)

    # TODO: boundary_conditions_velocity = ???
    # TODO: boundary_conditions_pressure = ???

    # TODO: PosInt and PosFloat not working for Arrays....
    # TODO: Try to display arrays on only one line
    channel_size = Array(PositiveFloat, (3,), [1.0e-1, 1.0e-2, 2.0e-3])
    num_grid = Array(PositiveInt, (3,), [400, 40, 1])

    traits_view = View(
        VGroup(
            Item(name='mode', style='custom'),
            '_',
            Item(name='mesh_name'),
            Item(name='mesh_type'),
            '_',
            Item(name='output_path'),
            '_',
            Item(name='timestep'),
            Item(name='num_iterations', label='Number of iterations'),
            '_',
            Item(name='viscosity'),
            Item(name='density'),
            Item(name='delta_p'),
            '_',
            Item(name='channel_size'),
            Item(name='num_grid'),
        )
    )


class TabsModel(HasStrictTraits):

    global_settings = Instance(GlobalParametersModel)
    liggghts_settings = Instance(LiggghtsModel)
    openfoam_settings = Instance(OpenfoamModel)

    traits_view = View(
        Tabbed(
            UItem('global_settings'),
            UItem('liggghts_settings'),
            UItem('openfoam_settings'),
        ),
        title='Simphony UI',
        resizable=True,
        style='custom',
        width=1.0,
        height=1.0
    )

    def _global_settings_default(self):
        return GlobalParametersModel()

    def _liggghts_settings_default(self):
        return LiggghtsModel()

    def _openfoam_settings_default(self):
        return OpenfoamModel()

if __name__ == '__main__':
    ui = TabsModel()
    ui.configure_traits()
