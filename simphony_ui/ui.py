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
    #: The global settings for the calculation
    global_settings = Instance(GlobalParametersModel)

    #: The Liggghts settings for the calculation
    liggghts_settings = Instance(LiggghtsModel)

    #: The Openfoam settings for the calculation
    openfoam_settings = Instance(OpenfoamModel)

    #: The Openfoam wrapper containing the mesh
    # dataset at the end of the documentation
    openfoam_wrapper = Instance(ABCModelingEngine)

    #: The Liggghts wrapper containing the particles datasets
    # at the end of the documentation
    liggghts_wrapper = Instance(ABCModelingEngine)

    #: The button on which the user will click to run the
    # calculation
    run_button = Button("Run")

    #: The pop up dialog which will show the status of the
    # calculation
    progress_dialog = Instance(ProgressDialog)

    #: Boolean representing if the calculation is running
    # or not
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
        """ Function which will start the calculation on a secondary
        thread on run button click

        Raises
        ------
        RuntimeError
            If the calculation is already running
        """
        if self.calculation_running:
            raise RuntimeError('Calculation already running...')
        self.calculation_running = True
        self.progress_dialog.open()
        future = self._executor.submit(self._run_calc_threaded)
        future.add_done_callback(self._calculation_done)

    def _run_calc_threaded(self):
        """ Function which will run the calculation. This function
        is only run by the secondary thread
        """
        return run_calc(
            self.global_settings,
            self.openfoam_settings,
            self.liggghts_settings,
            self.update_progress_bar
        )

    def _calculation_done(self, future):
        """ Function which will return the result of the computation to
        the main thread

        Parameters
        ----------
        future
            Object containing the result of the calculation
        """
        GUI.invoke_later(self._update_result, future.result())

    def _update_result(self, result):
        """ Function called in the main thread to get the result of the
        calculation from the secondary thread

        Parameters
        ----------
        result
            The result of the calculation, it is a tuple containing the
            Openfoam wrapper and the Liggghts wrapper
        """
        self.openfoam_wrapper, self.liggghts_wrapper = result
        self.calculation_running = False
        self.progress_dialog.update(100)

    def update_progress_bar(self, progress):
        """ Function called in the secondary thread. It will transfer the
        progress status of the calculation to the main thread

        Parameters
        ----------
        progress
            The progress of the calculation (Integer in the range [0, 100])
        """
        GUI.invoke_later(self.progress_dialog.update, progress)

    def __executor_default(self):
        return futures.ThreadPoolExecutor(max_workers=1)

    def _progress_dialog_default(self):
        return ProgressDialog(
            min=0,
            max=100,
            title='Calculation running...'
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
