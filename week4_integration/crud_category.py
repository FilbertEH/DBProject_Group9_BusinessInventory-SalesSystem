from db_connect import get_connection

def create_category(name):
    conn = get_connection()
    if not conn:
        print("Connection failed.")
        return

    cursor = None
    try:
        cursor = conn.cursor()
        query = "INSERT INTO category (category_name) VALUES (%s)"

        cursor.execute(query, (name,))
        conn.commit()

        print(f"category '{name}' added successfully.")

    except Exception as e:
        print(f"Error adding category: {e}")
        conn.rollback()

    finally:
        if cursor:
            cursor.close()
        conn.close()

def get_all_categories():
    conn = get_connection()
    if not conn:
        return []

    cursor = None
    try:
        cursor = conn.cursor()
        query = "SELECT category_id, category_name FROM category ORDER BY category_id ASC"

        cursor.execute(query)
        results = cursor.fetchall()

        return results

    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        conn.close()

def get_category(category_id):
    """Get a single category by ID"""
    conn = get_connection()
    if not conn:
        return None

    cursor = None
    try:
        cursor = conn.cursor()
        query = "SELECT category_id, category_name FROM category WHERE category_id = %s"
        cursor.execute(query, (category_id,))
        result = cursor.fetchone()
        return result

    except Exception as e:
        print(f"Error fetching category: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        conn.close()

def update_category(category_id, name):
    """Update a category name"""
    conn = get_connection()
    if not conn:
        return False, "Connection failed"

    cursor = None
    try:
        cursor = conn.cursor()
        query = "UPDATE category SET category_name = %s WHERE category_id = %s"
        cursor.execute(query, (name, category_id))
        conn.commit()

        if cursor.rowcount == 0:
            return False, "Category not found"

        return True, None

    except Exception as e:
        conn.rollback()
        return False, f"Error updating category: {e}"

    finally:
        if cursor:
            cursor.close()
        conn.close()

def delete_category(category_id):
    """Delete a category if not referenced by products"""
    conn = get_connection()
    if not conn:
        return False, "Connection failed"

    cursor = None
    try:
        cursor = conn.cursor()

        # Check if category is used by any products
        check_query = "SELECT COUNT(*) FROM product WHERE category_id = %s"
        cursor.execute(check_query, (category_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            return False, f"Cannot delete category: {count} product(s) still using this category"

        # Delete category
        delete_query = "DELETE FROM category WHERE category_id = %s"
        cursor.execute(delete_query, (category_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return False, "Category not found"

        return True, None

    except Exception as e:
        conn.rollback()
        return False, f"Error deleting category: {e}"

    finally:
        if cursor:
            cursor.close()
        conn.close()


# Test
if __name__ == "__main__":    
    # 1. Test Reading
    print("Existing Categories:")
    cats = get_all_categories()
    for c in cats:
        print(c)

    # 2. Test Creating
    print("\n--- Add New Category ---")
    new_cat = input("Enter new category name: ")
    
    if new_cat.strip():
        create_category(new_cat)
        
        print("\nUpdated Category List:")
        updated_cats = get_all_categories()
        for c in updated_cats:
            print(c)
    else:
        print("Skipped creation.")