from traits.api import HasStrictTraits, Int, Enum
from traitsui.api import View, Item, VGroup


class GlobalParametersModel(HasStrictTraits):
    """ The model of Global input parameters """

    #: The number of iterations in the simulation.
    num_iterations = Int(10)

    #: How often we should consider the current state for plotting/saving
    update_frequency = Int(1)

    #: The type of the force used during the simulation.
    force_type = Enum('Stokes', 'Coul', 'Dala')

    traits_view = View(
        VGroup(
            Item(name='num_iterations', label='Number of iterations'),
            Item(name='update_frequency', label='Update frequency'),
            Item(name='force_type'),
            show_border=True
        )
    )
