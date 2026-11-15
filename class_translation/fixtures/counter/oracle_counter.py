import unittest

from counter import Counter


class TestCounter(unittest.TestCase):
    def test_starts_at_zero(self):
        counter = Counter()
        self.assertEqual(counter.getValue(), 0)

    def test_add(self):
        counter = Counter()
        counter.add(2)
        counter.add(3)
        self.assertEqual(counter.getValue(), 5)
