import os

from traits.api import (HasStrictTraits, Enum, Str, Directory,
                        File, Instance)
from traitsui.api import View, Item, VGroup, HGroup, Spring

from simphony_ui.local_traits import PositiveFloat, PositiveInt
from simphony_ui.openfoam_model.openfoam_boundary_conditions import (
    BoundaryConditionsModel)


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
    channel_size_x = PositiveFloat(1.0e-1)
    channel_size_y = PositiveFloat(1.0e-2)
    channel_size_z = PositiveFloat(2.0e-3)

    #: The number of elements in all channel-directions.
    num_grid_x = PositiveInt(400)
    num_grid_y = PositiveInt(40)
    num_grid_z = PositiveInt(1)

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
                HGroup(
                    Item(name='channel_size_x', label='x'),
                    Item(name='channel_size_y', label='y'),
                    Item(name='channel_size_z', label='z'),
                    label='Channel size',
                    show_border=True,
                ),
                HGroup(
                    Item(name='num_grid_x', label='x'),
                    Item(name='num_grid_y', label='y'),
                    Item(name='num_grid_z', label='z'),
                    label='Number of elements in channel directions',
                    show_border=True,
                ),
                label='System parameters/ conditions',
                show_border=True,
            ),
            Spring(),
        )
    )

    def _boundary_conditions_default(self):
        return BoundaryConditionsModel()