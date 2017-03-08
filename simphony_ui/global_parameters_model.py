from traits.api import HasStrictTraits, Int, Enum
from traitsui.api import View, Item, VGroup


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
