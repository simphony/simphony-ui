"""
Tests
"""

import unittest


class DummyTest(unittest.TestCase):

    def setUp(self):
        """ Test initialization """
        self.a = 3

    def test_a(self):
        self.assertEqual(self.a, 3)
        self.assertNotEqual(self.a, 56)
