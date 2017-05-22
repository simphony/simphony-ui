import unittest
import mock
import os
import tempfile
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from simphony_mayavi.cuds.vtk_mesh import VTKMesh
from simphony_mayavi.cuds.vtk_particles import VTKParticles

from simphony_ui.couple_openfoam_liggghts import run_calc
from simphony_ui.global_parameters_model import GlobalParametersModel
from simphony_ui.liggghts_model.liggghts_model import LiggghtsModel
from simphony_ui.openfoam_model.openfoam_model import OpenfoamModel
from simphony_ui.tests.test_utils import cleanup_garbage
from simphony_ui.ui import Application, dataset2cudssource


class TestUI(unittest.TestCase, GuiTestAssistant):

    def setUp(self):
        GuiTestAssistant.setUp(self)
        self.application = Application()

    def test_multi_thread(self):
        app = self.application
        app.openfoam_settings.input_file = os.path.join(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'fixtures'
            ),
            'openfoam_input.txt'
        )
        app.liggghts_settings.input_file = os.path.join(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'fixtures'
            ),
            'liggghts_input.dat'
        )
        app.global_settings.num_iterations = 2
        temp_dir = tempfile.mkdtemp()
        with cleanup_garbage(temp_dir):
            app.openfoam_settings.output_path = temp_dir

            self.assertEqual(len(app.frames), 0)

            app.run_calc()

            with self.event_loop_until_condition(
                    lambda: (len(app.frames) != 0),
                    timeout=30
            ):
                pass

            with self.event_loop_until_condition(
                    lambda: not app.calculation_running,
                    timeout=30
            ):
                pass

            self.assertNotEqual(len(app.frames), 0)
            self.assertEqual(len(app.frames[0]), 3)

            # Last added module was the arrow_module
            self.assertEqual(
                app.sources[1].children[0].children[0].glyph.scale_mode,
                'scale_by_scalar')
            self.assertEqual(
                app.sources[1].children[0].children[1].glyph.scale_mode,
                'scale_by_vector')
            self.assertEqual(
                app.sources[1].children[0].children[1].glyph.color_mode,
                'color_by_vector')

            app.reset()

            app.run_calc()

            with self.event_loop_until_condition(
                    lambda: (len(app.frames) != 0),
                    timeout=30
            ):
                pass

            with self.event_loop_until_condition(
                    lambda: not app.calculation_running,
                    timeout=30
            ):
                pass

            self.assertEqual(
                app.sources[1].children[0].children[0].glyph.scale_mode,
                'scale_by_scalar')
            self.assertEqual(
                app.sources[1].children[0].children[1].glyph.scale_mode,
                'scale_by_vector')
            self.assertEqual(
                app.sources[1].children[0].children[1].glyph.color_mode,
                'color_by_vector')

    def test_ui_timeout(self):
        openfoam_settings = OpenfoamModel()
        openfoam_settings.input_file = os.path.join(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'fixtures'
            ),
            'openfoam_input.txt')
        liggghts_settings = LiggghtsModel()
        liggghts_settings.input_file = os.path.join(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'fixtures'
            ),
            'liggghts_input.dat')

        global_settings = GlobalParametersModel()

        def progress_callback(*args, **kwargs):
            pass

        event_lock = mock.Mock()
        event_lock.wait.return_value = False
        temp_dir = tempfile.mkdtemp()
        with cleanup_garbage(temp_dir):
            self.assertIsNone(
                run_calc(
                    global_settings,
                    openfoam_settings,
                    liggghts_settings,
                    progress_callback,
                    event_lock))

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
            self.assertEquals(len(self.application.frames), 0)

    def test_update_valid(self):
        self.assertFalse(self.application.valid)
        self.application.openfoam_settings.valid = True
        self.assertFalse(self.application.valid)
        self.application.liggghts_settings.valid = True
        self.assertTrue(self.application.valid)

    def test_movie_controls(self):
        app = self.application
        app.frames = [
            (VTKMesh('mesh'),
             VTKParticles("flow_particles"),
             VTKParticles("wall_particles")),
            (VTKMesh('mesh'),
             VTKParticles("flow_particles"),
             VTKParticles("wall_particles")),
            (VTKMesh('mesh'),
             VTKParticles("flow_particles"),
             VTKParticles("wall_particles")),
        ]

        self.assertEqual(app.current_frame_index, 0)
        self.assertEqual(app._current_frame, app.frames[0])
        app._to_next_frame()
        self.assertEqual(app.current_frame_index, 1)
        self.assertEqual(app._current_frame, app.frames[1])
        app._to_next_frame()
        self.assertEqual(app.current_frame_index, 2)
        self.assertEqual(app._current_frame, app.frames[2])
        app._to_next_frame()
        self.assertEqual(app.current_frame_index, 2)
        self.assertEqual(app._current_frame, app.frames[2])
        app._to_prev_frame()
        self.assertEqual(app.current_frame_index, 1)
        self.assertEqual(app._current_frame, app.frames[1])
        app._to_first_frame()
        self.assertEqual(app.current_frame_index, 0)
        self.assertEqual(app._current_frame, app.frames[0])

        self.assertIsNone(app.play_timer)
        app._start_stop_video()
        self.assertIsNotNone(app.play_timer)

        with self.event_loop_until_condition(
                lambda: app.current_frame_index == 2,
                timeout=30
        ):
            pass

        # check if it rolls over
        with self.event_loop_until_condition(
                lambda: app.current_frame_index == 0,
                timeout=30
        ):
            pass

        app._start_stop_video()
        self.assertIsNone(app.play_timer)
