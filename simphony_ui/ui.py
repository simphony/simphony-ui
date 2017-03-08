from traits.api import HasStrictTraits, Instance
from traitsui.api import View, UItem, Tabbed
from simphony_ui.global_parameters_model import GlobalParametersModel
from simphony_ui.liggghts_model import LiggghtsModel
from simphony_ui.openfoam_model import OpenfoamModel


class Application(HasStrictTraits):

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
    ui = Application()
    ui.configure_traits()
