from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
from stats import get_dashboard_stats
from sale import create_sale, get_sale_history, get_sale_with_items
from crud_customer import get_all_customers, add_customer
from decimal import Decimal, InvalidOperation
from crud_product import (
    list_products,
    list_categories,
    create_product,
    delete_product,
    get_all_products, 
)

load_dotenv()

app = Flask(__name__)
app.secret_key = "secret_key_for_session_management" # Change this to random string

@app.route('/')
def dashboard():
    stats = get_dashboard_stats()
    return render_template('index.html', stats=stats)

# --- SALE MANAGEMENT (Your Implementation) ---

@app.route('/sales')
def sales_history():
    """Display list of past sales transactions"""
    history = get_sale_history()
    
    # Fetch items for each sale
    sales_with_items = []
    for sale in history:
        sale_id = sale[0]
        items = get_sale_with_items(sale_id)
        sales_with_items.append({
            'id': sale[0],
            'date': sale[1],
            'operator': sale[2],
            'customer': sale[3],
            'total': sale[4],
            'items': items  # ← 追加
        })
    
    return render_template('sales_history.html', sales=sales_with_items)

@app.route('/sales/new')
def new_sale_form():
    """Show the POS form for creating a new sale (uses live products)."""
    products = get_all_products()  # [(id, name, stock, price)]
    return render_template('new_sale.html', products=products)

@app.route('/sales/create', methods=['POST'])
def create_sale_action():
    """Process the sale form submission"""
    try:
        operator_id = 1  # TODO: Get from session after login system is built
        customer_id = request.form.get('customer_id') or None
        
        items = []
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        
        for pid, qty in zip(product_ids, quantities):
            if pid and qty:
                items.append({
                    'product_id': int(pid),
                    'quantity': int(qty)
                })
        
        if not items:
            flash('Please add at least one product to the sale', 'error')
            return redirect(url_for('new_sale_form'))
        
        success, message = create_sale(operator_id, customer_id, items)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('sales_history'))
        else:
            flash(f'Sale failed: {message}', 'error')
            return redirect(url_for('new_sale_form'))
            
    except ValueError as e:
        flash(f'Invalid input: {e}', 'error')
        return redirect(url_for('new_sale_form'))
    except Exception as e:
        flash(f'Unexpected error: {e}', 'error')
        return redirect(url_for('new_sale_form'))

# --- PLACEHOLDERS FOR TEAMMATES ---
# Filbert will work here
@app.route('/products')
def product_list():
    rows = list_products()  # [(id, name, sku, price, qty, category_name)]
    return render_template('products.html', rows=rows)

@app.route('/product/add', methods=['GET', 'POST'])
def product_add():
    categories = list_categories()  # [(id, name)]
    if request.method == 'POST':
        name = (request.form.get('product_name') or '').strip()
        sku  = (request.form.get('sku') or '').strip()
        cat  = request.form.get('category_id')
        qty  = request.form.get('quantity_stock', '0')
        price = request.form.get('price', '0')

        if not name or not sku or not cat:
            flash('Name, SKU, and Category are required.', 'error')
            return render_template('add_product.html', categories=categories)

        try:
            qty = int(qty); price = Decimal(price)
            if qty < 0 or price < 0:
                raise ValueError
        except (ValueError, InvalidOperation):
            flash('Quantity and price must be valid non-negative numbers.', 'error')
            return render_template('add_product.html', categories=categories)

        new_id, err = create_product(name, sku, price, qty, int(cat))
        if err:
            flash(err, 'error')
            return render_template('add_product.html', categories=categories)

        flash('Product created.', 'success')
        return redirect(url_for('product_list'))

    return render_template('add_product.html', categories=categories)

@app.route('/product/delete/<int:id>', methods=['POST'])
def product_delete(id):
    ok, msg = delete_product(id)
    flash('Product deleted.' if ok else (msg or 'Delete failed.'), 'success' if ok else 'error')
    return redirect(url_for('product_list'))

# Arya will work here
@app.route('/customers')
def customer_list():
    customers = get_all_customers()
    return render_template('customers.html', customers=customers)

@app.route('/customer/add', methods=['GET', 'POST'])
def add_customer_page():
    if request.method == 'POST':
        name = request.form['customer_name']
        phone = request.form['phone']
        
        add_customer(name, phone)
        return redirect(url_for('customer_list'))

    return render_template('add_customer.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

