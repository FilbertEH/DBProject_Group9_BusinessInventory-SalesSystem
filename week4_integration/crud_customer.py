# crud_customer.py
import psycopg2
from psycopg2.extras import RealDictCursor
from db_connect import get_connection
from datetime import datetime

# GET ALL CUSTOMERS
def get_all_customers():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute('SELECT * FROM customer ORDER BY customer_id ASC;')
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


# ADD CUSTOMER
def add_customer(name, phone):
    conn = get_connection()
    cur = conn.cursor()

    query = '''
        INSERT INTO customer (customer_name, phone, created_at)
        VALUES (%s, %s, %s)
    '''

    cur.execute(query, (name, phone, datetime.now()))
    conn.commit()

    cur.close()
    conn.close()

# GET SINGLE CUSTOMER
def get_customer(customer_id):
    """Get a single customer by ID"""
    conn = get_connection()
    if not conn:
        return None

    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = "SELECT * FROM customer WHERE customer_id = %s"
        cursor.execute(query, (customer_id,))
        result = cursor.fetchone()
        return result

    except Exception as e:
        print(f"Error fetching customer: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        conn.close()

# UPDATE CUSTOMER
def update_customer(customer_id, name, phone):
    """Update a customer's information"""
    conn = get_connection()
    if not conn:
        return False, "Connection failed"

    cursor = None
    try:
        cursor = conn.cursor()
        query = "UPDATE customer SET customer_name = %s, phone = %s WHERE customer_id = %s"
        cursor.execute(query, (name, phone, customer_id))
        conn.commit()

        if cursor.rowcount == 0:
            return False, "Customer not found"

        return True, None

    except Exception as e:
        conn.rollback()
        return False, f"Error updating customer: {e}"

    finally:
        if cursor:
            cursor.close()
        conn.close()

# DELETE CUSTOMER
def delete_customer(customer_id):
    """Delete a customer if not referenced by sales"""
    conn = get_connection()
    if not conn:
        return False, "Connection failed"

    cursor = None
    try:
        cursor = conn.cursor()

        # Check if customer is used by any sales
        check_query = "SELECT COUNT(*) FROM sale WHERE customer_id = %s"
        cursor.execute(check_query, (customer_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            return False, f"Cannot delete customer: {count} sale(s) associated with this customer"

        # Delete customer
        delete_query = "DELETE FROM customer WHERE customer_id = %s"
        cursor.execute(delete_query, (customer_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return False, "Customer not found"

        return True, None

    except Exception as e:
        conn.rollback()
        return False, f"Error deleting customer: {e}"

    finally:
        if cursor:
            cursor.close()
        conn.close()
