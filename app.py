"""
Student Management System
Flask Backend Application with SQLite Database
Created for Python Full Stack Development Internship Demonstration
"""

import os
import sqlite3
import re
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, session

# Initialize Flask App
app = Flask(__name__)
app.secret_key = "student_management_secret_key_2026"

# Database Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database.db')


def get_db_connection():
    """Establish connection to SQLite database with Row factory."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the students table if it doesn't exist and seed initial demo data."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

    # Create users table for Admin authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

    # Seed default admin account if not already present
    admin_user = cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()
    if not admin_user:
        cursor.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            ('admin', generate_password_hash('admin123'))
        )
        conn.commit()

    # Seed demo data if database is currently empty
    cursor.execute('SELECT COUNT(*) as count FROM students')
    student_count = cursor.fetchone()['count']

    if student_count == 0:
        sample_students = [
            ("Aarav Sharma", "CS-101", "aarav.sharma@example.com", "Computer Science", "9876543210"),
            ("Priya Patel", "IT-202", "priya.patel@example.com", "Information Technology", "9812345678"),
            ("Rohan Verma", "EC-303", "rohan.verma@example.com", "Electronics & Comm", "9823456789"),
            ("Sneha Reddy", "ME-404", "sneha.reddy@example.com", "Mechanical Engg", "9834567890"),
            ("Vikram Das", "CS-105", "vikram.das@example.com", "Computer Science", "9845678901")
        ]
        cursor.executemany('''
            INSERT INTO students (name, roll_number, email, department, phone)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_students)
        conn.commit() 

    conn.close()


def validate_email(email):
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email.strip()) is not None


def validate_phone(phone):
    """Validate phone number format (at least 10 digits)."""
    clean_phone = re.sub(r'[\s\-+()]', '', phone.strip())
    return clean_phone.isdigit() and len(clean_phone) >= 10


def login_required(f):
    """Decorator to protect routes requiring admin authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ---------------------------- AUTH ROUTES ----------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Admin Login Page:
    GET: Render login form.
    POST: Authenticate username and password with secure hash verification.
    """
    if 'user' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template('login.html', username=username)

        conn = get_db_connection()
        cursor = conn.cursor()
        user = cursor.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = user['username']
            flash(f"Welcome back, {user['username'].capitalize()}! Logged in successfully.", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password. Please try again.", "danger")
            return render_template('login.html', username=username)

    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    Admin Logout:
    Clears the active session and redirects back to the login page.
    """
    session.pop('user', None)
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('login'))


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Change Password:
    Allows the currently logged-in admin to update their password.
    Requires entering the current password for verification before accepting a new one.
    """
    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Validate all fields are filled
        if not current_password or not new_password or not confirm_password:
            flash("All fields are required. Please fill in every field.", "danger")
            return render_template('change_password.html')

        # Fetch logged-in user from database
        conn = get_db_connection()
        cursor = conn.cursor()
        user = cursor.execute('SELECT * FROM users WHERE username = ?', (session['user'],)).fetchone()

        if not user:
            conn.close()
            flash("User session is invalid. Please log in again.", "danger")
            return redirect(url_for('logout'))

        # Verify current password
        if not check_password_hash(user['password'], current_password):
            conn.close()
            flash("Current password is incorrect. Please try again.", "danger")
            return render_template('change_password.html')

        # Validate new password strength
        if len(new_password) < 6:
            conn.close()
            flash("New password must be at least 6 characters long.", "danger")
            return render_template('change_password.html')

        # Check new password matches confirmation
        if new_password != confirm_password:
            conn.close()
            flash("New password and confirm password do not match.", "danger")
            return render_template('change_password.html')

        # Check new password is different from current
        if check_password_hash(user['password'], new_password):
            conn.close()
            flash("New password cannot be the same as the current password.", "warning")
            return render_template('change_password.html')

        # Update password in database
        try:
            hashed_new = generate_password_hash(new_password)
            cursor.execute('UPDATE users SET password = ? WHERE username = ?', (hashed_new, session['user']))
            conn.commit()
            conn.close()
            flash("Password changed successfully! Use your new password on the next login.", "success")
            return redirect(url_for('index'))
        except sqlite3.Error as err:
            conn.close()
            flash(f"Database Error: {err}", "danger")
            return render_template('change_password.html')

    return render_template('change_password.html')


# ---------------------------- STUDENT CRUD ROUTES ----------------------------

@app.route('/')
@login_required
def index():
    """
    Dashboard & Student List View:
    Displays all student records or filtered records matching search keyword and department.
    Also calculates quick summary metrics for the dashboard header.
    """
    search_query = request.args.get('search', '').strip()
    selected_dept = request.args.get('department', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Dynamic query builder
    query = 'SELECT * FROM students WHERE 1=1'
    params = []

    if selected_dept:
        query += ' AND department = ?'
        params.append(selected_dept)

    if search_query:
        query += ' AND (roll_number LIKE ? OR name LIKE ? OR department LIKE ?)'
        wildcard = f"%{search_query}%"
        params.extend([wildcard, wildcard, wildcard])

    query += ' ORDER BY id DESC'
    students = cursor.execute(query, params).fetchall()

    # Fetch distinct departments for the filter dropdown
    depts_rows = cursor.execute(
        'SELECT DISTINCT department FROM students WHERE department IS NOT NULL AND department != "" ORDER BY department ASC'
    ).fetchall()
    all_departments = [row['department'] for row in depts_rows]

    # Calculate summary statistics for the dashboard
    total_students = cursor.execute('SELECT COUNT(*) as count FROM students').fetchone()['count']
    total_depts = cursor.execute('SELECT COUNT(DISTINCT department) as count FROM students').fetchone()['count']

    conn.close()

    return render_template(
        'index.html',
        students=students,
        search_query=search_query,
        selected_dept=selected_dept,
        all_departments=all_departments,
        total_students=total_students,
        total_depts=total_depts
    )


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_student():
    """
    Add Student:
    GET: Render student registration form.
    POST: Validate input fields, verify unique roll number, insert into SQLite database.
    """
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        roll_number = request.form.get('roll_number', '').strip().upper()
        email = request.form.get('email', '').strip()
        department = request.form.get('department', '').strip()
        phone = request.form.get('phone', '').strip()

        form_data = {
            'name': name,
            'roll_number': roll_number,
            'email': email,
            'department': department,
            'phone': phone
        }

        # Input Validation
        if not name or not roll_number or not email or not department or not phone:
            flash("All fields are required. Please fill in all information.", "danger")
            return render_template('add_student.html', form_data=form_data)

        if not validate_email(email):
            flash("Please enter a valid email address (e.g., student@example.com).", "danger")
            return render_template('add_student.html', form_data=form_data)

        if not validate_phone(phone):
            flash("Please enter a valid phone number with at least 10 digits.", "danger")
            return render_template('add_student.html', form_data=form_data)

        # Database insertion with unique check
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if roll number already exists
            existing_student = cursor.execute(
                'SELECT id FROM students WHERE roll_number = ?', (roll_number,)
            ).fetchone()

            if existing_student:
                flash(f"Roll Number '{roll_number}' already exists! Please use a unique Roll Number.", "warning")
                conn.close()
                return render_template('add_student.html', form_data=form_data)

            # Insert record
            cursor.execute('''
                INSERT INTO students (name, roll_number, email, department, phone)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, roll_number, email, department, phone))
            conn.commit()
            conn.close()

            flash(f"Student '{name}' added successfully!", "success")
            return redirect(url_for('index'))

        except sqlite3.Error as err:
            conn.close()
            flash(f"Database Error: {err}", "danger")
            return render_template('add_student.html', form_data=form_data)

    return render_template('add_student.html', form_data={})


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_student(id):
    """
    Update Student:
    GET: Fetch student record by ID and populate the update form.
    POST: Validate edits, verify unique roll number conflict, update record.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    student = cursor.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()

    if not student:
        conn.close()
        flash("Student record not found.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        roll_number = request.form.get('roll_number', '').strip().upper()
        email = request.form.get('email', '').strip()
        department = request.form.get('department', '').strip()
        phone = request.form.get('phone', '').strip()

        form_data = {
            'id': id,
            'name': name,
            'roll_number': roll_number,
            'email': email,
            'department': department,
            'phone': phone
        }

        # Form Validations
        if not name or not roll_number or not email or not department or not phone:
            flash("All fields are required. Please fill in all information.", "danger")
            return render_template('update_student.html', student=form_data)

        if not validate_email(email):
            flash("Please enter a valid email address.", "danger")
            return render_template('update_student.html', student=form_data)

        if not validate_phone(phone):
            flash("Please enter a valid phone number (at least 10 digits).", "danger")
            return render_template('update_student.html', student=form_data)

        # Check if roll number belongs to another student
        duplicate = cursor.execute(
            'SELECT id FROM students WHERE roll_number = ? AND id != ?',
            (roll_number, id)
        ).fetchone()

        if duplicate:
            flash(f"Roll Number '{roll_number}' is already assigned to another student.", "warning")
            return render_template('update_student.html', student=form_data)

        try:
            cursor.execute('''
                UPDATE students
                SET name = ?, roll_number = ?, email = ?, department = ?, phone = ?
                WHERE id = ?
            ''', (name, roll_number, email, department, phone, id))
            conn.commit()
            conn.close()

            flash(f"Student '{name}' updated successfully!", "success")
            return redirect(url_for('index'))

        except sqlite3.Error as err:
            conn.close()
            flash(f"Database Error: {err}", "danger")
            return render_template('update_student.html', student=form_data)

    conn.close()
    return render_template('update_student.html', student=student)


@app.route('/delete/<int:id>', methods=['POST', 'GET'])
@login_required
def delete_student(id):
    """
    Delete Student:
    Removes the specified student record from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    student = cursor.execute('SELECT name FROM students WHERE id = ?', (id,)).fetchone()

    if student:
        student_name = student['name']
        cursor.execute('DELETE FROM students WHERE id = ?', (id,))
        conn.commit()
        flash(f"Student '{student_name}' record deleted successfully.", "success")
    else:
        flash("Record not found or already deleted.", "warning")

    conn.close()
    return redirect(url_for('index'))


# Initialize Database upon application startup
init_db()

if __name__ == '__main__':
    # Run the Flask local development server
    # debug=True allows auto-reloading when source files are modified
    print("Starting Student Management System...")
    print("Access the application at: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
