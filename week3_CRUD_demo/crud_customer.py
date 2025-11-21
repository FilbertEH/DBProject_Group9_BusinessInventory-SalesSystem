from db_connect import get_connection

def add_customer(name, phone):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        INSERT INTO customer (customer_name, phone)
        VALUES (%s, %s)
        RETURNING customer_id;
    """

    cur.execute(query, (name, phone))
    new_id = cur.fetchone()[0]
    conn.commit()

    cur.close()
    conn.close()

    print(f"✅ New customer added with ID: {new_id}")
    return new_id


def get_customers():
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT customer_id, customer_name, phone, created_at
        FROM customer
        ORDER BY customer_id;
    """

    cur.execute(query)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows
