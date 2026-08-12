import unittest
from unittest.mock import patch

from main import is_float, get_input, confirm, OptionException

# NOTE: customer_exists() and package_exists() no longer live in main.py —
# that existence-checking logic moved to Customer.customer_exists() and
# Package.package_exists() as part of the OOP refactor. Tests for that
# behaviour belong alongside customer.py / package.py, not here.


class TestIsFloat(unittest.TestCase):
    def test_valid_integer_string(self):
        self.assertTrue(is_float("599"))

    def test_valid_decimal_string(self):
        self.assertTrue(is_float("599.99"))

    def test_invalid_text(self):
        self.assertFalse(is_float("abc"))

    def test_empty_string(self):
        self.assertFalse(is_float(""))


class TestGetInput(unittest.TestCase):
    @patch("builtins.input", return_value="cancel")
    def test_cancel_returns_none(self, mock_input):
        result = get_input("Enter something:")
        self.assertIsNone(result)

    @patch("builtins.input", side_effect=["", "Home Standard"])
    def test_blank_then_valid_retries(self, mock_input):
        result = get_input("Enter package name:")
        self.assertEqual(result, "Home Standard")
        self.assertEqual(mock_input.call_count, 2)

    @patch("builtins.input", side_effect=["abc", "599.99"])
    def test_validate_function_rejects_then_accepts(self, mock_input):
        result = get_input(
            "Enter price:",
            validate=is_float,
            error_msg="Must be numeric",
        )
        self.assertEqual(result, "599.99")


class TestConfirm(unittest.TestCase):
    @patch("builtins.input", return_value="y")
    def test_yes_returns_true(self, mock_input):
        self.assertTrue(confirm())

    @patch("builtins.input", return_value="n")
    def test_no_returns_false(self, mock_input):
        self.assertFalse(confirm())

    @patch("builtins.input", side_effect=["maybe", "yes"])
    def test_invalid_then_valid_retries(self, mock_input):
        self.assertTrue(confirm())
        self.assertEqual(mock_input.call_count, 2)


class TestOptionException(unittest.TestCase):
    def test_is_subclass_of_exception(self):
        self.assertTrue(issubclass(OptionException, Exception))

    def test_raises_with_message(self):
        with self.assertRaises(OptionException) as ctx:
            raise OptionException("'9' is not a valid option. Please choose 1-6.")
        self.assertIn("not a valid option", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()