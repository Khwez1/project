import mysql.connector as mysql, sys, logging

from database import Database
from customer import Customer
from package import Package
from subscription import Subscription

logging.basicConfig(level="INFO")

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def get_input(prompt, validate=None, error_msg="Invalid input, try again."):
    """
    Keeps asking until the user gives a valid value or types 'cancel'.
    Returns the valid value, or None if the user cancelled.
    validate: optional function that returns True/False for the raw string.
    """
    while True:
        value = input(prompt + " (or 'cancel' to go back): ").strip()
        if value.lower() == "cancel":
            return None
        if not value:
            print("This field can't be blank.\n")
            continue
        if validate and not validate(value):
            print(error_msg + "\n")
            continue
        return value

def confirm(prompt="Save this? (y/n): "):
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please type y or n.\n")

def add_package_menu(package):
    print("Preparing a new package... (type 'cancel' at any prompt to go back)\r\n")

    package_name = get_input("Please input package name: ")
    if package_name is None:
        print("Cancelled. Returning to menu.\n")
        return

    description = get_input("Please input package description: ")
    if description is None:
        print("Cancelled. Returning to menu.\n")
        return

    monthly_price = get_input(
        "Please input package monthly price: ",
        validate=lambda v: is_float(v),
        error_msg="Price must be a number, e.g: 599.99",
    )
    if monthly_price is None:
        print("Cancelled. Returning to menu.\n")
        return

    try:
        monthly_price = float(monthly_price)
    except ValueError:
        print("Price must be a number. Cancelled.\n")
        return

    print(f"\nAbout to save: {package_name} | {description} | R{monthly_price:.2f}")
    if not confirm():
        print("Not saved. Returning to menu.\n")
        return

    try:
        package.register_package(package_name, description, monthly_price)
    except mysql.Error as e:
        logging.error(e)
        print("Something went wrong saving to the database. Please try again.\n")
        package.db.connection.rollback()

def register_customers_menu(customer):
    print("Welcome to the register customers menu\r\n")

    customer_name = get_input("Please input customer's name:")
    if customer_name is None:
        print("Cancelled. Returning to menu.\n")
        return

    phone_number = get_input("Please input customer's phone number:")
    if phone_number is None:
        print("Cancelled. Returning to menu.\n")
        return

    email_address = get_input("Please input customer's email:")
    if email_address is None:
        print("Cancelled. Returning to menu.\n")
        return

    print(f"\nAbout to save: {customer_name} | {phone_number} | {email_address}")
    if not confirm():
        print("Not saved. Returning to menu.\n")
        return

    try:
        customer.register_customer(customer_name, phone_number, email_address)
    except mysql.Error as e:
        logging.error(e)
        print("Something went wrong saving to the database. Please try again.\n")
        customer.db.connection.rollback()

def subscribe_customers_menu(customer, package, subscription):
    print("Welcome to the subscribe customers menu\r\n")

    customer_id = get_input(
        "Please input customer_ID:",
        validate=lambda v: v.isdigit() and customer.customer_exists(v),
        error_msg="That customer ID doesn't exist. Check View Customers and try again.",
    )
    if customer_id is None:
        print("Cancelled. Returning to menu.\n")
        return

    package_id = get_input(
        "Please input package_ID",
        validate=lambda v: v.isdigit() and package.package_exists(v),
        error_msg="That package ID doesn't exist. Check View Packages and try again."
    )
    if package_id is None:
        print("Cancelled. Returning to menu.\n")
        return

    print(f"\nAbout to save: {customer_id} | {package_id}")
    if not confirm():
        print("Not saved. Returning to menu.\n")
        return

    try:
        subscription.subscribe_customer(customer_id, package_id)
    except mysql.Error as e:
        logging.error(e)
        print("Something went wrong saving to the database. Please try again.\n")
        subscription.db.connection.rollback()


class OptionException(Exception):
    """Raised when the user enters a number outside the valid menu range."""
    pass

def main():
    db = Database()
    customer = Customer(db)
    package = Package(db)
    subscription = Subscription(db, customer, package)

    print("Welcome to Backspace Technologies Subscription System")
    try:
        while True:
            print("\nPlease choose an option:")
            print("1. Add Package")
            print("2. View Packages")
            print("3. Register Customer")
            print("4. View Customer")
            print("5. Subscribe Customer")
            print("6. Exit program")
            option = input()

            try:
                choice = int(option)
                if choice < 1 or choice > 6:
                    raise OptionException(f"'{choice}' is not a valid option. Please choose 1-6." )
            except ValueError:
                print("Please input a number")
                continue
            except OptionException as e:
                logging.error(e)
                continue

            if choice == 1:
                add_package_menu(package)
            elif choice == 2:
                package.view_packages()
            elif choice == 3:
                register_customers_menu(customer)
            elif choice == 4:
                customer.view_customers()
            elif choice == 5:
                subscribe_customers_menu(customer, package, subscription)
            elif choice == 6:
                print("Exiting program... Goodbye!")
                db.close()
                sys.exit(0)
            else:
                print("Please select a valid option (1-6).\n")
                
    except KeyboardInterrupt:
        print("\n\nInterrupted. Exiting program... Goodgbye!")
        db.close()
        sys.exit(0)

if __name__ == "__main__":
    main()