# PROJECT SECTION: Chunk 4 — Subscriptions & Pricing
    # Covers BR5 (Subscribe Customer to Package) and FR5
    #   - VAT must always be calculated at 15% of the subtotal
    #   - Total price must always equal subtotal + VAT
    #   - A customer must exist before a subscription can be created
    #   - A package must exist before it can be subscribed to

#-----------------------------------------------------------
class Subscription:
    def __init__(self, db, customer, package):
        # Store references to the shared Database object, and to the Customer and Package objects this class depends on for validation and price lookup.
        self.db = db
        self.customer = customer
        self.package = package


    def subscribe_customer(self, customer_id, package_id):
# -------------------------------------------------------
# BR5: "verify that the customer exists"
        if not self.customer.customer_exists(customer_id):
            print("Customer ID not found.")
            return  # Stop, don't create a subscription for a customer that doesn't exist

# -------------------------------------------------------
# BR5: "verify that the package exists" + "retrieve the package price"
        price = self.package.get_package_price(package_id)              # get_package_price() returns None if the ID doesn't exist, which doubles as our existence check
        if price is None:
            print("Package ID not found.")
            return                                                      # Stop here — don't create a subscription for a package that doesn't exist.

# -------------------------------------------------------
# BR5: calculate subtotal, VAT, total
        subtotal = price
        vat = round(subtotal * 0.15, 2)
        total = round(subtotal + vat, 2)

# -------------------------------------------------------
# BR6: Store Data — save the subscription record to MySQL.
        query = """INSERT INTO subscriptions (customer_id, package_id, subtotal, vat, total)
                   VALUES (%s, %s, %s, %s, %s)"""
        self.db.cursor.execute(query, (customer_id, package_id, subtotal, vat, total))
        self.db.commit()                                                # Save the insert

# -------------------------------------------------------
# FR5 output requirement: success message with pricing
        print("\nSubscription Created Successfully")
        print(f"Subtotal: R{subtotal:.2f}")
        print(f"VAT (15%): R{vat:.2f}")
        print(f"Total: R{total:.2f}")