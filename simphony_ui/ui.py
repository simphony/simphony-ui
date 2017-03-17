from concurrent import futures
from pyface.gui import GUI
from simphony.cuds.abc_modeling_engine import ABCModelingEngine

from traits.api import (HasStrictTraits, Instance, Button,
                        on_trait_change, Bool)
from traitsui.api import View, UItem, Tabbed, VGroup
from pyface.api import ProgressDialog
from simphony_ui.couple_openfoam_liggghts import run_calc
from simphony_ui.global_parameters_model import GlobalParametersModel
from simphony_ui.liggghts_model.liggghts_model import LiggghtsModel
from simphony_ui.openfoam_model.openfoam_model import OpenfoamModel


class Application(HasStrictTraits):
    """ Main GUI application which allows user to set global, Openfoam
    and Liggghts parameters of the computation and visualize it
    with Mayavi
    """
    global_settings = Instance(GlobalParametersModel)
    liggghts_settings = Instance(LiggghtsModel)
    openfoam_settings = Instance(OpenfoamModel)

    openfoam_wrapper = Instance(ABCModelingEngine)
    liggghts_wrapper = Instance(ABCModelingEngine)

    run_button = Button("Run")

    progress_dialog = Instance(ProgressDialog)

    calculation_running = Bool(False)

    # Private traits.
    #: Executor for the threaded action.
    _executor = Instance(futures.ThreadPoolExecutor)

    traits_view = View(
        VGroup(
            Tabbed(
                UItem('global_settings'),
                UItem('liggghts_settings'),
                UItem('openfoam_settings'),
            ),
            UItem(name='run_button'),
            enabled_when='calculation_running == False',
        ),
        title='Simphony UI',
        resizable=True,
        style='custom',
        width=1.0,
        height=1.0
    )

    @on_trait_change('run_button')
    def run_calc(self):
        if self.calculation_running:
            raise RuntimeError('Calculation already running...')
        self.calculation_running = True
        self.progress_dialog.open()
        future = self._executor.submit(self._run_calc_threaded)
        future.add_done_callback(self._calculation_done)

    def _run_calc_threaded(self):
        return run_calc(
            self.global_settings,
            self.openfoam_settings,
            self.liggghts_settings,
            self.update_progress_bar
        )

    def _calculation_done(self, future):
        GUI.invoke_later(self._update_result, future.result())

    def _update_result(self, result):
        self.openfoam_wrapper, self.liggghts_wrapper = result
        self.calculation_running = False
        self.progress_dialog.update(100)

    def __executor_default(self):
        return futures.ThreadPoolExecutor(max_workers=1)

    def update_progress_bar(self, progress):
        GUI.invoke_later(self.progress_dialog.update, progress)

    def _progress_dialog_default(self):
        return ProgressDialog(min=0, max=100)

    def _global_settings_default(self):
        return GlobalParametersModel()

    def _liggghts_settings_default(self):
        return LiggghtsModel()

    def _openfoam_settings_default(self):
        return OpenfoamModel()

if __name__ == '__main__':
    ui = Application()
    ui.configure_traits()
