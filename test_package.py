import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import MagicMock

from package import Package


class TestRegisterPackage(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.package = Package(self.mock_db)

    def test_registers_package_with_valid_data(self):
        self.package.register_package("Home Standard", "10 Mbps uncapped", 599.99)

        self.mock_db.cursor.execute.assert_called_once_with(
            "INSERT INTO packages (name, description, monthly_price) VALUES (%s, %s, %s)",
            ("Home Standard", "10 Mbps uncapped", 599.99),
        )
        self.mock_db.commit.assert_called_once()

    def test_success_message_includes_name(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.package.register_package("Home Standard", "10 Mbps uncapped", 599.99)
        self.assertIn("Home Standard", buf.getvalue())
        self.assertIn("registered successfully", buf.getvalue())

    def test_blank_name_is_rejected_without_hitting_db(self):
        self.package.register_package("   ", "10 Mbps uncapped", 599.99)

        self.mock_db.cursor.execute.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test_empty_name_prints_error(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.package.register_package("", "10 Mbps uncapped", 599.99)
        self.assertIn("cannot be blank", buf.getvalue())


class TestViewPackages(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.package = Package(self.mock_db)

    def test_queries_all_packages(self):
        self.mock_db.cursor.fetchall.return_value = []
        self.package.view_packages()
        self.mock_db.cursor.execute.assert_called_once_with("SELECT * FROM packages")

    def test_prints_no_packages_found_when_table_empty(self):
        self.mock_db.cursor.fetchall.return_value = []
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.package.view_packages()
        self.assertIn("No packages found.", buf.getvalue())

    def test_prints_each_package_row(self):
        self.mock_db.cursor.fetchall.return_value = [
            (1, "Home Standard", "10 Mbps uncapped", 599.99),
            (2, "Home Premium", "50 Mbps uncapped", 999.99),
        ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.package.view_packages()
        output = buf.getvalue()
        self.assertIn("Home Standard", output)
        self.assertIn("Home Premium", output)
        self.assertIn("R599.99", output)
        self.assertIn("R999.99", output)


class TestPackageExists(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.package = Package(self.mock_db)

    def test_package_found(self):
        self.mock_db.cursor.fetchone.return_value = (1,)

        result = self.package.package_exists("1")

        self.assertTrue(result)
        self.mock_db.cursor.execute.assert_called_once_with(
            "SELECT 1 FROM packages WHERE package_id = %s", ("1",)
        )

    def test_package_not_found(self):
        self.mock_db.cursor.fetchone.return_value = None

        result = self.package.package_exists("999")

        self.assertFalse(result)


class TestGetPackagePrice(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.package = Package(self.mock_db)

    def test_returns_price_when_package_found(self):
        self.mock_db.cursor.fetchone.return_value = (599.99,)

        result = self.package.get_package_price("1")

        self.assertEqual(result, 599.99)
        self.mock_db.cursor.execute.assert_called_once_with(
            "SELECT monthly_price FROM packages WHERE package_id = %s", ("1",)
        )

    def test_returns_none_when_package_not_found(self):
        self.mock_db.cursor.fetchone.return_value = None

        result = self.package.get_package_price("999")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()