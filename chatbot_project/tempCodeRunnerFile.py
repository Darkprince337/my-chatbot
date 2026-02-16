
# --- User Authentication Setup ---
USERS_FILE = 'data/users.json'

def load_users():
    """Loads the users dictionary from the JSON file."""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        try: