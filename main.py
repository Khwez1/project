import mysql.connector as mysql, sys, logging

logging.basicConfig(
  level='INFO'
)

mysql.connect(
  host="localhost",
  user="root",
  password="Oblivi0n",
  database="isp_subscription_system"
)

class OptionException(Exception):
  pass


def add_package_menu():
  print("Preparing a new package...\r\n")
  package_name = input("Please input package name:")
  description = input("Please input package description:")
  monthly_price = input("Please input package monthly price:")
  confirm = input(f"Are you sure you want to create this package Y/n?: package name{package_name}, desription{description}, {float(monthly_price, 2)}")
  if confirm == 'y':    
    """SQL logic for insert goes here:"""    
    print("Package succesfully created!")
  elif confirm == 'n':
    main()

def view_packages():
  """SQL logic to select * packages goes here"""
  pass

def view_customers():
  """SQL logic to select * packages goes here"""
  pass

def register_customers_menu():
  print("Welcome to the register customers menu\r\n")
  customer_name = input("Please input customer's name:")
  phone_number = input("Please input customer's phone number:")
  email_address = input("Please input customer's email:")
  confirm = input(f"Are you sure you want to register this user Y/n? Name:{customer_name}, Number:{phone_number}, Email:{email_address}")
  if(confirm == 'y'):
    """SQL logic for insert goes here"""
    print("Customer sucessfully created!")
  elif(confirm == 'n'):
    main()

def subscribe_customers_menu():
  print("Welcome to the subscribe customers menu\r\n")
  customer_id = input("Please input customer_ID:")
  package_id = input("Please input package_ID:")
  pass

def main():
  print("Welcome to Backspace Technologies Subscription System")

  print("Please choose an Option: ")
  print("1. Add Package")
  print("2. View Packages")
  print("3. Register Customer")
  print("4. View Customer")
  print("5. Subscribe Customer")
  print("6. Exit program")

  option = input()

  while(option):
    try:
      if(int(option) == 1):
        add_package_menu()
      elif(int(option) == 2):
        view_packages()
      elif(int(option) == 3):
        register_customers_menu()
      elif(int(option) == 4):
        view_customers()
      elif(int(option) == 5): 
        subscribe_customers_menu()
      elif(int(option) == 6):
        print("Exiting program... Goodbye!")
        sys.exit(0)
      else: 
        raise OptionException("Please select a valid option 1-6\r\n")
    except OptionException as e:
      logging.error(e)
      main()

main()

