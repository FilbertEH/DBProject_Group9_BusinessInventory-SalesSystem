# Week 3: Database Implementation & CRUD

## 🚀 Setup Instructions (Read First!)

1.  **Navigate to the Folder**
    Open your terminal in the project root and enter:

    ```bash
    cd week3_CRUD_demo
    ```

2.  **Install Dependencies**

    ```bash
    pip install psycopg2-binary bcrypt python-dotenv
    ```

3.  **Database Connection (IMPORTANT)**

    - Create a new file named `.env` inside the `week3_CRUD_demo/` folder.
    - **Do not upload this file to GitHub.**
    - Paste the content below into the file, replacing the value with the Neon DB URL from our group chat:

      ```ini
      DB_URL=postgres://neondb_owner:.......@.......neon.tech/neondb?sslmode=require
      ```

      _(Note: Do not use quotation marks "" around the URL inside the .env file)_

4.  **Check DB Connection**
    Before running the main app, verify your configuration works:

    ```bash
    python db_connect.py
    ```

    **Success Message:**

    > ✅ Successfully connected to Neon DB!

5.  **Run the App**
    ```bash
    python main.py
    ```

---

## 👥 Team Assignments & Git Workflow

**⚠️ Git Rule:** Please do not push directly to `main`.

1.  Create your branch: `git checkout -b feature/your-name-crud`
2.  Code your task.
3.  Push and tell the group.

### Member 1 - Keita

- **File:** `crud_category.py`
- **Tasks:**
  - Implement `create_category(name)`
  - Implement `get_all_categories()`

### Member 2 - Filbert

- **File:** `crud_product.py`
- **Tasks:**
  - Implement `show_all_products()`: Return list of products joined with Category Name.
  - Implement `add_product()`: INSERT query.
  - Implement `update_stock()`: UPDATE query.
  - Implement `delete_product()`: DELETE query.

### Member 3 - Arya

- **File:** `crud_customer.py`
- **Tasks:**
  - Implement `add_customer()`: INSERT query.
  - Implement `get_customers()`: SELECT query.

---

## 📊 Database Schema (Reference)

**1. Category Table**

- Columns: `category_id` (PK), `category_name`
- ![category table](images/category.png)

**2. Customer Table**

- Columns: `customer_id` (PK), `customer_name`, `phone`, `created_at`
- ![customer table](images/customer.png.png)

**3. Product Table**

- Columns: `product_id` (PK), `category_id` (FK), `product_name`, `sku`, `price`, `quantity_stock`
- ![product table](images/product.png)

**4. Operator Table** (For Login/Auth)

- Columns: `operator_id`, `username`, `password_hash`, `role`
- ![operator table](images/operator.png.png)

---

## ⚠️ Important Notes

- **Do not edit `main.py`** unless necessary. It is already set up to call your functions.
- **Do not run `setup_db.py`** (Keita has already initialized the Neon database).
- **Troubleshooting:** If you get a "Module not found" error, make sure you ran the `pip install` command in Step 2.
