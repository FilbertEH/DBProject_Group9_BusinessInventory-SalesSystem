from db_connect import get_connection
from decimal import Decimal
from psycopg2 import errors

def get_all_products():
    """
    Returns products for POS dropdown in shape:
    [(product_id, product_name, quantity_stock, price)]
    Only active products, sorted by name.
    """
    sql = """
        SELECT product_id, product_name, quantity_stock, price
        FROM product
        WHERE is_active = TRUE
        ORDER BY product_name;
    """
    conn = get_connection()
    with conn, conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    conn.close()
    return rows

def list_products():
    sql = """
      SELECT p.product_id, p.product_name, p.sku, p.price, p.quantity_stock,
             c.category_name
      FROM product p
      JOIN category c ON c.category_id = p.category_id
      ORDER BY p.product_name;
    """
    conn = get_connection()
    with conn, conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    conn.close()
    return rows  # [(id,name,sku,price,qty,category_name)]

def list_categories():
    sql = "SELECT category_id, category_name FROM category ORDER BY category_name;"
    conn = get_connection()
    with conn, conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    conn.close()
    return rows  # [(id, name)]

def create_product(name: str, sku: str, price: Decimal, qty: int, category_id: int):
    sql = """
      INSERT INTO product (product_name, sku, price, quantity_stock, category_id)
      VALUES (%s, %s, %s, %s, %s)
      RETURNING product_id;
    """
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql, (name.strip(), sku.strip(), price, qty, category_id))
            new_id = cur.fetchone()[0]
        return new_id, None
    except errors.UniqueViolation:
        conn.rollback()
        return None, "SKU already exists."
    except errors.ForeignKeyViolation:
        conn.rollback()
        return None, "Invalid category."
    finally:
        conn.close()

def get_product(pid: int):
    sql = """
      SELECT product_id, product_name, sku, price, quantity_stock, category_id
      FROM product WHERE product_id = %s;
    """
    conn = get_connection()
    with conn, conn.cursor() as cur:
        cur.execute(sql, (pid,))
        row = cur.fetchone()
    conn.close()
    return row

def update_product(pid: int, name: str, sku: str, price: Decimal, qty: int, category_id: int):
    sql = """
      UPDATE product
         SET product_name=%s, sku=%s, price=%s, quantity_stock=%s, category_id=%s
       WHERE product_id=%s;
    """
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql, (name.strip(), sku.strip(), price, qty, category_id, pid))
            if cur.rowcount == 0:
                conn.rollback()
                return False, "Product not found."
        return True, None
    except errors.UniqueViolation:
        conn.rollback()
        return False, "SKU already exists."
    except errors.ForeignKeyViolation:
        return False, "Invalid category."
    finally:
        conn.close()

def delete_product(pid: int):
    sql = "DELETE FROM product WHERE product_id = %s;"
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql, (pid,))
            if cur.rowcount == 0:
                conn.rollback()
                return False, "Product not found."
        return True, None
    except errors.ForeignKeyViolation:
        conn.rollback()
        return False, "Cannot delete: product is referenced by sales."
    finally:
        conn.close()
