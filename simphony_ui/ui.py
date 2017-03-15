from traits.api import HasStrictTraits, Instance, Button, on_trait_change
from traitsui.api import View, UItem, Tabbed, VGroup

from simphony_ui.couple_openfoam_liggghts import run_calc
from simphony_ui.global_parameters_model import GlobalParametersModel
from simphony_ui.liggghts_model.liggghts_model import LiggghtsModel
from simphony_ui.openfoam_model.openfoam_model import OpenfoamModel


class Application(HasStrictTraits):

    global_settings = Instance(GlobalParametersModel)
    liggghts_settings = Instance(LiggghtsModel)
    openfoam_settings = Instance(OpenfoamModel)

    run_button = Button("Run")

    traits_view = View(
        VGroup(
            Tabbed(
                UItem('global_settings'),
                UItem('liggghts_settings'),
                UItem('openfoam_settings'),
            ),
            UItem(name='run_button'),
        ),
        title='Simphony UI',
        resizable=True,
        style='custom',
        width=1.0,
        height=1.0
    )

    @on_trait_change('run_button')
    def run_calc(self):
        return run_calc(
            self.global_settings,
            self.openfoam_settings,
            self.liggghts_settings
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
