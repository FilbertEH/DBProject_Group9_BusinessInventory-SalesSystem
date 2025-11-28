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
