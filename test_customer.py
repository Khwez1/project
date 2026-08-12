import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import MagicMock

from customer import Customer


class TestRegisterCustomer(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.customer = Customer(self.mock_db)

    def test_registers_customer_with_valid_data(self):
        self.customer.register_customer("Jane Doe", "0821234567", "jane@example.com")

        self.mock_db.cursor.execute.assert_called_once_with(
            "INSERT INTO customers (name, phone, email) VALUES (%s, %s, %s)",
            ("Jane Doe", "0821234567", "jane@example.com"),
        )
        self.mock_db.commit.assert_called_once()

    def test_success_message_includes_name(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.customer.register_customer("Jane Doe", "0821234567", "jane@example.com")
        self.assertIn("Jane Doe", buf.getvalue())
        self.assertIn("registered successfully", buf.getvalue())

    def test_blank_name_is_rejected_without_hitting_db(self):
        self.customer.register_customer("   ", "0821234567", "jane@example.com")

        self.mock_db.cursor.execute.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test_empty_name_prints_error(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.customer.register_customer("", "0821234567", "jane@example.com")
        self.assertIn("cannot be blank", buf.getvalue())


class TestViewCustomers(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.customer = Customer(self.mock_db)

    def test_queries_all_customers(self):
        self.mock_db.cursor.fetchall.return_value = []
        self.customer.view_customers()
        self.mock_db.cursor.execute.assert_called_once_with("SELECT * FROM customers")

    def test_prints_no_customers_found_when_table_empty(self):
        self.mock_db.cursor.fetchall.return_value = []
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.customer.view_customers()
        self.assertIn("No customers found.", buf.getvalue())

    def test_prints_each_customer_row(self):
        self.mock_db.cursor.fetchall.return_value = [
            (1, "Jane Doe", "0821234567", "jane@example.com"),
            (2, "John Smith", "0839876543", "john@example.com"),
        ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.customer.view_customers()
        output = buf.getvalue()
        self.assertIn("Jane Doe", output)
        self.assertIn("John Smith", output)
        self.assertIn("ID: 1", output)
        self.assertIn("ID: 2", output)


class TestCustomerExists(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.customer = Customer(self.mock_db)

    def test_customer_found(self):
        self.mock_db.cursor.fetchone.return_value = (1, "Jane Doe", "0821234567", "jane@example.com")

        result = self.customer.customer_exists("1")

        self.assertTrue(result)
        self.mock_db.cursor.execute.assert_called_once_with(
            "SELECT * FROM customers WHERE customer_id = %s", ("1",)
        )

    def test_customer_not_found(self):
        self.mock_db.cursor.fetchone.return_value = None

        result = self.customer.customer_exists("999")

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()