from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
import os
from dotenv import load_dotenv
from stats import get_dashboard_stats
from sale import create_sale, get_sale_history, get_sale_with_items
from crud_customer import get_all_customers, add_customer, get_customer, update_customer, delete_customer
from decimal import Decimal, InvalidOperation
from crud_product import (
    list_products,
    list_categories,
    create_product,
    delete_product,
    get_all_products,
    get_product,
    update_product,
    update_stock,
)
from crud_category import (
    get_all_categories,
    get_category,
    create_category,
    update_category,
    delete_category,
)
from auth import auth_bp, load_user_from_db, role_required

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key-for-development")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login' # type: ignore
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'error'

# User loader callback
@login_manager.user_loader
def load_user(operator_id):
    return load_user_from_db(operator_id)

# Register auth blueprint
app.register_blueprint(auth_bp)

# Error handlers
@app.errorhandler(403)
def forbidden(error):
    flash('Access denied. You do not have permission to access this page.', 'error')
    return redirect(url_for('dashboard'))

@app.errorhandler(404)
def not_found(error):
    flash('Page not found.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/')
@login_required
def dashboard():
    stats = get_dashboard_stats()
    return render_template('index.html', stats=stats)

# --- SALE MANAGEMENT (Your Implementation) ---

@app.route('/sales')
@login_required
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
@login_required
def new_sale_form():
    """Show the POS form for creating a new sale (uses live products)."""
    products = get_all_products()  # [(id, name, stock, price)]
    return render_template('new_sale.html', products=products)

@app.route('/sales/create', methods=['POST'])
@login_required
def create_sale_action():
    """Process the sale form submission"""
    try:
        operator_id = current_user.operator_id  # Get from logged-in user
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
@login_required
def product_list():
    rows = list_products()  # [(id, name, sku, price, qty, category_name)]
    return render_template('products.html', rows=rows)

@app.route('/product/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
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

@app.route('/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def product_edit(id):
    categories = list_categories()
    product = get_product(id)

    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('product_list'))

    if request.method == 'POST':
        name = (request.form.get('product_name') or '').strip()
        sku = (request.form.get('sku') or '').strip()
        cat = request.form.get('category_id')
        qty = request.form.get('quantity_stock', '0')
        price = request.form.get('price', '0')

        if not name or not sku or not cat:
            flash('Name, SKU, and Category are required.', 'error')
            return render_template('edit_product.html', categories=categories, product=product)

        try:
            qty = int(qty); price = Decimal(price)
            if qty < 0 or price < 0:
                raise ValueError
        except (ValueError, InvalidOperation):
            flash('Quantity and price must be valid non-negative numbers.', 'error')
            return render_template('edit_product.html', categories=categories, product=product)

        ok, err = update_product(id, name, sku, price, qty, int(cat))
        if err:
            flash(err, 'error')
            return render_template('edit_product.html', categories=categories, product=product)

        flash('Product updated.', 'success')
        return redirect(url_for('product_list'))

    return render_template('edit_product.html', categories=categories, product=product)

@app.route('/product/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def product_delete(id):
    ok, msg = delete_product(id)
    flash('Product deleted.' if ok else (msg or 'Delete failed.'), 'success' if ok else 'error')
    return redirect(url_for('product_list'))

@app.route('/product/update_stock', methods=['POST'])
def product_update_stock():
    pid = request.form.get('product_id')
    qty = request.form.get('new_stock')

    if not pid or qty is None:
        flash('Product ID and stock are required.', 'error')
        return redirect(url_for('product_list'))

    try:
        pid = int(pid)
        qty = int(qty)
        if qty < 0:
            raise ValueError
    except ValueError:
        flash('Stock must be a non-negative integer.', 'error')
        return redirect(url_for('product_list'))

    ok, msg = update_stock(pid, qty)
    flash('Stock updated.' if ok else (msg or 'Update failed.'), 'success' if ok else 'error')
    return redirect(url_for('product_list'))

# Arya will work here
@app.route('/customers')
@login_required
def customer_list():
    customers = get_all_customers()
    return render_template('customers.html', customers=customers)

@app.route('/customer/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_customer_page():
    if request.method == 'POST':
        name = request.form['customer_name']
        phone = request.form['phone']

        add_customer(name, phone)
        return redirect(url_for('customer_list'))

    return render_template('add_customer.html')

@app.route('/customer/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def customer_edit(id):
    customer = get_customer(id)

    if not customer:
        flash('Customer not found.', 'error')
        return redirect(url_for('customer_list'))

    if request.method == 'POST':
        name = (request.form.get('customer_name') or '').strip()
        phone = (request.form.get('phone') or '').strip()

        if not name or not phone:
            flash('Customer name and phone are required.', 'error')
            return render_template('edit_customer.html', customer=customer)

        ok, err = update_customer(id, name, phone)
        if err:
            flash(err, 'error')
            return render_template('edit_customer.html', customer=customer)

        flash('Customer updated successfully.', 'success')
        return redirect(url_for('customer_list'))

    return render_template('edit_customer.html', customer=customer)

@app.route('/customer/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def customer_delete(id):
    ok, msg = delete_customer(id)
    flash('Customer deleted.' if ok else (msg or 'Delete failed.'), 'success' if ok else 'error')
    return redirect(url_for('customer_list'))

# Category Management
@app.route('/categories')
@login_required
def category_list():
    categories = get_all_categories()
    return render_template('categories.html', categories=categories)

@app.route('/category/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def category_add():
    if request.method == 'POST':
        name = (request.form.get('category_name') or '').strip()

        if not name:
            flash('Category name is required.', 'error')
            return render_template('add_category.html')

        create_category(name)
        flash('Category created successfully.', 'success')
        return redirect(url_for('category_list'))

    return render_template('add_category.html')

@app.route('/category/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def category_edit(id):
    category = get_category(id)

    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('category_list'))

    if request.method == 'POST':
        name = (request.form.get('category_name') or '').strip()

        if not name:
            flash('Category name is required.', 'error')
            return render_template('edit_category.html', category=category)

        ok, err = update_category(id, name)
        if err:
            flash(err, 'error')
            return render_template('edit_category.html', category=category)

        flash('Category updated successfully.', 'success')
        return redirect(url_for('category_list'))

    return render_template('edit_category.html', category=category)

@app.route('/category/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def category_delete(id):
    ok, msg = delete_category(id)
    flash('Category deleted.' if ok else (msg or 'Delete failed.'), 'success' if ok else 'error')
    return redirect(url_for('category_list'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

