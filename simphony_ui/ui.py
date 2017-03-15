import threading
from pyface.api import GUI
import copy
from traits.api import HasStrictTraits, Instance, Button, on_trait_change
from traitsui.api import View, UItem, Tabbed, VGroup
from simphony.core.cuds_item import CUDSItem
from simphony.core.cuba import CUBA
from simphony_ui.couple_openfoam_liggghts import run_calc
from simphony_ui.global_parameters_model import GlobalParametersModel
from simphony_ui.liggghts_model.liggghts_model import LiggghtsModel
from simphony_ui.openfoam_model.openfoam_model import OpenfoamModel


class ThreadedCalculation(threading.Thread):

    def __init__(
            self,
            callback,
            global_settings,
            openfoam_settings,
            liggghts_settings,
            **kwargs):
        threading.Thread.__init__(self, **kwargs)
        self.callback = callback
        self.global_settings = global_settings
        self.openfoam_settings = openfoam_settings
        self.liggghts_settings = liggghts_settings
        self.openfoam_wrapper = None
        self.liggghts_wrapper = None

    def run(self):
        print "Performing computation..."
        self.openfoam_wrapper, self.liggghts_wrapper = run_calc(
            self.global_settings,
            self.openfoam_settings,
            self.liggghts_settings
        )
        print('Done')
        GUI.invoke_later(self.callback)


class Application(HasStrictTraits):

    global_settings = Instance(GlobalParametersModel)
    liggghts_settings = Instance(LiggghtsModel)
    openfoam_settings = Instance(OpenfoamModel)

    run_button = Button("Run")

    thread_calculation = Instance(ThreadedCalculation)

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
        self.thread_calculation = ThreadedCalculation(
            self.get_wrappers,
            copy.deepcopy(self.global_settings),
            copy.deepcopy(self.openfoam_settings),
            copy.deepcopy(self.liggghts_settings)
        )
        self.thread_calculation.start()

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
