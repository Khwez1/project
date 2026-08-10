import unittest
from unittest.mock import patch, MagicMock

import main as main_module
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


class TestMainRouting(unittest.TestCase):
    def _run_main_with_inputs(self, inputs):
        """Runs main() with a scripted sequence of typed inputs. The
        sequence should always end in '6' so the loop exits normally
        instead of running forever."""
        with self.assertRaises(SystemExit):
            with patch("builtins.input", side_effect=inputs):
                main_module.main()

    @patch("main.mysql")
    @patch("main.subscribe_customers_menu")
    @patch("main.view_customers")
    @patch("main.register_customers_menu")
    @patch("main.view_packages")
    @patch("main.add_package_menu")
    def test_routes_to_correct_submenu(
        self, mock_add_package, mock_view_packages, mock_register,
        mock_view_customers, mock_subscribe, mock_mysql
    ):
        mock_mysql.connect.return_value = MagicMock()
        routing_map = {
            "1": mock_add_package,
            "2": mock_view_packages,
            "3": mock_register,
            "4": mock_view_customers,
            "5": mock_subscribe,
        }
        all_mocks = list(routing_map.values())

        for choice, expected_mock in routing_map.items():
            with self.subTest(choice=choice):
                for m in all_mocks:
                    m.reset_mock()
                self._run_main_with_inputs([choice, "6"])
                expected_mock.assert_called_once()
                for m in all_mocks:
                    if m is not expected_mock:
                        m.assert_not_called()

    @patch("main.mysql")
    def test_choice_6_exits_and_closes_connection(self, mock_mysql):
        mock_connection = MagicMock()
        mock_mysql.connect.return_value = mock_connection

        self._run_main_with_inputs(["6"])

        mock_connection.close.assert_called_once()

    @patch("main.mysql")
    def test_non_numeric_input_does_not_crash_and_retries(self, mock_mysql):
        mock_mysql.connect.return_value = MagicMock()

        # "abc" should be rejected and re-prompted, not crash the program
        self._run_main_with_inputs(["abc", "6"])

    @patch("main.mysql")
    def test_out_of_range_choice_raises_option_exception_and_retries(self, mock_mysql):
        mock_mysql.connect.return_value = MagicMock()

        # "9" is a valid number but out of the 1-6 range
        self._run_main_with_inputs(["9", "6"])

    @patch("main.mysql")
    def test_keyboard_interrupt_exits_cleanly_and_closes_connection(self, mock_mysql):
        mock_connection = MagicMock()
        mock_mysql.connect.return_value = mock_connection

        # Simulate Ctrl+C happening while the program is waiting on input()
        with self.assertRaises(SystemExit):
            with patch("builtins.input", side_effect=KeyboardInterrupt):
                main_module.main()

        mock_connection.close.assert_called_once()

if __name__ == "__main__":
    unittest.main()