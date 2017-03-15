from concurrent import futures
from pyface.gui import GUI
from simphony.cuds.abc_modeling_engine import ABCModelingEngine

from traits.api import HasStrictTraits, Instance, Button, on_trait_change
from traitsui.api import View, UItem, Tabbed, VGroup
from simphony.core.cuds_item import CUDSItem
from simphony.core.cuba import CUBA
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
        ),
        title='Simphony UI',
        resizable=True,
        style='custom',
        width=1.0,
        height=1.0
    )

    @on_trait_change('run_button')
    def run_calc(self):
        future = self._executor.submit(self._run_calc_threaded)
        future.add_done_callback(self._calculation_done)

    def _run_calc_threaded(self):
        return run_calc(
            self.global_settings,
            self.openfoam_settings,
            self.liggghts_settings
        )

    def _calculation_done(self, result):
        GUI.invoke_later(self._update_result, result)

    def _update_result(self, result):
        self.openfoam_wrapper = result.openfoam_wrapper
        self.liggghts_wrapper = result.liggghts_wrapper

    def __executor_default(self):
        return futures.ThreadPoolExecutor(max_workers=1)

    def get_wrappers(self):
        openfoam_wrapper = self.thread_calculation.openfoam_wrapper
        # liggghts_wrapper = self.thread_calculation.liggghts_wrapper

        mesh_dataset = openfoam_wrapper.get_dataset(
            openfoam_wrapper.get_dataset_names()[0])
        avg_velo = 0.0
        for cell in mesh_dataset.iter_cells():
            avg_velo += cell.data[CUBA.VELOCITY][0]
        avg_velo = avg_velo / mesh_dataset.count_of(CUDSItem.CELL)
        print avg_velo

    def _global_settings_default(self):
        return GlobalParametersModel()

    def _liggghts_settings_default(self):
        return LiggghtsModel()

    def _openfoam_settings_default(self):
        return OpenfoamModel()

if __name__ == '__main__':
    ui = Application()
    ui.configure_traits()
