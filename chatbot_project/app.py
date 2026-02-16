# app.py
import os
import json
from flask import Flask, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from chatbot import Chatbot

# --- App Initialization ---
app = Flask(__name__)

# --- Chatbot Initialization ---
print("Initializing Chatbot...")
chatbot_instance = Chatbot()
print("Chatbot Initialized Successfully.")

# --- User Authentication Setup ---
USERS_FILE = 'data/users.json'

def load_users():
    """Loads the users dictionary from the JSON file."""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    """Saves the users dictionary to the JSON file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# --- Page Routes ---

@app.route('/')
def login_page():
    """Serves the login/registration page."""
    return render_template('login.html')

@app.route('/chat')
def chat_page():
    """Serves the main chat interface."""
    return render_template('index.html')


# --- API Routes ---

# NEW: Registration Endpoint
@app.route('/api/register', methods=['POST'])
def register():
    """Handles new user registration."""
    data = request.json
    user_id = data.get('user_id')
    password = data.get('password')

    if not user_id or not password:
        return jsonify({"error": "User ID and password are required"}), 400

    users = load_users()
    if user_id in users:
        return jsonify({"error": "User ID already exists"}), 409 # 409 Conflict

    # Hash the password for security
    hashed_password = generate_password_hash(password)
    users[user_id] = {"password_hash": hashed_password}
    save_users(users)

    return jsonify({"success": True, "message": "Registration successful. Please log in."}), 201

# NEW: Login Endpoint
@app.route('/api/login', methods=['POST'])
def login():
    """Handles user login."""
    data = request.json
    user_id = data.get('user_id')
    password = data.get('password')

    if not user_id or not password:
        return jsonify({"error": "User ID and password are required"}), 400

    users = load_users()
    user = users.get(user_id)

    # Check if user exists and if the password hash matches
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({"error": "Invalid user ID or password"}), 401 # 401 Unauthorized

    return jsonify({"success": True})


# Chat API - no changes needed here
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('user_id')
    user_message = data.get('message')
    if not user_id or not user_message:
        return jsonify({"error": "Missing user_id or message"}), 400
    if user_id not in chatbot_instance.all_users_data:
        chatbot_instance.handle_user_login(user_id)
    response_data = chatbot_instance.get_response(user_id, user_message)
    return jsonify(response_data)

# Feedback API - no changes needed here
@app.route('/api/feedback', methods=['POST'])
def feedback():
    data = request.json
    user_id = data.get('user_id')
    reward = float(data.get('reward', 0))
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    feedback_message = chatbot_instance.provide_feedback(user_id, reward)
    return jsonify({"status": "success", "message": feedback_message})


# --- Main Execution ---
if __name__ == '__main__':
    # Ensure the 'data' directory exists
    if not os.path.exists('data'):
        os.makedirs('data')
    app.run(debug=True, threaded=False)