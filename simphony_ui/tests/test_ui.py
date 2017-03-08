"""
Tests user interface
"""

import unittest
from traits.api import TraitError, HasStrictTraits
from simphony_ui.local_traits import PositiveInt, PositiveFloat


class TestModel(HasStrictTraits):

    pos_float = PositiveFloat(1e-6)
    pos_int = PositiveInt(10)


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
