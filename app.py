from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# MongoDB connection URI
client = MongoClient(
    "mongodb+srv://phemanthkumar746:htnameh509h@data.psr09.mongodb.net/?retryWrites=true&w=majority&appName=Data"
)
db = client["myLoginDatabase"]  # Replace with your database name
users_collection = db["users"]  # Replace with your collection name

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json

        # Validate required fields
        if not data or 'username' not in data or 'password' not in data or 'email' not in data:
            return jsonify(status="failure", message="Username, email, and password are required"), 400

        username = data['username']
        email = data['email']
        password = data['password']

        # Check for existing user
        if users_collection.find_one({'username': username}):
            return jsonify(status="failure", message="Username already exists"), 409
        if users_collection.find_one({'email': email}):
            return jsonify(status="failure", message="Email already exists"), 409

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create and insert the user document
        user = {'username': username, 'email': email, 'password': hashed_password}
        users_collection.insert_one(user)

        return jsonify(status="success", message="User registered successfully"), 201

    except Exception as e:
        return jsonify(status="failure", message=f"An error occurred: {str(e)}"), 500


@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json

        # Validate required fields
        if not data or 'username' not in data or 'password' not in data:
            return jsonify(status="failure", message="Username and password are required"), 400

        login_identifier = data['username']  # Can be username or email
        password = data['password']

        # Find user by username or email
        user = users_collection.find_one({'$or': [{'username': login_identifier}, {'email': login_identifier}]})

        if not user:
            return jsonify(status="failure", message="User not found"), 404

        # Check password hash
        if check_password_hash(user['password'], password):
            return jsonify(status="success", message="Login successful"), 200
        else:
            return jsonify(status="failure", message="Invalid password"), 401

    except Exception as e:
        return jsonify(status="failure", message=f"An error occurred: {str(e)}"), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
