import unittest
from calculator import add


class AdditionTests(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(add(7, 5), 12)

    def test_negative(self):
        self.assertEqual(add(-4, -9), -13)

    def test_zero(self):
        self.assertEqual(add(0, 8), 8)

    def test_decimal(self):
        self.assertAlmostEqual(add(1.25, 2.5), 3.75)


if __name__ == '__main__':
    unittest.main()
