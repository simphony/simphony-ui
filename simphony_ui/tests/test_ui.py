"""
Tests user interface
"""

import unittest
import simphony_ui.ui as ui
from traits.api import TraitError


class TestModel(ui.HasStrictTraits):

    pos_float = ui.PositiveFloat(1e-6)
    pos_int = ui.PositiveInt(10)


class TestUI(unittest.TestCase):

    def setUp(self):
        self.test_model = TestModel()

    def test_positive_float(self):
        self.test_model.validate_trait('pos_float', 33.3)
        with self.assertRaises(TraitError):
            self.test_model.validate_trait('pos_float', -2.3)

    def test_positive_int(self):
        self.test_model.validate_trait('pos_int', 56)
        with self.assertRaises(TraitError):
            self.test_model.validate_trait('pos_int', -2)
        with self.assertRaises(TraitError):
            self.test_model.validate_trait('pos_int', 23.3)
