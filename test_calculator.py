import unittest

from calculator import power


class PowerTests(unittest.TestCase):
    def test_positive_integer_exponent(self):
        self.assertEqual(power(2, 3), 8)

    def test_zero_exponent(self):
        self.assertEqual(power(9, 0), 1)

    def test_negative_exponent(self):
        self.assertEqual(power(2, -3), 0.125)

    def test_fractional_exponent(self):
        self.assertEqual(power(9, 0.5), 3.0)


if __name__ == "__main__":
    unittest.main()
