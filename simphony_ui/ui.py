import threading
from pyface.api import GUI
import copy
from traits.api import HasStrictTraits, Instance, Button, on_trait_change
from traitsui.api import View, UItem, Tabbed, VGroup
from simphony_ui.couple_openfoam_liggghts import run_calc
from simphony_ui.global_parameters_model import GlobalParametersModel
from simphony_ui.liggghts_model.liggghts_model import LiggghtsModel
from simphony_ui.openfoam_model.openfoam_model import OpenfoamModel


class ThreadedCalculation(threading.Thread):

    def __init__(
            self,
            global_settings,
            openfoam_settings,
            liggghts_settings,
            **kwargs):
        threading.Thread.__init__(self, **kwargs)
        self.done = False
        self.global_settings = global_settings
        self.openfoam_settings = openfoam_settings
        self.liggghts_settings = liggghts_settings
        self.openfoam_wrapper = None
        self.liggghts_wrapper = None

    def run(self):
        print "Performing computation..."
        GUI.invoke_later(self._run_calculation)

    def _run_calculation(self):
        self.openfoam_wrapper, self.liggghts_wrapper = run_calc(
            self.global_settings,
            self.openfoam_settings,
            self.liggghts_settings
        )
        self.done = True
        print('Done')


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
        calculation = ThreadedCalculation(
            copy.deepcopy(self.global_settings),
            copy.deepcopy(self.openfoam_settings),
            copy.deepcopy(self.liggghts_settings)
        )
        calculation.start()

    def _global_settings_default(self):
        return GlobalParametersModel()

    def _liggghts_settings_default(self):
        return LiggghtsModel()

    def _openfoam_settings_default(self):
        return OpenfoamModel()

if __name__ == '__main__':
    ui = Application()
    ui.configure_traits()
