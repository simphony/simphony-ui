from concurrent import futures
import logging
import traceback
import numpy
from pyface.gui import GUI
from pyface.api import error

import mayavi.tools.mlab_scene_model
from mayavi.modules.api import Surface, Glyph
from simphony.cuds.abc_dataset import ABCDataset
from traits.trait_types import Tuple, Either
from tvtk.tvtk_classes.sphere_source import SphereSource

from simphony_mayavi.sources.api import CUDSSource
from simphony.core.cuba import CUBA
from tvtk.pyface.scene_editor import SceneEditor
from mayavi.core.ui.mayavi_scene import MayaviScene

from simphony.cuds.abc_modeling_engine import ABCModelingEngine

from traits.api import (HasStrictTraits, Instance, Button,
                        on_trait_change, Bool, Event, Str, Dict)
from traitsui.api import (View, UItem, Tabbed, VGroup, HSplit, VSplit,
                          ShellEditor)

from pyface.api import ProgressDialog

from simphony_ui.couple_openfoam_liggghts import run_calc
from simphony_ui.global_parameters_model import GlobalParametersModel
from simphony_ui.liggghts_model.liggghts_model import LiggghtsModel
from simphony_ui.openfoam_model.openfoam_model import OpenfoamModel

MlabSceneModel = mayavi.tools.mlab_scene_model.MlabSceneModel

log = logging.getLogger(__name__)


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

    #: The datasets of the current frame. Order is important, and
    # maps as follows: openfoam, liggghts flow, liggghts wall
    datasets = Either(None,
                      Tuple(Instance(ABCDataset),
                            Instance(ABCDataset),
                            Instance(ABCDataset)))

    # The mayavi sources, associated to the above datasets. Order is
    # the same as above.
    sources = Either(None,
                     Tuple(Instance(CUDSSource),
                           Instance(CUDSSource),
                           Instance(CUDSSource)))

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

    #: True if the calculation can be safely run, False otherwise
    valid = Bool(False)

    #: Dictionary of the namespace associated to the shell editor
    shell = Dict()

    # Private traits.
    #: Executor for the threaded action.
    _executor = Instance(futures.ThreadPoolExecutor)

    traits_view = View(
        HSplit(
            VSplit(
                VGroup(
                    Tabbed(
                        UItem('global_settings'),
                        UItem('liggghts_settings'),
                        UItem('openfoam_settings', label='OpenFOAM settings'),
                    ),
                    UItem(
                        name='run_button',
                        enabled_when='valid'
                    ),
                    enabled_when='calculation_running == False',
                ),
                UItem('shell', editor=ShellEditor())
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
    def show_error(self, error_message):
        error(
            None,
            'Oups ! Something went bad...\n\n{}'.format(error_message),
            'Error'
        )

    @on_trait_change('openfoam_settings:valid,'
                     'liggghts_settings:valid')
    def update_valid(self):
        self.valid = (self.openfoam_settings.valid and
                      self.liggghts_settings.valid)

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

    @on_trait_change('datasets')
    def update_sources(self):
        """ Function which add the Openfoam dataset to the
        mayavi scene
        """
        self._clear_sources()

        if self.datasets is None:
            return


        # Get Openfoam dataset
        self.sources = map(dataset2cudssource, self.datasets)

    @on_trait_change('sources')
    def show_sources(self):
        # Add Openfoam source
        mayavi_engine = self.mlab_model.engine
        mayavi_engine.add_source(self.sources[0])

        # Add surface module to Openfoam source
        mayavi_engine.add_module(Surface())

        self._add_liggghts_source_to_scene(self.datasets[1], self.sources[1])
        self._add_liggghts_source_to_scene(self.datasets[2], self.sources[2])

    def _add_liggghts_source_to_scene(self, dataset, source):
        """ Function which add to liggghts source to the Mayavi scene

        Parameters
        ----------
        dataset :
            The dataset containing particles
        source :
            The mayavi source linked to the dataset
        """
        mayavi_engine = self.mlab_model.engine

        # Create Sphere glyph
        sphere_glyph_module = Glyph()

        # Add Liggghts sources
        mayavi_engine.add_source(source)

        source.point_vectors_name = 'VELOCITY'

        # Add sphere glyph module
        mayavi_engine.add_module(sphere_glyph_module)

        sphere_glyph_module.glyph.glyph_source.glyph_source = \
            SphereSource()
        sphere_glyph_module.glyph.scale_mode = 'scale_by_scalar'
        sphere_glyph_module.glyph.glyph.range = [0.0, 1.0]
        sphere_glyph_module.glyph.glyph_source.glyph_source.radius = \
            1.0

        # Create Arrow glyph
        # Get maximum particle velocity
        velocities = numpy.array(
            [numpy.linalg.norm(particle.data[CUBA.VELOCITY])
             for particle
             in dataset.iter_particles()]
        )
        max_velocity = numpy.max(velocities)

        # If the max velocity is not 0, we create the arrow glyph
        if max_velocity != 0:
            # Velocities are in meter/second, this scale factor makes
            # 1 graphical unit = 1 micrometer/sec
            arrow_scale_factor = 1.0e6

            arrow_glyph_module = Glyph()

            mayavi_engine.add_module(arrow_glyph_module)

            arrow_glyph_module.glyph.scale_mode = 'scale_by_vector'
            arrow_glyph_module.glyph.color_mode = 'color_by_vector'
            arrow_glyph_module.glyph.glyph.range = [0.0, 1.0]
            arrow_glyph_module.glyph.glyph.scale_factor = arrow_scale_factor

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
        except Exception:
            self.calculation_error_event = traceback.format_exc()
            log.exception('Error during the calculation')
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
            self.datasets = result

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

    def reset(self):
        """ Function which reset the Mayavi scene.
        """
        # Clear scene
        self._clear_sources()

        # Clear wrappers
        self.datasets = None

    def _clear_sources(self):
        """ Function which reset the sources
        """
        for source in self.sources:
            try:
                self.mlab_model.mayavi_scene.remove_child(source)
            except ValueError:
                pass
        self.sources = None

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
