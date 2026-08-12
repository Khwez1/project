# PROJECT SECTION: Customer Management
    # Registers a Customer and views customers from
    # the BRD, plus the validation piece BR5/FR5 depends on when a
    # customer subscribes to a package.


# registering, viewing and checking if customers exists
class Customer:
    def __init__(self, db):
        self.db = db  # Store the shared Database object so every method in this class can use it to run queries.


# -------------------------------------------------------
# BR3: Register Customer

    def register_customer(self, name, phone, email):
        if not name.strip():                                                        # Basic validation: reject the request if the name is blank - required field.
            print("Customer name cannot be blank.")
            return 

        # SQL query to insert a new customer row.
        query = "INSERT INTO customers (name, phone, email) VALUES (%s, %s, %s)"    # %s placeholders are used instead of putting the values directly into the string


        # Run the query, passing the actual values as a tuple.
        # The cursor matches each %s to the corresponding value in order.
        self.db.cursor.execute(query, (name, phone, email))
        self.db.commit()                                                            # Commit the transaction so the insert is actually saved to the database
        print(f"Customer '{name}' registered successfully.")                        # FR3 output requirement: confirmation message that customer was added.


# -------------------------------------------------------
# BR4: View Customers
        
    def view_customers(self):
        self.db.cursor.execute("SELECT * FROM customers")                           # Select every column for every row in the customers table.

        rows = self.db.cursor.fetchall()                                            # Pull all the matching rows back as a list of tuples.

        if not rows:                                                                # If the table is empty, alert and exit early.
            print("No customers found.")
            return

        # Otherwise, loop through each row and print it in a readable format
        for row in rows:
            print(f"ID: {row[0]} | Name: {row[1]} | Phone: {row[2]} | Email: {row[3]}")

# -------------------------------------------------------
# # Supports BR5: Subscribe Customer to Package 
        # verify that the customer exists before a subscription can be created 
    
    def customer_exists(self, customer_id):
        self.db.cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))    # Look for a customer row matching the given ID.
        return self.db.cursor.fetchone() is not None                                                # fetchone() returns the first matching row, or None if there isn't one