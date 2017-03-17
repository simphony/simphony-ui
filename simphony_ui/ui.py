from concurrent import futures
from pyface.gui import GUI

from mayavi.tools.mlab_scene_model import MlabSceneModel
from simphony_mayavi.sources.api import CUDSSource
from tvtk.pyface.scene_editor import SceneEditor
from simphony_mayavi.modules.default_module import default_module

from simphony.cuds.abc_modeling_engine import ABCModelingEngine

from traits.api import (HasStrictTraits, Instance, Button,
                        on_trait_change, Bool)
from traitsui.api import View, UItem, Tabbed, VGroup, HGroup

from pyface.api import ProgressDialog

from simphony_ui.couple_openfoam_liggghts import run_calc
from simphony_ui.global_parameters_model import GlobalParametersModel
from simphony_ui.liggghts_model.liggghts_model import LiggghtsModel
from simphony_ui.openfoam_model.openfoam_model import OpenfoamModel


class Application(HasStrictTraits):
    global_settings = Instance(GlobalParametersModel)
    liggghts_settings = Instance(LiggghtsModel)
    openfoam_settings = Instance(OpenfoamModel)

    openfoam_wrapper = Instance(ABCModelingEngine)
    liggghts_wrapper = Instance(ABCModelingEngine)

    run_button = Button("Run")

    progress_dialog = Instance(ProgressDialog)

    calculation_running = Bool(False)

    mayavi_scene = Instance(MlabSceneModel, ())

    # Private traits.
    #: Executor for the threaded action.
    _executor = Instance(futures.ThreadPoolExecutor)

    traits_view = View(
        HGroup(
            VGroup(
                Tabbed(
                    UItem('global_settings'),
                    UItem('liggghts_settings'),
                    UItem('openfoam_settings'),
                ),
                UItem(name='run_button'),
                enabled_when='calculation_running == False',
            ),
            UItem(name='mayavi_scene', editor=SceneEditor())
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
            raise BaseException('Calculation already running...')
        self.calculation_running = True
        self.progress_dialog.open()
        future = self._executor.submit(self._run_calc_threaded)
        future.add_done_callback(self._calculation_done)

    @on_trait_change('openfoam_wrapper')
    def show_openfoam_result(self):
        mayavi_engine = self.mayavi_scene.engine

        # Get Openfoam dataset
        openfoam_dataset = self.openfoam_wrapper.get_dataset(
            self.openfoam_wrapper.get_dataset_names()[0])
        openfoam_source = CUDSSource(cuds=openfoam_dataset)

        modules = default_module(openfoam_source)

        # Add Openfoam source
        mayavi_engine.add_source(openfoam_source)

        # Add default Openfoam modules
        for module in modules:
            mayavi_engine.add_module(module)

    @on_trait_change('liggghts_wrapper')
    def show_liggghts_result(self):
        mayavi_engine = self.mayavi_scene.engine

        # Get Liggghts datasets
        liggghts_flow_dataset = self.liggghts_wrapper.get_dataset('flow_particles')
        liggghts_wall_dataset = self.liggghts_wrapper.get_dataset('wall_particles')

        liggghts_flow_source = CUDSSource(cuds=liggghts_flow_dataset)
        liggghts_wall_source = CUDSSource(cuds=liggghts_wall_dataset)

        flow_modules = default_module(liggghts_flow_source)
        wall_modules = default_module(liggghts_wall_source)

        # Add Liggghts sources
        mayavi_engine.add_source(liggghts_wall_source)
        mayavi_engine.add_source(liggghts_flow_source)

        # Add default Liggghts modules
        for module in flow_modules:
            mayavi_engine.add_module(module)
        for module in wall_modules:
            mayavi_engine.add_module(module)

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

    def update_progress_bar(self, progress):
        GUI.invoke_later(self.progress_dialog.update, progress)


    def __executor_default(self):
        return futures.ThreadPoolExecutor(max_workers=1)

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
