"""
Tests
"""

import os
import shutil
import tempfile
import unittest
import logging
from contextlib import contextmanager
from simphony.core.cuds_item import CUDSItem
from simphony.core.cuba import CUBA
from simphony_ui.couple_CFDDEM import run_calc
from simphony_ui.global_parameters_model import GlobalParametersModel
from simphony_ui.liggghts_model import LiggghtsModel
from simphony_ui.openfoam_model import OpenfoamModel


@contextmanager
def cleanup_garbage(tmpdir):
    try:
        yield
    except:
        try:
            print "Things went bad. Cleaning up ", tmpdir
            shutil.rmtree(tmpdir)
        except OSError:
            logging.exception("could not delete the tmp directory")
        raise


class TestCFEDem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.global_settings = GlobalParametersModel()
        cls.openfoam_settings = OpenfoamModel()
        cls.liggghts_settings = LiggghtsModel()

        cls.openfoam_settings.input_file = \
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'openfoam_input.txt'
            )
        cls.liggghts_settings.input_file = \
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'liggghts_input.dat'
            )

        cls.openfoam_settings.output_path = tempfile.mkdtemp()
        with cleanup_garbage(cls.openfoam_settings.output_path):
            cls.openfoam_wrapper, cls.liggghts_wrapper = run_calc(
                cls.global_settings,
                cls.openfoam_settings,
                cls.liggghts_settings
            )
            super(TestCFEDem, cls).setUpClass()

    def test_output(self):
        self.assertTrue(os.path.exists(
            os.path.join(
                self.openfoam_settings.output_path,
                self.openfoam_settings.mesh_name)
        ))

    def test_nb_entities(self):
        flow_dataset = self.liggghts_wrapper.get_dataset(
            self.liggghts_wrapper.get_dataset_names()[0])
        self.assertEqual(flow_dataset.count_of(CUDSItem.PARTICLE), 200)
        self.assertEqual(flow_dataset.count_of(CUDSItem.BOND), 0)

        mesh_dataset = self.openfoam_wrapper.get_dataset(
            self.openfoam_wrapper.get_dataset_names()[0])
        self.assertEqual(mesh_dataset.count_of(CUDSItem.CELL), 15744)
        self.assertEqual(mesh_dataset.count_of(CUDSItem.FACE), 63448)
        self.assertEqual(mesh_dataset.count_of(CUDSItem.EDGE), 0)
        self.assertEqual(mesh_dataset.count_of(CUDSItem.POINT), 32432)

    def test_velocity(self):
        mesh_dataset = self.openfoam_wrapper.get_dataset(
            self.openfoam_wrapper.get_dataset_names()[0])
        avg_velo = 0.0
        for cell in mesh_dataset.iter_cells():
            avg_velo += cell.data[CUBA.VELOCITY][0]
        avg_velo = avg_velo/mesh_dataset.count_of(CUDSItem.CELL)
        self.assertAlmostEqual(avg_velo, 0.00151286)
