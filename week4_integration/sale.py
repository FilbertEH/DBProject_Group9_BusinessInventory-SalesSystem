from db_connect import get_connection

def create_sale(operator_id, customer_id, items):
    """
    Executes a sales transaction.
    
    Args:
        operator_id (int): ID of the logged-in user.
        customer_id (int or None): ID of the customer (optional).
        items (list): List of dicts [{'product_id': 1, 'quantity': 2}, ...]

    Returns:
        (bool, str): (Success/Fail, Message)
    """

    conn = get_connection()
    if not conn:
        return False, "Database connection failed"

    cursor = None
    try:
        cursor = conn.cursor()
        
        # --- STEP 1: Create the Sale Record (Parent) ---
        print(f"Creating Sale for Operator {operator_id}, Customer {customer_id}...")
        
        query_sale = """
            INSERT INTO Sale (operator_id, customer_id, total_amount)
            VALUES (%s, %s, 0)
            RETURNING sale_id
        """
        cursor.execute(query_sale, (operator_id, customer_id))
        result = cursor.fetchone()
        if not result:
            raise Exception("Failed to create sale record")
        sale_id = result[0]
        
        total_sale_amount = 0.0
        
        # --- STEP 2: Process Each Item (Children) ---
        for item in items:
            p_id = int(item['product_id'])
            qty = int(item['quantity'])
            
            # A. Check Stock & Price
            cursor.execute("SELECT price, quantity_stock, product_name FROM Product WHERE product_id = %s", (p_id,))
            product = cursor.fetchone()
            
            if not product:
                raise Exception(f"Product ID {p_id} not found.")
            
            price, current_stock, product_name = product
            
            # B. Validate Inventory
            if current_stock < qty:
                raise Exception(f"Not enough stock for '{product_name}'. (Available: {current_stock}, Requested: {qty})")

            # C. Calculate Subtotal
            subtotal = float(price) * qty
            total_sale_amount += subtotal
            
            # D. Insert into SaleItem
            query_item = """
                INSERT INTO SaleItem (sale_id, product_id, quantity, unit_price, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query_item, (sale_id, p_id, qty, price, subtotal))
            
            # E. Decrease Stock
            cursor.execute("UPDATE Product SET quantity_stock = quantity_stock - %s WHERE product_id = %s", (qty, p_id))

        # --- STEP 3: Finalize Total Amount ---
        cursor.execute("UPDATE Sale SET total_amount = %s WHERE sale_id = %s", (total_sale_amount, sale_id))
        
        # --- COMMIT TRANSACTION ---
        conn.commit()
        print(f"Sale #{sale_id} committed successfully.")
        return True, f"Sale #{sale_id} completed! Total: ${total_sale_amount:.2f}"

    except Exception as e:
        # --- ROLLBACK TRANSACTION ---
        conn.rollback()
        print(f"Transaction Failed: {e}")
        return False, str(e)
        
    finally:
        if cursor:
            cursor.close()
        conn.close()

def get_sale_history():
    """Fetches list of recent sales for the history page."""
    conn = get_connection()
    if not conn: return []
    
    try:
        cursor = conn.cursor()
        # Join tables to show Names instead of IDs
        query = """
            SELECT s.sale_id, s.sale_date, o.operator_name, c.customer_name, s.total_amount
            FROM Sale s
            JOIN Operator o ON s.operator_id = o.operator_id
            LEFT JOIN Customer c ON s.customer_id = c.customer_id
            ORDER BY s.sale_date DESC
            LIMIT 50
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []
    finally:
        conn.close()

def get_sale_with_items(sale_id):
    """Fetch sale details with all items"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        query = """
            SELECT 
                si.sale_item_id,
                p.product_name,
                si.quantity,
                si.unit_price,
                si.subtotal
            FROM SaleItem si
            JOIN Product p ON si.product_id = p.product_id
            WHERE si.sale_id = %s
            ORDER BY si.sale_item_id
        """
        cursor.execute(query, (sale_id,))
        return cursor.fetchall()
    finally:
        conn.close()