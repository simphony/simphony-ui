import unittest
import mock
import time
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from simphony.cuds.abc_modeling_engine import ABCModelingEngine
from simphony_ui.ui import Application, dataset2cudssource
from simphony_mayavi.sources.api import CUDSSource


class TestUI(unittest.TestCase, GuiTestAssistant):

    def setUp(self):
        GuiTestAssistant.setUp(self)
        self.application = Application()

    def test_multi_thread(self):
        openfoam_wrapper = mock.Mock(spec=ABCModelingEngine)
        liggghts_wrapper = mock.Mock(spec=ABCModelingEngine)

        openfoam_wrapper.get_dataset_names = mock.MagicMock()

        run_calc_target = 'simphony_ui.ui.run_calc'

        def mock_run_calc(global_settings, openfoam_settings,
                          liggghts_settings, progress_callback):
            time.sleep(5)
            progress_callback(50)
            time.sleep(5)
            progress_callback(100)
            return openfoam_wrapper, liggghts_wrapper

        dataset2cudssource_target = 'simphony_ui.ui.dataset2cudssource'

        def mock_dataset2cudssource(*args, **kwargs):
            return CUDSSource()

        default_module_target = 'simphony_ui.ui.default_module'

        def mock_default_module(*args, **kwargs):
            return [1]

        add_module_target = \
            'simphony_ui.ui.mayavi.tools.mlab_scene_model.Engine.add_module'

        def mock_add_module(module):
            return module

        with mock.patch(run_calc_target) as mock_run, \
                mock.patch(dataset2cudssource_target) as mock_cuds, \
                mock.patch(default_module_target) as mock_def, \
                mock.patch(add_module_target) as mock_add:

            mock_run.side_effect = mock_run_calc
            mock_cuds.side_effect = mock_dataset2cudssource
            mock_def.side_effect = mock_default_module
            mock_add.side_effect = mock_add_module

            self.assertIsNone(self.application.openfoam_wrapper)
            self.assertIsNone(self.application.liggghts_wrapper)

            with self.event_loop_until_condition(
                    lambda: (self.application.openfoam_wrapper
                             is not None),
                    timeout=20
            ):
                self.application.run_calc()

            self.assertEqual(
                self.application.openfoam_wrapper,
                openfoam_wrapper
            )
            self.assertEqual(
                self.application.liggghts_wrapper,
                liggghts_wrapper
            )

    def test_double_run(self):
        # Simulate the calculation running
        self.application.calculation_running = True
        with self.assertRaises(RuntimeError):
            self.application.run_calc()

    def test_dataset2cudssource(self):

        def mock_cudssource(cuds):
            return cuds

        with mock.patch('simphony_ui.ui.CUDSSource') as mock_cuds:
            mock_cuds.side_effect = mock_cudssource

            self.assertEqual(dataset2cudssource(36), 36)

    def test_report_failure(self):

        def mock_msg(*args, **kwargs):
            return

        with mock.patch('simphony_ui.ui.error') as mock_message:
            mock_message.side_effect = mock_msg

            # Those methods are not supposed to be called
            self.assertIsNone(self.application._run_calc_threaded())

            self.application._update_result(None)
            self.assertIsNone(self.application.openfoam_wrapper)

    def test_update_valid(self):
        self.assertFalse(self.application.valid)
        self.application.openfoam_settings.valid = True
        self.assertFalse(self.application.valid)
        self.application.liggghts_settings.valid = True
        self.assertTrue(self.application.valid)
