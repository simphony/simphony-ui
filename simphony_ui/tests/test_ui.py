import unittest
import mock
import time
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from simphony.cuds.abc_modeling_engine import ABCModelingEngine
from simphony_ui.ui import Application


class TestUI(unittest.TestCase, GuiTestAssistant):

    def setUp(self):
        GuiTestAssistant.setUp(self)
        self.application = Application()

    def test_multi_thread(self):
        openfoam_wrapper = mock.Mock(spec=ABCModelingEngine)
        liggghts_wrapper = mock.Mock(spec=ABCModelingEngine)

        def mock_wait(*args, **kwargs):
            time.sleep(10)
            return openfoam_wrapper, liggghts_wrapper

        with mock.patch('simphony_ui.ui.run_calc') as mock_run:
            mock_run.side_effect = mock_wait

            self.assertIsNone(self.application.openfoam_wrapper)
            self.assertIsNone(self.application.liggghts_wrapper)

            with self.event_loop_until_condition(
                    lambda: self.application.openfoam_wrapper is not None,
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
        with self.assertRaises(BaseException):
            self.application.run_calc()
