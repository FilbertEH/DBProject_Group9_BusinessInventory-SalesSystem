from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
from stats import get_dashboard_stats
from sale import create_sale, get_sale_history, get_sale_with_items
from crud_customer import get_all_customers, add_customer


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
    """Show the POS form for creating a new sale"""
    
    # TEMPORARY: Mock data matching db_setup.py
    # TODO: Replace with get_all_products() when Filbert implements crud_product.py
    products = [
        (1, 'Wireless Mouse', 50, 15.50),
        (2, 'USB Keyboard', 30, 25.00),
        (3, 'Notebook A4', 100, 2.50),
        (4, 'Mineral Water', 100, 1.00)
    ]
    
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
    return "Product Page (Under Construction by Filbert)"

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

