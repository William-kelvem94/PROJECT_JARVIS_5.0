
import unittest
import math
from src.utils.safe_math import safe_eval

class TestSafeMath(unittest.TestCase):

    def test_basic_arithmetic(self):
        self.assertEqual(safe_eval("2 + 2"), 4)
        self.assertEqual(safe_eval("10 - 4"), 6)
        self.assertEqual(safe_eval("3 * 5"), 15)
        self.assertEqual(safe_eval("20 / 4"), 5.0)
        self.assertEqual(safe_eval("2 ** 3"), 8)
        self.assertEqual(safe_eval("10 % 3"), 1)
        self.assertEqual(safe_eval("-5"), -5)
        self.assertEqual(safe_eval("+5"), 5)

    def test_order_of_operations(self):
        self.assertEqual(safe_eval("2 + 3 * 4"), 14)
        self.assertEqual(safe_eval("(2 + 3) * 4"), 20)

    def test_functions(self):
        self.assertEqual(safe_eval("abs(-10)"), 10)
        self.assertEqual(safe_eval("min(1, 2, 3)"), 1)
        self.assertEqual(safe_eval("max(1, 2, 3)"), 3)
        self.assertEqual(safe_eval("round(3.14159, 2)"), 3.14)
        self.assertEqual(safe_eval("sum([1, 2, 3])"), 6)
        self.assertEqual(safe_eval("sqrt(16)"), 4.0)
        self.assertEqual(safe_eval("pow(2, 3)"), 8)

    def test_constants(self):
        self.assertAlmostEqual(safe_eval("pi"), math.pi)
        self.assertAlmostEqual(safe_eval("e"), math.e)

    def test_security_exploits(self):
        # Imports
        with self.assertRaises(ValueError):
            safe_eval("__import__('os').system('ls')")

        # Builtins
        with self.assertRaises(ValueError):
            safe_eval("eval('2+2')")

        # Lambda
        with self.assertRaises(ValueError):
            safe_eval("(lambda x: x)(1)")

        # Function definition
        with self.assertRaises(ValueError):
            safe_eval("def foo(): pass")

        # Attribute access
        with self.assertRaises(ValueError):
            safe_eval("''.__class__")

        # String multiplication (memory DOS)
        # Assuming safe_eval handles string literals as constants but operators check types?
        # My implementation allows ast.Constant, but operators rely on python's operator module.
        # safe_eval doesn't explicitly check types of operands in BinOp, but it relies on _eval recursively.
        # If I pass a string "a" and multiply by 1000000, it might be an issue.
        # However, ast.Constant allows strings.
        # Let's check if my implementation allows strings.
        # _eval allows ast.Constant if value is int or float.
        # So string literals should be rejected!
        with self.assertRaises(ValueError):
             safe_eval("'a' * 100")

    def test_string_literals(self):
        # String literals should be rejected
        with self.assertRaises(ValueError):
            safe_eval("'hello'")

    def test_invalid_syntax(self):
        with self.assertRaises(ValueError):
            safe_eval("2 +")
        with self.assertRaises(ValueError):
            safe_eval("2 + * 3")

    def test_long_expression(self):
        with self.assertRaises(ValueError):
            safe_eval("1" * 1001)

if __name__ == '__main__':
    unittest.main()
