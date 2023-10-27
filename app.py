from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_REGISTER_NAME = 'register.db'
DB_ADMIN_NAME = 'admin.db'
DB_APPLICANT_NAME = 'applicant.db'
DB_PAYMENT_NAME = 'payment.db'

def init_register_db():
    conn = sqlite3.connect(DB_REGISTER_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registered_users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def init_admin_db():
    conn = sqlite3.connect(DB_ADMIN_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY,
            admin_email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def init_applicant_db():
    conn = sqlite3.connect(DB_APPLICANT_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applicants (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            dob TEXT NOT NULL,
            gender TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT NOT NULL,
            adhar TEXT NOT NULL,
            residence TEXT NOT NULL,
            permanent TEXT NOT NULL,
            pass_type TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def init_payment_db():
    conn = sqlite3.connect(DB_PAYMENT_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES registered_users (id)
        )
    ''')
    conn.commit()
    conn.close()

def handle_db_error(func):
    try:
        return func()
    except Exception as e:
        flash("An error occurred while processing your request.", 'danger')

def generate_unique_id(prefix, length=4):
    random_number = ''.join(random.choice(string.digits) for _ in range(length))
    return f"{prefix}{random_number}"

init_register_db()
init_admin_db()
init_applicant_db()
init_payment_db()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html')
    elif 'admin_id' in session:
        return render_template('admin_dashboard.html', user_data=None)
    else:
        return redirect(url_for('index'))

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'admin_id' in session:
        conn = sqlite3.connect(DB_REGISTER_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM registered_users")
        user_data = cursor.fetchall()
        conn.close()
        return render_template('admin_dashboard.html', user_data=user_data)
    else:
        return redirect(url_for('admin_login'))

@app.route('/view-registered-data')
def view_registered_data():
    conn = sqlite3.connect(DB_REGISTER_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM registered_users")
    user_data = cursor.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', user_data=user_data)

@app.route('/application', methods=['GET'])
def application():
    return render_template('application.html')

@app.route('/register', methods=['GET'])
def register_form():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('register-email')
    password = request.form.get('register-password')
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    conn = sqlite3.connect(DB_REGISTER_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM registered_users WHERE username = ?", (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        flash("Username already exists. Choose another username.", 'danger')
        conn.close()
    else:
        cursor.execute("INSERT INTO registered_users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        flash("Registration successful. You can now log in.", 'success')
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('login-email')
    password = request.form.get('login-password')
    conn = sqlite3.connect(DB_REGISTER_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM registered_users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user and check_password_hash(user[1], password):
        session['user_id'] = user[0]
        conn.close()
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid login credentials. Please try again.", 'danger')
        conn.close()
    return redirect(url_for('index'))

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_email = request.form.get('admin-login-email')
        admin_password = request.form.get('admin-login-password')
        conn = sqlite3.connect(DB_ADMIN_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM admin_users WHERE admin_email = ?", (admin_email,))
        admin = cursor.fetchone()
        conn.close()
        if admin and check_password_hash(admin[1], admin_password):
            session['admin_id'] = admin[0]
            return redirect(url_for('admin_dashboard'))
    return render_template('admin_dashboard.html')

@app.route('/admin-register', methods=['POST'])
def admin_register():
    admin_email = request.form.get('admin-register-email')
    admin_password = request.form.get('admin-register-password')
    hashed_password = generate_password_hash(admin_password, method='pbkdf2:sha256')
    conn = sqlite3.connect(DB_ADMIN_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM admin_users WHERE admin_email = ?", (admin_email,))
    existing_admin = cursor.fetchone()
    if existing_admin:
        conn.close()
        return "Admin with this email already exists."
    else:
        cursor.execute("INSERT INTO admin_users (admin_email, password) VALUES (?, ?)", (admin_email, hashed_password))
        conn.commit()
        conn.close()
        return "Admin registration successful."

@app.route('/new-application', methods=['POST'])
def new_application():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        adhar = request.form.get('adhar')
        residence = request.form.get('residence')
        permanent = request.form.get('permanent')
        pass_type = request.form.get('pass-type')
        
        # Generate a unique pass ID
        pass_id = generate_unique_id('EBP-')  # Use your own format or prefix
        
        conn = sqlite3.connect(DB_APPLICANT_NAME)
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO applicants (id, name, age, dob, gender, mobile, email, adhar, residence, permanent, pass_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(insert_query, (pass_id, name, age, dob, gender, mobile, email, adhar, residence, permanent, pass_type))
        conn.commit()
        conn.close()
        
        flash("Application submitted successfully.", 'success')
        
        # Redirect to E-Bus Pass page with the unique pass ID
        return redirect(url_for('submission'))

    return render_template('application.html')


@app.route('/submission')
def submission():
    return render_template('submission.html')

@app.route('/payment', methods=['POST'])
def payment():
    if request.method == 'POST':
        # Process the payment (your payment processing logic here)
        flash("Payment processed successfully.", 'success')

        pass_id = request.form.get('pass_id')  # Pass ID is required for generating the E-Bus pass

        # Retrieve E-Bus Pass details based on pass_id
        pass_details = fetch_pass_details(pass_id)

        if pass_details:
            return render_template('e_pass.html', pass_id=pass_id, pass_details=pass_details)
        else:
            return "E-Bus Pass not found."

    return render_template('payment.html')

def fetch_pass_details(pass_id):
    # Implement a function to retrieve E-Bus Pass details from your database
    # Replace this with your database query logic
    pass_details = {
        "name": "Alwin Selva Kumar",
        "address": "Chennai",
        "expiry_date": "2023-10-26",
        "passenger_sign": "path_to_passenger_sign_image.png",
        "provider_sign": "path_to_provider_sign_image.png"
    }
    return pass_details
    
@app.route('/payment', methods=['GET'], endpoint='payment_get')
def payment_get():
    return render_template('payment.html')

@app.route('/payment', methods=['POST'], endpoint='payment_post')
def payment_post():
    # Process the payment here
    pass_details = generate_pass_details()  # Replace this with your logic
    if pass_details:
        return render_template('e_pass.html', pass_details=pass_details)
    else:
        return "E-Bus Pass not found"

@app.route('/e_pass', methods=['GET'])
def e_pass_form():
    pass_id = request.args.get('pass_id')
    pass_details = fetch_pass_details(pass_id)
    if pass_details:
        return render_template('e_pass.html', pass_id=pass_id, pass_details=pass_details)
    else:
        return "E-Bus Pass not found."

@app.route('/view-applicant-data')
def view_applicant_data():
    conn = sqlite3.connect(DB_APPLICANT_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applicants")
    applicant_data = cursor.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', applicant_data=applicant_data)

@app.route('/logout')
def logout():
    session.pop('user_id', default=None)
    session.pop('admin_id', default=None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_register_db()
    init_admin_db()
    init_applicant_db()
    init_payment_db()
    app.run(debug=True)