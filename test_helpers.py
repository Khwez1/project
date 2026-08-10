import unittest
from unittest.mock import patch, MagicMock

from main import is_float, customer_exists, package_exists, get_input, confirm, OptionException


class TestIsFloat(unittest.TestCase):
    def test_valid_integer_string(self):
        self.assertTrue(is_float("599"))

    def test_valid_decimal_string(self):
        self.assertTrue(is_float("599.99"))

    def test_invalid_text(self):
        self.assertFalse(is_float("abc"))

    def test_empty_string(self):
        self.assertFalse(is_float(""))


class TestCustomerExists(unittest.TestCase):
    def test_customer_found(self):
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchone.return_value = (1,)

        result = customer_exists(mock_connection, "5")

        self.assertTrue(result)
        mock_cursor.execute.assert_called_once_with(
            "SELECT 1 FROM customers WHERE customer_id = %s", ("5",)
        )
        mock_cursor.close.assert_called_once()

    def test_customer_not_found(self):
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchone.return_value = None

        result = customer_exists(mock_connection, "999")

        self.assertFalse(result)


class TestPackageExists(unittest.TestCase):
    def test_package_found(self):
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchone.return_value = (1,)

        result = package_exists(mock_connection, "2")

        self.assertTrue(result)

    def test_package_not_found(self):
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchone.return_value = None

        result = package_exists(mock_connection, "999")

        self.assertFalse(result)


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