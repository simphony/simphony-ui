from __future__ import division

import threading
from concurrent import futures
import logging
import traceback
from pyface.gui import GUI
from pyface.api import error
from pyface.timer.api import Timer

import mayavi.tools.mlab_scene_model
from mayavi.modules.api import Surface, Glyph
from simphony_mayavi.cuds.vtk_mesh import VTKMesh
from simphony_mayavi.cuds.vtk_particles import VTKParticles
from tvtk.tvtk_classes.sphere_source import SphereSource

from simphony_mayavi.sources.api import CUDSSource

from tvtk.pyface.scene_editor import SceneEditor
from mayavi.core.ui.mayavi_scene import MayaviScene

from traits.api import (HasStrictTraits, Instance, Button,
                        on_trait_change, Bool, Event, Str, Dict, List, Tuple,
                        Either, Int)
from traitsui.api import (View, UItem, Tabbed, VGroup, HSplit, VSplit,
                          ShellEditor, HGroup, Item, ButtonEditor)

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

    # The mayavi sources, associated to the following datasets:
    # first element is the openfoam mesh, second and third are
    # the flow and walls particles, respectively.
    # It is an invariant. The cuds gets changed as we select different
    # frames.
    sources = Tuple(Instance(CUDSSource),
                    Instance(CUDSSource),
                    Instance(CUDSSource))

    # All the frames resulting from the execution of our computation.
    frames = List(Tuple(VTKMesh, VTKParticles, VTKParticles))

    # The frame to visualize
    current_frame_index = Int()

    # The physical current frame, for practicality
    _current_frame = Either(
        None,
        Tuple(VTKMesh, VTKParticles, VTKParticles)
    )

    #: The button on which the user will click to run the
    # calculation
    run_button = Button("Run")

    first_button = Button("First")
    previous_button = Button("Previous")
    play_stop_button = Button()
    play_stop_label = Str("Play")
    next_button = Button("Next")

    play_timer = Instance(Timer)

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

    # Lock to synchronize the execution loop and the storage of the Datasets
    # from application specific cuds to VTK Datasets. We need to do so because
    # the computational engine can change the datasets, so we need to hold
    # the computational engine until we are done "copying and storing" each
    # frame
    _event_lock = Instance(threading.Event, ())

    traits_view = View(
        HSplit(
            VSplit(
                VGroup(
                    Tabbed(
                        UItem('global_settings', style='custom'),
                        UItem('liggghts_settings', style='custom'),
                        UItem('openfoam_settings', label='OpenFOAM settings', style="custom"),
                    ),
                    UItem(
                        name='run_button',
                        enabled_when='valid'
                    ),
                    enabled_when='calculation_running == False',
                ),
                UItem('shell', editor=ShellEditor())
            ),
            VGroup(
                UItem(
                    name='mlab_model',
                    editor=SceneEditor(scene_class=MayaviScene)
                ),
                HGroup(
                    UItem(
                        name="first_button",
                        enabled_when="current_frame_index > 0 and play_timer is None",
                    ),
                    UItem(
                        name="previous_button",
                        enabled_when="current_frame_index > 0 and play_timer is None",
                    ),
                    UItem(
                        name="play_stop_button", editor=ButtonEditor(label_value="play_stop_label")
                    ),
                    UItem(
                        name="next_button",
                        enabled_when="current_frame_index < len(frames) and play_timer is None",
                    ),
                    Item(name="current_frame_index", style="readonly"),
                    enabled_when='calculation_running == False and len(frames) > 0'
                )
            ),
        ),
        title='Simphony UI',
        resizable=True,
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
        self.frames = []
        self.calculation_running = True
        self.progress_dialog.open()
        future = self._executor.submit(self._run_calc_threaded)
        future.add_done_callback(self._calculation_done)

    def _add_sources_to_scene(self):
        mayavi_engine = self.mlab_model.engine
        mayavi_engine.add_source(self.sources[0])

        mayavi_engine.add_module(Surface())
        self._add_liggghts_source_to_scene(self.sources[1])
        self._add_liggghts_source_to_scene(self.sources[2])

    def _add_liggghts_source_to_scene(self, source):
        """ Function which add to liggghts source to the Mayavi scene

        Parameters
        ----------
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

        # Velocities are in meter/second, this scale factor makes
        # 1 graphical unit = 1 millimeter/sec
        arrow_scale_factor = 1.0

        arrow_glyph_module = Glyph()

        mayavi_engine.add_module(arrow_glyph_module)

        arrow_glyph_module.glyph.scale_mode = 'scale_by_vector'
        arrow_glyph_module.glyph.color_mode = 'color_by_vector'
        arrow_glyph_module.glyph.glyph.range = [0.0, 1.0]
        arrow_glyph_module.glyph.glyph.scale_factor = arrow_scale_factor

    def _remove_sources_from_scene(self):
        for source in self.sources:
            try:
                self.mlab_model.mayavi_scene.remove_child(source)
            except ValueError:
                pass

    def _run_calc_threaded(self):
        """ Function which will run the calculation. This function
        is only run by the secondary thread
        """
        try:
            return run_calc(
                self.global_settings,
                self.openfoam_settings,
                self.liggghts_settings,
                self.progress_callback,
                self._event_lock
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
        GUI.invoke_later(self._computation_done, future.result())

    def _computation_done(self, datasets):
        self.progress_dialog.update(100)
        self._append_frame(datasets)
        self.calculation_running = False

    def _append_frame(self, datasets):
        self.frames.append(
            (
                VTKMesh.from_mesh(datasets[0]),
                VTKParticles.from_particles(datasets[1]),
                VTKParticles.from_particles(datasets[2])
            )
        )

    @on_trait_change("current_frame_index,frames[]")
    def _sync_current_frame(self):
        try:
            self._current_frame = self.frames[self.current_frame_index]
        except IndexError:
            self._current_frame = None
            return

    @on_trait_change("_current_frame")
    def _update_sources_with_current_frame(self, object, name, old, new):
        if new is None:
            self._clear_sources()
        else:
            self._remove_sources_from_scene()
            for i in xrange(len(self._current_frame)):
                self.sources[i].cuds = self._current_frame[i]
            self._add_sources_to_scene()

    def progress_callback(self, datasets, current_iteration, total_iterations):
        """ Function called in the secondary thread. It will transfer the
        progress status of the calculation to the main thread

        Parameters
        ----------
        progress
            The progress of the calculation (Integer in the range [0, 100])
        """
        progress = current_iteration/total_iterations*100

        GUI.invoke_later(self._append_frame_and_continue, datasets)
        GUI.invoke_later(self.progress_dialog.update, progress)

    def _append_frame_and_continue(self, datasets):
        self._append_frame(datasets)
        self._event_lock.set()
        self.current_frame_index = len(self.frames) - 1

    def reset(self):
        """ Function which reset the Mayavi scene.
        """
        # Clear scene
        self._clear_sources()

    @on_trait_change('first_button')
    def _to_first_frame(self):
        self.current_frame_index = 0

    @on_trait_change('previous_button')
    def _to_prev_frame(self):
        frame = self.current_frame_index - 1
        if frame < 0:
            frame = 0
        self.current_frame_index = frame

    @on_trait_change('next_button')
    def _to_next_frame(self):
        frame = self.current_frame_index + 1
        if frame >= len(self.frames):
            frame = len(self.frames) - 1
        self.current_frame_index = frame

    @on_trait_change('play_stop_button')
    def _start_video(self):
        if self.play_timer is None:
            self.play_timer = Timer(500, self._next_frame_looped)
        else:
            self.play_timer.Stop()
            self.play_timer = None

    @on_trait_change('play_timer')
    def _change_play_button_label(self):
        self.play_stop_label = "Stop" if self.play_timer else "Start"

    def _next_frame_looped(self):
        if len(self.frames) == 0:
            self.current_frame_index = 0

        self.current_frame_index = (
            self.current_frame_index + 1
            ) % len(self.frames)

    def _clear_sources(self):
        """ Function which reset the sources
        """
        self._remove_sources_from_scene()
        for source in self.sources:
            source.cuds = None

    def __executor_default(self):
        return futures.ThreadPoolExecutor(max_workers=1)

    def _progress_dialog_default(self):
        return ProgressDialog(
            min=0,
            max=100,
            title='Calculation running...'
        )

    def _sources_default(self):
        return CUDSSource(), CUDSSource(), CUDSSource()

    def _global_settings_default(self):
        return GlobalParametersModel()

    def _liggghts_settings_default(self):
        return LiggghtsModel()

    def _openfoam_settings_default(self):
        return OpenfoamModel()
