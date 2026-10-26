"""
DATABASE SETUP MODULE
=====================
This file creates the SQLite database and all required tables.
Run this file once — the database will be automatically ready.

Tables:
- users     → stores login credentials
- expenses  → stores all expense records
- budgets   → stores monthly budget goals
"""

import sqlite3  # Built-in Python library for database operations
import os       # For handling file paths
import bcrypt   # For password encryption

# ── Database file path ─────────────────────────────────────
# This file will be created inside SmartBudgetTool/database/ folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "budget.db")


def get_connection():
    """
    Creates and returns a connection to the database.
    Call this function every time database access is required.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Returns results in dictionary format
    return conn


def create_tables():
    """
    Creates all required tables if they do not already exist.
    IF NOT EXISTS ensures tables are not recreated on every run.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ── USERS TABLE ────────────────────────────────────────
    # Stores user login credentials and profile information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            full_name   TEXT,
            created_at  TEXT    DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # ── EXPENSES TABLE ─────────────────────────────────────
    # Stores all expense records entered by users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            description TEXT,
            date        TEXT    NOT NULL,
            payment     TEXT    DEFAULT 'Cash',
            created_at  TEXT    DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── BUDGETS TABLE ──────────────────────────────────────
    # Stores monthly budget goals set by users for each category
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            category    TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            month       TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()   # Save all changes to the database
    conn.close()    # Close the database connection
    print("All tables created successfully!")


def create_default_users():
    """
    Creates a default admin user if no users exist in the database.
    Default credentials — username: admin | password: Admin@123
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check if any users already exist in the database
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    if count == 0:
        # Encrypt the password using bcrypt before storing
        # bcrypt converts plain text password into a secure hash
        password = "Admin@123"
        hashed = bcrypt.hashpw(
            password.encode('utf-8'),   # Convert string to bytes
            bcrypt.gensalt()            # Generate a random salt value
        )

        # Insert the default admin user into the database
        cursor.execute("""
            INSERT INTO users (username, password, full_name)
            VALUES (?, ?, ?)
        """, ("admin", hashed.decode('utf-8'), "Arpit Nigam"))

        conn.commit()
        print("Default user created successfully!")
        print("   Username : admin")
        print("   Password : Admin@123")
    else:
        print("Users already exist in the database.")

    conn.close()


def verify_password(plain_password, hashed_password):
    """
    Verifies the user password during login.
    plain_password  — password entered by the user
    hashed_password — encrypted password stored in the database
    Returns True if passwords match, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def initialize_database():
    """
    Initializes the complete database setup in a single function call.
    This function is called from main.py when the application starts.
    """
    print("Initializing database...")
    create_tables()
    create_default_users()
    print("Database is ready!\n")


# ── Run directly for testing purposes ─────────────────────
if __name__ == "__main__":
    initialize_database()
