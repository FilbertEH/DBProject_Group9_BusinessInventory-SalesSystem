import crud_product
import crud_customer
import crud_category
import sys

def print_header(text):
    print(f"\n=== {text} ===")

def start_app():
    while True:
        print("\n" + "="*35)
        print(" SMALL BUSINESS INVENTORY SYSTEM")
        print("="*35)
        print("1. [Product]  View All Products")
        print("2. [Product]  Add New Product")
        print("3. [Product]  Update Stock")
        print("4. [Product]  Delete Product")
        print("5. [Customer] View Customers")
        print("6. [Customer] Add Customer")
        print("7. [Category] View Categories")
        print("8. Exit")
        
        choice = input("\nSelect Option: ")

        # --- OPTION 1: VIEW PRODUCTS ---
        if choice == '1':
            print_header("PRODUCT LIST")
            products = crud_product.show_all_products()
            
            if not products:
                print("⚠️  No products found (or function not implemented).")
            else:
                # Table Header
                print(f"{'ID':<5} {'SKU':<12} {'Name':<20} {'Category':<15} {'Price':<10} {'Stock':<5}")
                print("-" * 75)
                # Table Rows
                for p in products:
                    # Assumes tuple: (id, sku, name, cat_name, price, stock)
                    # We use try/except here in case the tuple structure doesn't match exactly yet
                    try:
                        print(f"{p[0]:<5} {p[1]:<12} {p[2]:<20} {p[3]:<15} ${p[4]:<9} {p[5]:<5}")
                    except IndexError:
                        print(p) # Fallback to raw print if index fails

        # --- OPTION 2: ADD PRODUCT ---
        elif choice == '2':
            print_header("ADD PRODUCT")
            
            # Helper: Show categories nicely
            cats = crud_category.get_all_categories()
            print("Available Categories:")
            if cats:
                for c in cats:
                    print(f"  [{c[0]}] {c[1]}") # ID, Name
            else:
                print("  (No categories found)")
            
            print("-" * 20)
            
            try:
                cat_id = int(input("Category ID: "))
                name = input("Name: ")
                sku = input("SKU: ")
                price = float(input("Price: "))
                stock = int(input("Stock: "))
                
                crud_product.add_product(cat_id, name, sku, price, stock)
            except ValueError:
                print("❌ Error: Please enter valid numbers for ID, Price, and Stock.")

        # --- OPTION 3: UPDATE STOCK ---
        elif choice == '3':
            print_header("UPDATE STOCK")
            try:
                pid = int(input("Product ID: "))
                qty = int(input("New Quantity: "))
                crud_product.update_stock(pid, qty)
            except ValueError:
                print("❌ Error: Numbers only.")

        # --- OPTION 4: DELETE PRODUCT ---
        elif choice == '4':
            print_header("DELETE PRODUCT")
            try:
                pid = int(input("Product ID: "))
                confirm = input(f"Are you sure you want to delete ID {pid}? (y/n): ")
                if confirm.lower() == 'y':
                    crud_product.delete_product(pid)
                else:
                    print("Operation cancelled.")
            except ValueError:
                print("❌ Error: Numbers only.")

        # --- OPTION 5: VIEW CUSTOMERS ---
        elif choice == '5':
            print_header("CUSTOMER LIST")
            custs = crud_customer.get_customers()
            
            if not custs:
                print("⚠️  No customers found (or function not implemented).")
            else:
                print(f"{'ID':<5} {'Name':<20} {'Phone':<15}")
                print("-" * 45)
                for c in custs:
                    try:
                        print(f"{c[0]:<5} {c[1]:<20} {c[2]:<15}")
                    except IndexError:
                        print(c)

        # --- OPTION 6: ADD CUSTOMER ---
        elif choice == '6':
            print_header("ADD CUSTOMER")
            name = input("Name: ")
            phone = input("Phone: ")
            crud_customer.add_customer(name, phone)

        # --- OPTION 7: VIEW CATEGORIES ---
        elif choice == '7':
            print_header("CATEGORIES")
            cats = crud_category.get_all_categories()
            if not cats:
                print("No categories found.")
            else:
                print(f"{'ID':<5} {'Name'}")
                print("-" * 20)
                for c in cats:
                    print(f"{c[0]:<5} {c[1]}")

        # --- OPTION 8: EXIT ---
        elif choice == '8':
            print("Exiting... Goodbye!")
            sys.exit()
        
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    start_app()