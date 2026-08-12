import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import MagicMock

from subscription import Subscription


class TestSubscribeCustomer(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_customer = MagicMock()
        self.mock_package = MagicMock()
        self.subscription = Subscription(self.mock_db, self.mock_customer, self.mock_package)

    def test_rejects_when_customer_does_not_exist(self):
        self.mock_customer.customer_exists.return_value = False

        self.subscription.subscribe_customer("999", "1")

        self.mock_customer.customer_exists.assert_called_once_with("999")
        self.mock_package.get_package_price.assert_not_called()
        self.mock_db.cursor.execute.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test_customer_not_found_prints_message(self):
        self.mock_customer.customer_exists.return_value = False

        buf = io.StringIO()
        with redirect_stdout(buf):
            self.subscription.subscribe_customer("999", "1")
        self.assertIn("Customer ID not found.", buf.getvalue())

    def test_rejects_when_package_does_not_exist(self):
        self.mock_customer.customer_exists.return_value = True
        self.mock_package.get_package_price.return_value = None

        self.subscription.subscribe_customer("1", "999")

        self.mock_package.get_package_price.assert_called_once_with("999")
        self.mock_db.cursor.execute.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test_package_not_found_prints_message(self):
        self.mock_customer.customer_exists.return_value = True
        self.mock_package.get_package_price.return_value = None

        buf = io.StringIO()
        with redirect_stdout(buf):
            self.subscription.subscribe_customer("1", "999")
        self.assertIn("Package ID not found.", buf.getvalue())

    def test_inserts_correct_customer_and_package_ids(self):
        self.mock_customer.customer_exists.return_value = True
        self.mock_package.get_package_price.return_value = 599.99

        self.subscription.subscribe_customer("1", "2")

        args, _ = self.mock_db.cursor.execute.call_args
        _, params = args
        customer_id, package_id, *_ = params
        self.assertEqual(customer_id, "1")
        self.assertEqual(package_id, "2")

    def test_calculates_vat_and_total_correctly(self):
        self.mock_customer.customer_exists.return_value = True
        self.mock_package.get_package_price.return_value = 599.99

        self.subscription.subscribe_customer("1", "2")

        args, _ = self.mock_db.cursor.execute.call_args
        _, params = args
        _, _, subtotal, vat, total = params

        expected_vat = round(599.99 * 0.15, 2)
        expected_total = round(599.99 + expected_vat, 2)
        self.assertEqual(subtotal, 599.99)
        self.assertEqual(vat, expected_vat)
        self.assertEqual(total, expected_total)

    def test_commits_after_successful_insert(self):
        self.mock_customer.customer_exists.return_value = True
        self.mock_package.get_package_price.return_value = 599.99

        self.subscription.subscribe_customer("1", "2")

        self.mock_db.commit.assert_called_once()

    def test_success_output_includes_pricing_breakdown(self):
        self.mock_customer.customer_exists.return_value = True
        self.mock_package.get_package_price.return_value = 100.0

        buf = io.StringIO()
        with redirect_stdout(buf):
            self.subscription.subscribe_customer("1", "2")

        output = buf.getvalue()
        self.assertIn("Subscription Created Successfully", output)
        self.assertIn("Subtotal: R100.00", output)
        self.assertIn("VAT (15%): R15.00", output)
        self.assertIn("Total: R115.00", output)


if __name__ == "__main__":
    unittest.main()