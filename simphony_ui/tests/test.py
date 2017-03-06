"""
Tests
"""

import unittest
import simphony_ui.couple_CFDDEM as cfd_dem
import shutil


output_dir = 'test_mesh'


class CFD_DEM(unittest.TestCase):

    def test_run(self):
        try:
            cfd_dem.main()
        except:
            self.fail('Error when running the main script')
        finally:
            # remove output if it exists
            shutil.rmtree(output_dir, ignore_errors=True)
