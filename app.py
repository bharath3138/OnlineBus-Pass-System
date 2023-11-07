from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
from datetime import datetime, timedelta

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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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

def generate_unique_id(prefix, length=4):
    random_number = ''.join(random.choice(string.digits) for _ in range(length))
    return f"{prefix}{random_number}"

def fetch_pass_details(pass_id):
    conn = sqlite3.connect(DB_APPLICANT_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applicants WHERE id = ?", (pass_id,))
    pass_details = cursor.fetchone()
    conn.close()
    return pass_details

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html', target_section=request.args.get('target'))
    elif 'admin_id' in session:
        conn = sqlite3.connect(DB_REGISTER_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM registered_users")
        user_data = cursor.fetchall()
        conn.close()
        return render_template('admin_dashboard.html', user_data=user_data, target_section=request.args.get('target'))
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
    return render_template('login.html')

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
        # Collect applicant data
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
        pass_id = generate_unique_id('EBP-')
        pass_details = fetch_pass_details_from_database(pass_id)
        # Store applicant data in the database (applicant.db)
        conn = sqlite3.connect(DB_APPLICANT_NAME)
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO applicants (id, name, age, dob, gender, mobile, email, adhar, residence, permanent, pass_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(insert_query, (pass_id, name, age, dob, gender, mobile, email, adhar, residence, permanent, pass_type))
        conn.commit()
        conn.close()

        # Generate e-bus pass data
        e_pass_data = {
            'pass_id': pass_id,
            'name': name,
            'gender': gender,
            'residence': residence,
            # Include other relevant data
        }

        # Render the e-pass template and pass the e-bus pass data
        return redirect(url_for('submission', pass_id=pass_id))
    return render_template('application.html')

@app.route('/submission/<pass_id>')
def submission(pass_id):
    return render_template('submission.html', pass_id=pass_id)

@app.route('/e_pass', methods=['GET'])
def e_pass_form():
    pass_details = request.args.get('pass_details')
    if pass_details:
        return render_template('e_pass.html', pass_details=pass_details)
    else:
        return "E-Bus Pass not found."

@app.route('/payment/<pass_id>', methods=['GET'])
def payment(pass_id):
    pass_details = fetch_pass_details_from_database(pass_id)

    if pass_details:
        return render_template('payment.html', pass_id=pass_id, pass_details=pass_details)
    else:
        return "E-Bus Pass not found"

@app.route('/generate-pass/<pass_id>', methods=['GET'])
def generate_pass(pass_id):
    # Implement the logic to generate the e-bus pass based on the pass_id
    pass_details = fetch_pass_details_from_database(pass_id)
    if pass_details:
        return render_template('e_pass.html', pass_details=pass_details)
    else:
        return "E-Bus Pass not found"


@app.route('/payment', methods=['POST'])
def payment_post():
    pass_id = request.form.get('pass_id')  # Get the pass ID from the form
    pass_details = fetch_pass_details_from_database(pass_id)

    if pass_details:
        return render_template('e_pass.html', pass_details=pass_details)
    else:
        return "E-Bus Pass not found"


def fetch_pass_details_from_database(pass_id):
    # Implement the logic to retrieve pass details from your database (applicant.db)
    conn = sqlite3.connect(DB_APPLICANT_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, gender, residence FROM applicants WHERE id = ?", (pass_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        pass_id, name, gender, residence = result
        # You can calculate the expiry date here (for example, add a year to the current date)
        expiry_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        # You may also have logic to retrieve passenger sign and officer sign
        passenger_sign = "path_to_passenger_sign_image.png"
        officer_sign = "path_to_officer_sign_image.png"

        # Construct the pass_details dictionary
        pass_details = {
            "pass_id": pass_id,
            "name": name,
            "gender": gender,
            "residence": residence,
            "expiry_date": expiry_date,
            "passenger_sign": passenger_sign,
            "officer_sign": officer_sign
        }
        return pass_details
    else:
        return None

def fetch_last_submitted_application():
    conn = sqlite3.connect(DB_APPLICANT_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM applicants ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]  # Return the ID of the last submitted application
    else:
        return None

@app.route('/submit-payment', methods=['POST'])
def submit_payment():
    # Retrieve the details of the last submitted application from the database
    pass_id = fetch_last_submitted_application()

    if pass_id:
        # Fetch the pass details for the last submitted application
        pass_details = fetch_pass_details_from_database(pass_id)

        if pass_details:
            return render_template('e_pass.html', pass_details=pass_details)
        else:
            return "E-Bus Pass not found"
    else:
        return "No recent applications found"

@app.route('/view-applicant-data')
def view_applicant_data():
    conn = sqlite3.connect(DB_APPLICANT_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applicants")
    applicant_data = cursor.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', applicant_data=applicant_data)

@app.route('/renewal', methods=['GET', 'POST'])
def renewal():
    if request.method == 'POST':
        pass_id = request.form.get('pass_id')
        pass_details = fetch_pass_details_from_database(pass_id)

        if pass_details:
            return redirect(url_for('payment', pass_id=pass_id))  # Redirect to the payment page
        else:
            flash("Pass ID not found. Please enter a valid Pass ID.", 'danger')
    
    return render_template('renewal.html')

@app.route('/generate-renewed-pass/<pass_id>', methods=['GET'])
def generate_renewed_pass(pass_id):
    # Implement the logic to generate the renewed e-bus pass based on the pass_id
    pass_details = fetch_pass_details_from_database(pass_id)
    if pass_details:
        # You may have logic to renew the pass (e.g., update the expiration date)
        renewed_pass_details = pass_details  # You can modify this based on your actual logic
        return render_template('renewed.html', pass_details=renewed_pass_details)
    else:
        flash("E-Bus Pass not found.", 'danger')
        return redirect(url_for('renewal'))

@app.route('/renewed', methods=['GET'])
def renewed():
    # This route can display the renewed pass details (e.g., after a successful renewal)
    # You can use the "generate_renewed_pass" route and template for this purpose.
    return "Renewed Pass Details"    

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
