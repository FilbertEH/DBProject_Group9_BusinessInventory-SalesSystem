from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
from stats import get_dashboard_stats

load_dotenv()

app = Flask(__name__)
app.secret_key = "secret_key_for_session_management" # Change this to random string

@app.route('/')
def dashboard():
    stats = get_dashboard_stats()
    return render_template('index.html', stats=stats)

# --- PLACEHOLDERS FOR TEAMMATES ---
# Filbert will work here
@app.route('/products')
def product_list():
    return "Product Page (Under Construction by Filbert)"

# Arya will work here
@app.route('/customers')
def customer_list():
    return "Customer Page (Under Construction by Arya)"

if __name__ == '__main__':
    app.run(debug=True, port=5000)