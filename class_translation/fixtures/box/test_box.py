import unittest

from Box import Box


class TestBox(unittest.TestCase):
    def test_starts_at_zero(self):
        box = Box()
        self.assertEqual(box.getValue(), 0)

    def test_add(self):
        box = Box()
        box.add(2)
        box.add(3)
        self.assertEqual(box.getValue(), 5)
