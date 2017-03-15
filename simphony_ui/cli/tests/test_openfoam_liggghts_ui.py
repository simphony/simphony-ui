import unittest
import mock

from simphony_ui.cli.openfoam_liggghts_ui import main


class TestOpenFoamLiggghtsUI(unittest.TestCase):
    def test_execution(self):
        with mock.patch(
                "simphony_ui.ui.Application.configure_traits"
                ) as mock_configure_traits:

            main()

            self.assertTrue(mock_configure_traits.called)
