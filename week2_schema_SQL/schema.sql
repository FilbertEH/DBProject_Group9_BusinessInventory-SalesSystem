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
    
    CONSTRAINT fk_product_category 
        FOREIGN KEY (category_id) REFERENCES Category(category_id)
        ON DELETE RESTRICT
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
    
    CONSTRAINT fk_sale_customer 
        FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
        ON DELETE SET NULL,
    
    CONSTRAINT fk_sale_operator 
        FOREIGN KEY (operator_id) REFERENCES Operator(operator_id)
        ON DELETE RESTRICT
);

CREATE TABLE SaleItem (
    sale_item_id SERIAL PRIMARY KEY,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    subtotal DECIMAL(10, 2) NOT NULL CHECK (subtotal >= 0),
    
    CONSTRAINT fk_saleitem_sale 
        FOREIGN KEY (sale_id) REFERENCES Sale(sale_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_saleitem_product 
        FOREIGN KEY (product_id) REFERENCES Product(product_id)
        ON DELETE RESTRICT
);

--- Indexes for Performance

-- Product indexes
CREATE INDEX idx_product_category ON Product(category_id);

-- Sale indexes
CREATE INDEX idx_sale_customer ON Sale(customer_id);
CREATE INDEX idx_sale_operator ON Sale(operator_id);
CREATE INDEX idx_sale_date ON Sale(sale_date);

-- SaleItem indexes
CREATE INDEX idx_saleitem_sale ON SaleItem(sale_id);
CREATE INDEX idx_saleitem_product ON SaleItem(product_id);