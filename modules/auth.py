"""
AUTHENTICATION MODULE
=====================
This module handles all user authentication operations.
Functions:
- login_user()      : Verifies username and password
- register_user()   : Creates a new user account
- get_user_by_id()  : Fetches user details by user ID
- change_password() : Updates user password
- get_all_users()   : Returns list of all registered users
"""

import bcrypt
import sys
import os

# Add parent directory to path so we can import db_setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_setup import get_connection


def login_user(username, password):
    """
    Verifies user credentials against the database.
    Returns user data dictionary if successful, None if failed.

    Parameters:
        username (str) : Username entered by the user
        password (str) : Plain text password entered by the user
    """
    conn   = get_connection()
    cursor = conn.cursor()

    # Fetch user record from database by username
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()

    # If user not found, return None
    if user is None:
        return None

    # Verify the entered password against the stored hashed password
    password_match = bcrypt.checkpw(
        password.encode('utf-8'),
        user["password"].encode('utf-8')
    )

    # Return user data if password matches, else return None
    if password_match:
        return {
            "id"        : user["id"],
            "username"  : user["username"],
            "full_name" : user["full_name"],
        }
    return None


def register_user(username, password, full_name):
    """
    Registers a new user in the database.
    Returns True if successful, False if username already exists.

    Parameters:
        username  (str) : Desired username
        password  (str) : Plain text password
        full_name (str) : Full name of the user
    """
    conn   = get_connection()
    cursor = conn.cursor()

    # Check if username already exists in the database
    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return False  # Username already taken

    # Encrypt the password before storing in database
    hashed = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    # Insert new user record into the database
    cursor.execute(
        "INSERT INTO users (username, password, full_name) VALUES (?, ?, ?)",
        (username, hashed, full_name)
    )
    conn.commit()
    conn.close()
    return True


def get_user_by_id(user_id):
    """
    Fetches user details from the database using user ID.
    Returns user data dictionary or None if not found.

    Parameters:
        user_id (int) : Unique ID of the user
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, full_name, created_at FROM users WHERE id = ?",
        (user_id,)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "id"         : user["id"],
            "username"   : user["username"],
            "full_name"  : user["full_name"],
            "created_at" : user["created_at"],
        }
    return None


def change_password(user_id, old_password, new_password):
    """
    Updates the password for an existing user.
    Returns True if successful, False if old password is incorrect.

    Parameters:
        user_id      (int) : ID of the user
        old_password (str) : Current plain text password
        new_password (str) : New plain text password to set
    """
    conn   = get_connection()
    cursor = conn.cursor()

    # Fetch current hashed password from database
    cursor.execute(
        "SELECT password FROM users WHERE id = ?",
        (user_id,)
    )
    user = cursor.fetchone()

    if user is None:
        conn.close()
        return False

    # Verify old password before allowing the change
    password_match = bcrypt.checkpw(
        old_password.encode('utf-8'),
        user["password"].encode('utf-8')
    )

    if not password_match:
        conn.close()
        return False  # Old password is incorrect

    # Encrypt the new password and update in database
    new_hashed = bcrypt.hashpw(
        new_password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    cursor.execute(
        "UPDATE users SET password = ? WHERE id = ?",
        (new_hashed, user_id)
    )
    conn.commit()
    conn.close()
    return True


def get_all_users():
    """
    Returns a list of all registered users.
    Used for admin panel and multi-user management.
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, full_name, created_at FROM users"
    )
    users = cursor.fetchall()
    conn.close()

    return [
        {
            "id"         : u["id"],
            "username"   : u["username"],
            "full_name"  : u["full_name"],
            "created_at" : u["created_at"],
        }
        for u in users
    ]


# ── Test authentication directly ──────────────────────────
if __name__ == "__main__":
    print("Testing login with default credentials...")
    result = login_user("admin", "Admin@123")
    if result:
        print(f"Login successful!")
        print(f"User     : {result['full_name']}")
        print(f"Username : {result['username']}")
    else:
        print("Login failed. Check credentials.")
