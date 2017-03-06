"""
Tests
"""

import unittest
import simphony_ui.couple_CFDDEM as cfd_dem
import shutil
import os


output_dir = 'test_mesh'


class CfeDem(unittest.TestCase):

    def test_run(self):
        try:
            cfd_dem.main()
        except:
            self.fail('Error when running the main script')
        finally:
            # remove output if it exists
            shutil.rmtree(output_dir, ignore_errors=True)

    def test_output(self):
        cfd_dem.main()
        self.assertTrue(os.path.exists(output_dir))
        shutil.rmtree(output_dir, ignore_errors=True)
