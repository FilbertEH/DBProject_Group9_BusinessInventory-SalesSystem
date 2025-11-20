## Keita

#### Tasks:

- [x] Implement `create_category(name)`
- [x] Implement `get_all_categories()`

#### SQL Query

```sql
# get_all_categories()
SELECT category_id, category_name FROM category ORDER BY category_id ASC;

# create_category(name)
INSERT INTO category (category_name) VALUES (...);
```

#### Result:

- **Terminal:**

  ![crud_category_terminal](images/crud_category_terminal.png)

- **Database (Neon):**

  ![crud_category_db](images/crud_category_db.png)

---
