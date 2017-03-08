import os
from traits.api import HasStrictTraits, Float, Enum, Str, Directory, Array
from traitsui.api import View, Item, VGroup
from simphony_ui.tests.local_traits import PositiveFloat, PositiveInt


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
