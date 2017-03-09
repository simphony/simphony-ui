from traits.api import HasStrictTraits, Float, Enum, Instance, Array
from traitsui.api import View, Item, Tabbed, UItem


class BoundaryConditionModel(HasStrictTraits):

    type = Enum('none', 'empty', 'fixedGradient', 'fixedValue')

    traits_view = View(
        'type',
        Item(
            name='fixed_gradient',
            visible_when='type == "fixedGradient"',
            style='custom'
        ),
        Item(
            name='fixed_value',
            visible_when='type == "fixedValue"',
            style='custom'
        ),
    )


class VelocityBoundaryConditionModel(BoundaryConditionModel):

    fixed_gradient = Array(Float, (3,))

    fixed_value = Array(Float, (3,))


class PressureBoundaryConditionModel(BoundaryConditionModel):

    fixed_gradient = Float()

    fixed_value = Float()


class SurfaceModel(HasStrictTraits):

    velocity_boundary_condition = Instance(VelocityBoundaryConditionModel)

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

    inlet_BC = Instance(SurfaceModel)
    outlet_BC = Instance(SurfaceModel)
    walls_BC = Instance(SurfaceModel)
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
            ),
        )
    )

    def _inlet_BC_default(self):
        return SurfaceModel()

    def _outlet_BC_default(self):
        return SurfaceModel()

    def _walls_BC_default(self):
        return SurfaceModel()

    def _front_and_back_BC_default(self):
        return SurfaceModel()

if __name__ == '__main__':
    BoundaryConditionsModel().configure_traits()
