import os
from traits.api import (HasStrictTraits, Enum, Str, Directory, Array,
                        File, Instance)
from traitsui.api import View, Item, VGroup, Spring
from simphony_ui.local_traits import PositiveFloat, PositiveInt
from simphony_ui.openfoam_boundary_conditions import BoundaryConditionsModel


class OpenfoamModel(HasStrictTraits):
    """ The model of Openfoam input parameters """

    # Computational method parameters
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

    # Boundary conditions parameters
    #: The boundary conditions during the simulation
    boundary_conditions = Instance(BoundaryConditionsModel)

    # System parameters/ conditions
    #: The viscosity of the fluid.
    viscosity = PositiveFloat(1.0e-3)

    #: The density of the fluid.
    density = PositiveFloat(1000.0)

    #: The channel size.
    channel_size = Array(PositiveFloat, (1, 3), [[1.0e-1, 1.0e-2, 2.0e-3]])

    #: The number of elements in all channel-directions.
    num_grid = Array(PositiveInt, (1, 3), [[400, 40, 1]])

    traits_view = View(
        VGroup(
            VGroup(
                Item(name='timestep'),
                Item(name='num_iterations', label='Number of iterations'),
                '_',
                Item(name='input_file'),
                '_',
                Item(name='mode', style='custom'),
                '_',
                Item(name='mesh_name'),
                Item(name='mesh_type'),
                '_',
                Item(name='output_path'),
                label='Computational method parameters',
                show_border=True,
            ),
            VGroup(
                Item(name='boundary_conditions', style='custom'),
                show_border=True
            ),
            VGroup(
                Item(name='viscosity'),
                Item(name='density'),
                '_',
                Item(name='channel_size'),
                Item(name='num_grid'),
                label='System parameters/ conditions',
                show_border=True,
            ),
            Spring(),
        )
    )

    def _boundary_conditions_default(self):
        return BoundaryConditionsModel()
