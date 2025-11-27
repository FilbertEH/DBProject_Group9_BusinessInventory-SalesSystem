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
