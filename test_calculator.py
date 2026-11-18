import unittest

from calculator import CalculatorApp, power, toggle_window


class PowerTests(unittest.TestCase):
    def test_positive_integer_exponent(self):
        self.assertEqual(power(2, 3), 8)

    def test_zero_exponent(self):
        self.assertEqual(power(9, 0), 1)

    def test_negative_exponent(self):
        self.assertEqual(power(2, -3), 0.125)

    def test_fractional_exponent(self):
        self.assertEqual(power(9, 0.5), 3.0)


class ToggleWindowTests(unittest.TestCase):
    class FakeRoot:
        def __init__(self, state):
            self._state = state
            self.deiconified = False
            self.lifted = False
            self.focused = False
            self.withdrawn = False

        def state(self):
            return self._state

        def deiconify(self):
            self.deiconified = True
            self._state = "normal"

        def lift(self):
            self.lifted = True

        def focus_force(self):
            self.focused = True

        def withdraw(self):
            self.withdrawn = True
            self._state = "withdrawn"

    def test_f10_opens_withdrawn_window(self):
        root = self.FakeRoot("withdrawn")

        result = toggle_window(root)

        self.assertEqual(result, "break")
        self.assertTrue(root.deiconified)
        self.assertTrue(root.lifted)
        self.assertTrue(root.focused)

    def test_f10_closes_open_window(self):
        root = self.FakeRoot("normal")

        result = toggle_window(root)

        self.assertEqual(result, "break")
        self.assertTrue(root.withdrawn)


class CalculatorOperationTests(unittest.TestCase):
    def test_arithmetic_operations(self):
        self.assertEqual(CalculatorApp._calculate(7, 3, "+"), 10)
        self.assertEqual(CalculatorApp._calculate(7, 3, "-"), 4)
        self.assertEqual(CalculatorApp._calculate(7, 3, "*"), 21)
        self.assertEqual(CalculatorApp._calculate(8, 2, "/"), 4)
        self.assertEqual(CalculatorApp._calculate(2, 3, "^"), 8)


if __name__ == "__main__":
    unittest.main()
