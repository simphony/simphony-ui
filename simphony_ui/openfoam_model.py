import os
from traits.api import (HasStrictTraits, Float, Enum, Str, Directory, Array,
                        File)
from traitsui.api import View, Item, VGroup
from simphony_ui.tests.local_traits import PositiveFloat, PositiveInt


class OpenfoamModel(HasStrictTraits):
    """ The model of Openfoam input parameters """

    #: The input file used for OpenFoam.
    input_file = File()

    #: The mode of computation used with Openfoam.
    mode = Enum('internal', 'io')

    #: The name of the output mesh.
    mesh_name = Str('mesh')

    #: The type of the mesh.
    mesh_type = Enum('block', 'quad')

    #: The directory where to put output files.
    output_path = Directory(os.path.abspath(os.path.curdir))

    #: The duration of a step of computation.
    timestep = PositiveFloat(2.0e-4)

    #: The number of iterations in the simulation.
    num_iterations = PositiveInt(10)

    #: The viscosity of the fluid.
    viscosity = PositiveFloat(1.0e-3)

    #: The density of the fluid.
    density = PositiveFloat(1000.0)

    #: The pression difference.
    delta_p = Float(0.008)

    #: The channel size.
    channel_size = Array(PositiveFloat, (3,), [1.0e-1, 1.0e-2, 2.0e-3])

    #: The number of elements in all channel-directions.
    num_grid = Array(PositiveInt, (3,), [400, 40, 1])

    traits_view = View(
        VGroup(
            Item(name='input_file'),
            '_',
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
