import numpy as np
from traits.api import HasStrictTraits, Float, Enum, Instance, Array
from traitsui.api import View, Item, Tabbed, UItem, VGroup


class BoundaryConditionModel(HasStrictTraits):

    #: The type of the boundary condition
    type = Enum('none', 'empty', 'zeroGradient', 'fixedGradient', 'fixedValue')

    #: A fixed value of velocity gradient for the boundary
    fixed_gradient = Array(np.float, (1, 3))

    traits_view = View(
        VGroup(
            'type',
            Item(
                name='fixed_gradient',
                visible_when='type == "fixedGradient"',
            ),
            Item(
                name='fixed_value',
                visible_when='type == "fixedValue"',
            ),
            show_border=True,
        )
    )


class VelocityBoundaryConditionModel(BoundaryConditionModel):

    #: A fixed value of velocity for the boundary
    fixed_value = Array(np.float, (1, 3))


class PressureBoundaryConditionModel(BoundaryConditionModel):

    #: A fixed value of pressure for the boundary
    fixed_value = Float()


class SurfaceModel(HasStrictTraits):

    #: The velocity boundary condition model for the surface
    velocity_boundary_condition = Instance(VelocityBoundaryConditionModel)

    #: The pressure boundary condition model for the surface
    pressure_boundary_condition = Instance(PressureBoundaryConditionModel)

    traits_view = View(
        Item(name='velocity_boundary_condition', style='custom'),
        Item(name='pressure_boundary_condition', style='custom'),
    )

    def _velocity_boundary_condition_default(self):
        return VelocityBoundaryConditionModel()

    def _pressure_boundary_condition_default(self):
        return PressureBoundaryConditionModel()


class BoundaryConditionsModel(HasStrictTraits):

    #: The boundary conditions of the inlet
    inlet_BC = Instance(SurfaceModel)

    #: The boundary conditions of the outlet
    outlet_BC = Instance(SurfaceModel)

    #: The boundary conditions of the walls
    walls_BC = Instance(SurfaceModel)

    #: The boundary conditions of the front and back
    front_and_back_BC = Instance(SurfaceModel)

    traits_view = View(
        Tabbed(
            UItem(
                name='inlet_BC',
                style='custom',
                label='Inlet'
            ),
            UItem(
                name='outlet_BC',
                style='custom',
                label='Outlet'
            ),
            UItem(
                name='walls_BC',
                style='custom',
                label='Walls'
            ),
            UItem(
                name='front_and_back_BC',
                style='custom',
                label='Front and Back'
            )
        )
    )

    def _inlet_BC_default(self):
        inlet_bc = SurfaceModel()

        # Add default velocity values
        inlet_bc.velocity_boundary_condition.type = 'zeroGradient'

        # Add default pressure values
        inlet_bc.pressure_boundary_condition.type = 'fixedValue'
        inlet_bc.pressure_boundary_condition.fixed_value = 0.008

        return inlet_bc

    def _outlet_BC_default(self):
        outlet_bc = SurfaceModel()

        outlet_bc.velocity_boundary_condition.type = 'zeroGradient'

        outlet_bc.pressure_boundary_condition.type = 'fixedValue'

        return outlet_bc

    def _walls_BC_default(self):
        walls_bc = SurfaceModel()

        walls_bc.velocity_boundary_condition.type = 'fixedValue'

        walls_bc.pressure_boundary_condition.type = 'zeroGradient'

        return walls_bc

    def _front_and_back_BC_default(self):
        front_and_back_bc = SurfaceModel()

        front_and_back_bc.velocity_boundary_condition.type = 'empty'

        front_and_back_bc.pressure_boundary_condition.type = 'empty'

        return front_and_back_bc
