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