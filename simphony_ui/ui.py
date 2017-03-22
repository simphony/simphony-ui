from concurrent import futures
import logging
from pyface.gui import GUI
from pyface.api import error

import mayavi.tools.mlab_scene_model
from simphony_mayavi.sources.api import CUDSSource
from tvtk.pyface.scene_editor import SceneEditor
from simphony_mayavi.modules.default_module import default_module
from mayavi.core.ui.mayavi_scene import MayaviScene

from simphony.cuds.abc_modeling_engine import ABCModelingEngine

from traits.api import (HasStrictTraits, Instance, Button,
                        on_trait_change, Bool, Event, Str)
from traitsui.api import View, UItem, Tabbed, VGroup, HSplit

from pyface.api import ProgressDialog

from simphony_ui.couple_openfoam_liggghts import run_calc
from simphony_ui.global_parameters_model import GlobalParametersModel
from simphony_ui.liggghts_model.liggghts_model import LiggghtsModel
from simphony_ui.openfoam_model.openfoam_model import OpenfoamModel

MlabSceneModel = mayavi.tools.mlab_scene_model.MlabSceneModel


def dataset2cudssource(dataset):
    return CUDSSource(cuds=dataset)


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

    openfoam_source = Instance(CUDSSource)

    liggghts_flow_source = Instance(CUDSSource)
    liggghts_wall_source = Instance(CUDSSource)

    #: The button on which the user will click to run the
    # calculation
    run_button = Button("Run")

    #: The pop up dialog which will show the status of the
    # calculation
    progress_dialog = Instance(ProgressDialog)

    #: Boolean representing if the calculation is running
    # or not
    calculation_running = Bool(False)

    #: The Mayavi traits model which contains the scene and engine
    mlab_model = Instance(MlabSceneModel, ())

    #: Event object which will be useful for error dialog
    calculation_error_event = Event(Str)

    #: Logger for error prints
    logger = Instance(logging.Logger)

    # Private traits.
    #: Executor for the threaded action.
    _executor = Instance(futures.ThreadPoolExecutor)

    traits_view = View(
        HSplit(
            VGroup(
                Tabbed(
                    UItem('global_settings'),
                    UItem('liggghts_settings'),
                    UItem('openfoam_settings'),
                ),
                UItem(name='run_button'),
                enabled_when='calculation_running == False',
            ),
            UItem(
                name='mlab_model',
                editor=SceneEditor(scene_class=MayaviScene)
            )
        ),
        title='Simphony UI',
        resizable=True,
        style='custom',
        width=1.0,
        height=1.0
    )

    @on_trait_change('calculation_error_event', dispatch='ui')
    def show_error(self, msg):
        error(None, 'Oups ! Something went bad:\n{}'.format(msg), 'Error')

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

    @on_trait_change('openfoam_wrapper')
    def show_openfoam_result(self):
        """ Function which add the Openfoam dataset to the
        mayavi scene
        """
        # Clear the scene
        try:
            self.mlab_model.mayavi_scene.remove_child(self.openfoam_source)
        except ValueError:
            pass

        mayavi_engine = self.mlab_model.engine

        # Get Openfoam dataset
        openfoam_dataset = self.openfoam_wrapper.get_dataset(
            self.openfoam_wrapper.get_dataset_names()[0])
        self.openfoam_source = dataset2cudssource(openfoam_dataset)

        modules = default_module(self.openfoam_source)

        # Add Openfoam source
        mayavi_engine.add_source(self.openfoam_source)

        # Add default Openfoam modules
        for module in modules:
            mayavi_engine.add_module(module)

    @on_trait_change('liggghts_wrapper')
    def show_liggghts_result(self):
        """ Function which add the Liggghts datasets to the
        mayavi scene
        """
        # Clear the scene
        try:
            self.mlab_model.mayavi_scene.remove_child(
                self.liggghts_flow_source)
        except ValueError:
            pass
        try:
            self.mlab_model.mayavi_scene.remove_child(
                self.liggghts_wall_source)
        except ValueError:
            pass

        mayavi_engine = self.mlab_model.engine

        # Get Liggghts datasets
        liggghts_flow_dataset = self.liggghts_wrapper.get_dataset(
            'flow_particles')
        liggghts_wall_dataset = self.liggghts_wrapper.get_dataset(
            'wall_particles')

        self.liggghts_flow_source = dataset2cudssource(liggghts_flow_dataset)
        self.liggghts_wall_source = dataset2cudssource(liggghts_wall_dataset)

        flow_modules = default_module(self.liggghts_flow_source)
        wall_modules = default_module(self.liggghts_wall_source)

        # Add Liggghts sources
        mayavi_engine.add_source(self.liggghts_flow_source)

        # Add default Liggghts modules
        for module in flow_modules:
            mayavi_engine.add_module(module)

        mayavi_engine.add_source(self.liggghts_wall_source)

        for module in wall_modules:
            mayavi_engine.add_module(module)

    def _run_calc_threaded(self):
        """ Function which will run the calculation. This function
        is only run by the secondary thread
        """
        try:
            return run_calc(
                self.global_settings,
                self.openfoam_settings,
                self.liggghts_settings,
                self.update_progress_bar
            )
        except Exception as e:
            self.calculation_error_event = str(e)
            self.logger.exception('Error during the calculation')
            return None

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
        # Close progress dialog
        self.progress_dialog.update(100)

        if result is not None:
            self.openfoam_wrapper, self.liggghts_wrapper = result

        self.calculation_running = False

    def update_progress_bar(self, progress):
        """ Function called in the secondary thread. It will transfer the
        progress status of the calculation to the main thread

        Parameters
        ----------
        progress
            The progress of the calculation (Integer in the range [0, 100])
        """
        GUI.invoke_later(self.progress_dialog.update, progress)

    def _logger_default(self):
        return logging.getLogger(self.__class__.__name__)

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
