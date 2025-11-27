from db_connect import get_connection

def get_dashboard_stats():
    conn = get_connection()
    if not conn: return {}

    stats = {
        "revenue": 0.0,
        "low_stock": 0,
        "total_items": 0,
        "recent_sales": [],
        'low_stock_items': []
    }

    try:
        cursor = conn.cursor()

        # 1. Total Revenue (The Money)
        cursor.execute("SELECT SUM(total_amount) FROM Sale")
        res_rev = cursor.fetchone()
        stats["revenue"] = float(res_rev[0]) if res_rev and res_rev[0] else 0.0

        # 2. Low Stock Alerts (The Warning)
        cursor.execute("SELECT COUNT(*) FROM Product WHERE quantity_stock <= low_stock_threshold")
        res_low_stock = cursor.fetchone()
        stats["low_stock"] = res_low_stock[0] if res_low_stock else 0

        # 3. Total Products (The Scope)
        cursor.execute("SELECT COUNT(*) FROM Product")
        res_total_items = cursor.fetchone()
        stats["total_items"] = res_total_items[0] if res_total_items else 0

        # 4. Recent 5 Sales (The Activity)
        query_recent = """
            SELECT s.sale_id, s.sale_date, o.operator_name, s.total_amount 
            FROM Sale s
            JOIN Operator o ON s.operator_id = o.operator_id
            ORDER BY s.sale_date DESC LIMIT 5
        """
        cursor.execute(query_recent)
        stats["recent_sales"] = cursor.fetchall()

        # Low Stock Items (NEW)
        cursor.execute("""
            SELECT product_name, quantity_stock, low_stock_threshold
            FROM Product 
            WHERE quantity_stock <= low_stock_threshold
            ORDER BY quantity_stock ASC
            LIMIT 10
        """)

        stats["low_stock_items"] = cursor.fetchall()

    except Exception as e:
        print(f"Stats Error: {e}")
    finally:
        conn.close()
    
    return stats