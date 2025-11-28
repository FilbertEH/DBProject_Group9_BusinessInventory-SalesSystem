from db_connect import get_connection

def show_all_products():
    """
    Returns rows in the exact order main.py expects:
      (product_id, sku, product_name, category_name, price, quantity_stock)
    """
    conn = get_connection()
    if not conn:
        print("Connection failed.")
        return []

    cur = None
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                p.product_id,
                p.sku,
                p.product_name,
                c.category_name,
                p.price,
                p.quantity_stock
            FROM product p
            JOIN category c ON p.category_id = c.category_id
            ORDER BY p.product_id;
        """)
        rows = cur.fetchall()
        return rows
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []
    finally:
        if cur: cur.close()
        conn.close()


def add_product(category_id, name, sku, price, stock):
    """
    INSERT a new product. Returns new product_id or None on error.
    """
    conn = get_connection()
    if not conn:
        print("Connection failed.")
        return None

    cur = None
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO product
                (category_id, product_name, sku, price, quantity_stock, is_active)
            VALUES (%s, %s, %s, %s, %s, TRUE)
            RETURNING product_id;
        """, (category_id, name, sku, price, stock))
        new_id = cur.fetchone()[0]
        conn.commit()
        print(f"New product added with ID: {new_id}")
        return new_id
    except Exception as e:
        conn.rollback()
        print(f"Error adding product: {e}")  # e.g., duplicate SKU, bad category_id
        return None
    finally:
        if cur: cur.close()
        conn.close()


def update_stock(product_id, new_stock):
    """
    UPDATE product stock. Returns True on success, False on failure.
    """
    conn = get_connection()
    if not conn:
        print("Connection failed.")
        return False

    cur = None
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE product
            SET quantity_stock = %s
            WHERE product_id = %s
            RETURNING product_id;
        """, (new_stock, product_id))
        row = cur.fetchone()
        conn.commit()
        if not row:
            print("No product found with that ID.")
            return False
        print("Stock updated.")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error updating stock: {e}")
        return False
    finally:
        if cur: cur.close()
        conn.close()


def delete_product(product_id):
    """
    DELETE a product. Returns True on success, False otherwise.
    (Will fail if referenced by saleitem; DB enforces it.)
    """
    conn = get_connection()
    if not conn:
        print("Connection failed.")
        return False

    cur = None
    try:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM product WHERE product_id = %s RETURNING product_id;",
            (product_id,)
        )
        row = cur.fetchone()
        conn.commit()
        if not row:
            print("No product found with that ID.")
            return False
        print("Product deleted.")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error deleting product: {e}")  # FK errors show here
        return False
    finally:
        if cur: cur.close()
        conn.close()
