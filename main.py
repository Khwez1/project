import os
import sys
import logging
import mysql.connector as mysql

from termcolor import colored
from colorama import init as colorama_init

from database import Database
from customer import Customer
from package import Package
from subscription import Subscription

colorama_init(autoreset=True)  # Makes ANSI color codes work in Windows terminals (cmd.exe / PowerShell), not just Linux/Mac.
logging.basicConfig(level="INFO")

BANNER_WIDTH = 60

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    print(colored("=" * BANNER_WIDTH, "cyan"))
    print(colored("Backspace Technologies Subscription System".center(BANNER_WIDTH), "cyan", attrs=["bold"]))
    print(colored("=" * BANNER_WIDTH, "cyan"))

def press_enter_to_continue():
    input(colored("\nPress Enter to continue...", "white", attrs=["dark"]))
    clear_screen()

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
    print(colored("Preparing a new package... (type 'cancel' at any prompt to go back)\r\n", "cyan"))

    package_name = get_input(colored("Please input package name:", "cyan"))
    if package_name is None:
        print(colored("Cancelled. Returning to menu.\n", "yellow"))
        return

    description = get_input(colored("Please input package description:", "cyan"))
    if description is None:
        print(colored("Cancelled. Returning to menu.\n", "yellow"))
        return

    monthly_price = get_input(
        colored("Please input package monthly price:", "cyan"),
        validate=lambda v: is_float(v),
        error_msg=colored("Price must be a number, e.g: 599.99", "red"),
    )
    if monthly_price is None:
        print(colored("Cancelled. Returning to menu.\n", "yellow"))
        return

    try:
        monthly_price = float(monthly_price)
    except ValueError:
        print(colored("Price must be a number. Cancelled.\n", "red"))
        return

    print(colored(f"\nAbout to save: {package_name} | {description} | R{monthly_price:.2f}", "magenta"))
    if not confirm(colored("Save this? (y/n): ", "yellow")):
        print(colored("Not saved. Returning to menu.\n", "yellow"))
        return

    try:
        package.register_package(package_name, description, monthly_price)
    except mysql.Error as e:
        logging.error(e)
        print(colored("Something went wrong saving to the database. Please try again.\n", "red"))
        package.db.connection.rollback()

def register_customers_menu(customer):
    print(colored("Welcome to the register customers menu\r\n", "cyan"))

    customer_name = get_input(colored("Please input customer's name:", "cyan"))
    if customer_name is None:
        print(colored("Cancelled. Returning to menu.\n", "yellow"))
        return

    phone_number = get_input(colored("Please input customer's phone number:", "cyan"))
    if phone_number is None:
        print(colored("Cancelled. Returning to menu.\n", "yellow"))
        return

    email_address = get_input(colored("Please input customer's email:", "cyan"))
    if email_address is None:
        print(colored("Cancelled. Returning to menu.\n", "yellow"))
        return

    print(colored(f"\nAbout to save: {customer_name} | {phone_number} | {email_address}", "magenta"))
    if not confirm(colored("Save this? (y/n): ", "yellow")):
        print(colored("Not saved. Returning to menu.\n", "yellow"))
        return

    try:
        customer.register_customer(customer_name, phone_number, email_address)
    except mysql.Error as e:
        logging.error(e)
        print(colored("Something went wrong saving to the database. Please try again.\n", "red"))
        customer.db.connection.rollback()

def subscribe_customers_menu(customer, package, subscription):
    print(colored("Welcome to the subscribe customers menu\r\n", "cyan"))

    customer_id = get_input(
        colored("Please input customer_ID:", "cyan"),
        validate=lambda v: v.isdigit() and customer.customer_exists(v),
        error_msg=colored("That customer ID doesn't exist. Check View Customers and try again.", "red"),
    )
    if customer_id is None:
        print(colored("Cancelled. Returning to menu.\n", "yellow"))
        return

    package_id = get_input(
        colored("Please input package_ID:", "cyan"),
        validate=lambda v: v.isdigit() and package.package_exists(v),
        error_msg=colored("That package ID doesn't exist. Check View Packages and try again.", "red"),
    )
    if package_id is None:
        print(colored("Cancelled. Returning to menu.\n", "yellow"))
        return

    print(colored(f"\nAbout to save: {customer_id} | {package_id}", "magenta"))
    if not confirm(colored("Save this? (y/n): ", "yellow")):
        print(colored("Not saved. Returning to menu.\n", "yellow"))
        return

    try:
        subscription.subscribe_customer(customer_id, package_id)
    except mysql.Error as e:
        logging.error(e)
        print(colored("Something went wrong saving to the database. Please try again.\n", "red"))
        subscription.db.connection.rollback()


class OptionException(Exception):
    """Raised when the user enters a number outside the valid menu range."""
    pass

def main():
    db = Database()
    customer = Customer(db)
    package = Package(db)
    subscription = Subscription(db, customer, package)

    clear_screen()
    print_banner()
    try:
        while True:
            print(colored("\nPlease choose an option:", "yellow"))
            print("1. Add Package")
            print("2. View Packages")
            print("3. Register Customer")
            print("4. View Customer")
            print("5. Subscribe Customer")
            print("6. Exit program")
            option = input(colored("> ", "green"))

            try:
                choice = int(option)
                if choice < 1 or choice > 6:
                    raise OptionException(f"'{choice}' is not a valid option. Please choose 1-6." )
            except ValueError:
                print(colored("Please input a number", "red"))
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
                print(colored("Exiting program... Goodbye!", "green"))
                db.close()
                sys.exit(0)
            else:
                print(colored("Please select a valid option (1-6).\n", "red"))
                continue

            press_enter_to_continue()
            print_banner()

    except KeyboardInterrupt:
        print(colored("\n\nInterrupted. Exiting program... Goodgbye!", "red"))
        db.close()
        sys.exit(0)

if __name__ == "__main__":
    main()