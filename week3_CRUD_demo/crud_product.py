from db_connect import get_connection

def show_all_products():
    """
    Return list of products joined with Category Name.
    Columns: id, name, sku, price, stock, category_name
    """
    conn = get_connection()
    if not conn:
        print("Connection failed.")
        return []

    cursor = None
    try:
        cursor = conn.cursor()
        query = """
            SELECT
                p.product_id,
                p.product_name,
                p.sku,
                p.price,
                p.quantity_stock,
                c.category_name
            FROM product p
            JOIN category c ON p.category_id = c.category_id
            ORDER BY p.product_id;
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        # Pretty print (same vibe as your teammates)
        print("ID | Name | SKU | Price | Stock | Category")
        for r in rows:
            print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]}")

        return rows

    except Exception as e:
        print(f"Error fetching products: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        conn.close()


def add_product(cat_id, name, sku, price, stock):
    """
    INSERT a new product. Returns new product_id or None on error.
    """
    conn = get_connection()
    if not conn:
        print("Connection failed.")
        return None

    cursor = None
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO product
                (category_id, product_name, sku, price, quantity_stock, is_active)
            VALUES (%s, %s, %s, %s, %s, TRUE)
            RETURNING product_id;
        """
        cursor.execute(query, (cat_id, name, sku, price, stock))
        new_id = cursor.fetchone()[0]
        conn.commit()

        print(f"✅ New product '{name}' added with ID: {new_id}")
        return new_id

    except Exception as e:
        conn.rollback()
        print(f"Error adding product: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        conn.close()


def update_stock(product_id, new_stock):
    """
    UPDATE product stock. Returns True on success, False on failure.
    """
    conn = get_connection()
    if not conn:
        print("Connection failed.")
        return False

    cursor = None
    try:
        cursor = conn.cursor()
        query = """
            UPDATE product
            SET quantity_stock = %s
            WHERE product_id = %s
            RETURNING quantity_stock;
        """
        cursor.execute(query, (new_stock, product_id))
        row = cursor.fetchone()
        conn.commit()

        if not row:
            print("⚠️ No product found with that ID.")
            return False

        print(f"✅ Stock for product {product_id} set to {row[0]}")
        return True

    except Exception as e:
        conn.rollback()
        print(f"Error updating stock: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        conn.close()


def delete_product(product_id):
    """
    DELETE a product. Returns True on success, False otherwise.
    (If product is referenced by sales, DB will block and we print the error.)
    """
    conn = get_connection()
    if not conn:
        print("Connection failed.")
        return False

    cursor = None
    try:
        cursor = conn.cursor()
        query = "DELETE FROM product WHERE product_id = %s RETURNING product_id;"
        cursor.execute(query, (product_id,))
        row = cursor.fetchone()
        conn.commit()

        if not row:
            print("⚠️ No product found with that ID.")
            return False

        print(f"🗑️ Deleted product {product_id}")
        return True

    except Exception as e:
        conn.rollback()
        print(f"Error deleting product: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        conn.close()


# Optional quick test (CLI)
if __name__ == "__main__":
    print("\nExisting products:")
    show_all_products()

    print("\n--- Add New Product (optional) ---")
    try:
        name = input("Name (leave blank to skip): ").strip()
    except EOFError:
        name = ""

    if name:
        sku = input("SKU: ").strip()
        cat = int(input("Category ID: ").strip() or "1")
        price = float(input("Price: ").strip() or "0")
        stock = int(input("Stock: ").strip() or "0")
        add_product(cat, name, sku, price, stock)
        print("\nUpdated products:")
        show_all_products()
