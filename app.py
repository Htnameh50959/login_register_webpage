import secrets
from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash
import re
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
# Connect to MongoDB
client = MongoClient("mongodb+srv://phemanthkumar746:htnameh509h@data.psr09.mongodb.net/?retryWrites=true&w=majority&appName=Data")
db = client.myLoginDatabase
users_collection = db.users
# Home page (Login form)
@app.route('/')
def index():
    return render_template('index.html')
# Home page after login
@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('home.html')
# Registration form route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password_1 = request.form['password_1']
        password_2 = request.form['password_2']
        # Check if the passwords match
        if password_1 != password_2:
            return render_template('register.html', error="Passwords do not match!")
        # Check if username or email already exists
        if users_collection.find_one({'username': username}):
            return render_template('register.html', error="Username already exists!")
        if users_collection.find_one({'email': email}):
            return render_template('register.html', error="Email already exists!")
        # Hash the password
        hashed_password = generate_password_hash(password_1)
        # Insert the new user into the database
        users_collection.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password,
            'verified': False  # Initialize email verification status
        })
        # Redirect to login page after successful registration
        return redirect(url_for('index'))
    return render_template('register.html')
# Handle login form submission
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_identifier = request.form['login']  # Input field named 'login'
        password = request.form['password']
        # Check if the user exists in the database by username or email
        user = users_collection.find_one({'$or': [{'username': login_identifier}, {'email': login_identifier}]})
        if user:
            # Verify the hashed password
            if check_password_hash(user['password'], password):
                session['username'] = user['username']  # Store user in session
                return redirect(url_for('home'))
            else:
                return render_template('index.html', error="Invalid password!")
        else:
            return render_template('index.html', error="User not found!")
    return render_template('index.html')
# Logout function
@app.route('/logout')
def logout():
    session.pop('username', None)  # Clear session data
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)
