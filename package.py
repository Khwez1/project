# PROJECT SECTION: Package Management
    # Registers a Package and views packages from
    # the BRD, plus the validation/price-lookup piece BR5/FR5 depends on
    # when a customer subscribes to a package.


# registering, viewing, checking if packages exist, and looking up price
class Package:
    def __init__(self, db):
        self.db = db  # Store the shared Database object so every method in this class can use it to run queries.


# -------------------------------------------------------
# BR1: Add Package

    def register_package(self, name, description, monthly_price):
        if not name.strip():                                                        # Basic validation: reject the request if the name is blank - required field.
            print("Package name cannot be blank.")
            return

        # SQL query to insert a new package row.
        query = "INSERT INTO packages (name, description, price) VALUES (%s, %s, %s)"  # %s placeholders are used instead of putting the values directly into the string

        # Run the query, passing the actual values as a tuple.
        # The cursor matches each %s to the corresponding value in order.
        self.db.cursor.execute(query, (name, description, monthly_price))
        self.db.commit()                                                            # Commit the transaction so the insert is actually saved to the database
        print(f"Package '{name}' registered successfully.")                         # FR1 output requirement: confirmation message that package was added.


# -------------------------------------------------------
# BR2: View Packages

    def view_packages(self):
        self.db.cursor.execute("SELECT * FROM packages")                           # Select every column for every row in the packages table.

        rows = self.db.cursor.fetchall()                                            # Pull all the matching rows back as a list of tuples.

        if not rows:                                                                # If the table is empty, alert and exit early.
            print("No packages found.")
            return

        # Otherwise, loop through each row and print it in a readable format
        for row in rows:
            print(f"ID: {row[0]} | Name: {row[1]} | Description: {row[2]} | Monthly Price: R{row[3]:.2f}")

# -------------------------------------------------------
# Supports BR5: Subscribe Customer to Package
        # verify that the package exists before a subscription can be created

    def package_exists(self, package_id):
        self.db.cursor.execute("SELECT 1 FROM packages WHERE package_id = %s", (package_id,))  # Look for a package row matching the given ID.
        return self.db.cursor.fetchone() is not None                                            # fetchone() returns the first matching row, or None if there isn't one

# -------------------------------------------------------
# Supports BR5: retrieve the package price so Subscription can calculate subtotal/VAT/total

    def get_package_price(self, package_id):
        self.db.cursor.execute("SELECT price FROM packages WHERE package_id = %s", (package_id,))
        row = self.db.cursor.fetchone()
        if row is None: # None doubles as our "package doesn't exist" signal for Subscription
            return None 
        return float(row[0]) # multiplied with a plain float (subscription.py does subtotal * 0.15), MySQL DECIMAL columns come back as decimal.Decimal, which can't be so convert to float here at the boundary.