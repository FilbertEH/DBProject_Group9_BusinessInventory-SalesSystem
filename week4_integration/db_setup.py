import psycopg2
import sys
import bcrypt 
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Get the URL from the environment
DB_URL = os.getenv("DB_URL")

if not DB_URL:
    print("❌ Error: DB_URL not found in .env file.")
    sys.exit(1)

def setup_database():
    print("🔄 Connecting to Neon DB to reset tables...")
    
    try:
        # Connect directly using the URL
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
        cursor = conn.cursor()

        # --- 1. CLEANUP (Drop existing tables) ---
        print("🗑️  Dropping old tables (if any)...")
        cursor.execute("""
            DROP TABLE IF EXISTS SaleItem CASCADE;
            DROP TABLE IF EXISTS Sale CASCADE;
            DROP TABLE IF EXISTS Product CASCADE;
            DROP TABLE IF EXISTS Category CASCADE;
            DROP TABLE IF EXISTS Customer CASCADE;
            DROP TABLE IF EXISTS Operator CASCADE;
        """)

        # --- 2. CREATE TABLES ---
        print("🏗️  Creating new tables...")
        cursor.execute("""
            --- Category Table
            CREATE TABLE Category (
                category_id SERIAL PRIMARY KEY,
                category_name VARCHAR(100) NOT NULL
            );

            --- Product Table
            CREATE TABLE Product (
                product_id SERIAL PRIMARY KEY,
                category_id INTEGER NOT NULL,
                product_name VARCHAR(200) NOT NULL,
                sku VARCHAR(50) NOT NULL UNIQUE,
                price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
                quantity_stock INTEGER NOT NULL DEFAULT 0 CHECK (quantity_stock >= 0),
                low_stock_threshold INTEGER NOT NULL DEFAULT 10 CHECK (low_stock_threshold >= 0),
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES Category(category_id) ON DELETE RESTRICT
            );

            --- Customer Table
            CREATE TABLE Customer (
                customer_id SERIAL PRIMARY KEY,
                customer_name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            --- Operator Table
            CREATE TABLE Operator (
                operator_id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                operator_name VARCHAR(100) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'cashier',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            --- Sale Table
            CREATE TABLE Sale (
                sale_id SERIAL PRIMARY KEY,
                customer_id INTEGER NULL,
                operator_id INTEGER NOT NULL,
                sale_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
                CONSTRAINT fk_sale_customer FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE SET NULL,
                CONSTRAINT fk_sale_operator FOREIGN KEY (operator_id) REFERENCES Operator(operator_id) ON DELETE RESTRICT
            );

            CREATE TABLE SaleItem (
                sale_item_id SERIAL PRIMARY KEY,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
                subtotal DECIMAL(10, 2) NOT NULL CHECK (subtotal >= 0),
                CONSTRAINT fk_saleitem_sale FOREIGN KEY (sale_id) REFERENCES Sale(sale_id) ON DELETE CASCADE,
                CONSTRAINT fk_saleitem_product FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE RESTRICT
            );
            
            -- Create Indexes
            CREATE INDEX idx_product_category ON Product(category_id);
            CREATE INDEX idx_sale_customer ON Sale(customer_id);
            CREATE INDEX idx_sale_operator ON Sale(operator_id);
            CREATE INDEX idx_sale_date ON Sale(sale_date);
            CREATE INDEX idx_saleitem_sale ON SaleItem(sale_id);
            CREATE INDEX idx_saleitem_product ON SaleItem(product_id);
        """)

        # --- 3. INSERT DUMMY DATA ---
        print("🌱 Inserting dummy data...")
        
        # Generate hash for "admin123"
        password_bytes = "admin123".encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

        sql_insert_data = """
        -- 1. Insert Categories
        INSERT INTO Category (category_name) VALUES 
        ('Electronics'), ('Stationery'), ('Beverages');

        -- 2. Insert Products
        INSERT INTO Product (category_id, product_name, sku, price, quantity_stock) VALUES 
        (1, 'Wireless Mouse', 'TECH-001', 15.50, 50),
        (1, 'USB Keyboard', 'TECH-002', 25.00, 30),
        (2, 'Notebook A4', 'STAT-001', 2.50, 100),
        (3, 'Mineral Water', 'DRNK-001', 1.00, 100);

        -- 3. Insert Operators
        INSERT INTO Operator (username, password_hash, operator_name, role) VALUES 
        ('admin', %s, 'System Admin', 'admin'),
        ('cashier', %s, 'John Cashier', 'cashier');

        -- 4. Insert Customers
        INSERT INTO Customer (customer_name, phone) VALUES 
        ('Alice Wonderland', '08123456789'),
        ('Bob Builder', '08987654321');

        -- 5. Insert Sales (Transactions)
        -- Sale 1: Admin sold to Alice (Total: $31.00)
        INSERT INTO Sale (customer_id, operator_id, total_amount) VALUES 
        (1, 1, 31.00); 

        -- Sale Items for Sale 1
        INSERT INTO SaleItem (sale_id, product_id, quantity, unit_price, subtotal) VALUES 
        (1, 1, 2, 15.50, 31.00);

        -- Sale 2: Cashier sold to Bob (Total: $7.50)
        INSERT INTO Sale (customer_id, operator_id, total_amount) VALUES 
        (2, 2, 7.50);

        -- Sale Items for Sale 2
        INSERT INTO SaleItem (sale_id, product_id, quantity, unit_price, subtotal) VALUES 
        (2, 3, 3, 2.50, 7.50);
        """
        
        cursor.execute(sql_insert_data, (hashed_pw, hashed_pw))

        print("✅ Database setup complete! Tables created and data inserted.")
        print(f"🔑 Default User: 'admin' | Password: 'admin123'")
        
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    setup_database()