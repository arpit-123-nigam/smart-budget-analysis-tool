"""
EXPENSE MANAGER MODULE
======================
This module handles all expense-related database operations.
Functions:
- add_expense()         : Adds a new expense record
- get_all_expenses()    : Fetches all expenses for a user
- get_expense_by_id()   : Fetches a single expense by ID
- update_expense()      : Updates an existing expense record
- delete_expense()      : Deletes an expense record
- get_expenses_by_category()  : Fetches expenses filtered by category
- get_expenses_by_month()     : Fetches expenses for a specific month
- get_category_totals()       : Returns total spending per category
- get_monthly_totals()        : Returns total spending per month
- get_dashboard_stats()       : Returns summary statistics for dashboard
"""

import sys
import os
import datetime
import pandas as pd

# Add parent directory to path for database import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_setup import get_connection

# Available expense categories
CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Health",
    "Education",
    "Entertainment",
    "Rent",
    "Other"
]

# Available payment methods
PAYMENT_METHODS = [
    "Cash",
    "UPI",
    "Card",
    "Net Banking",
    "Other"
]


def add_expense(user_id, amount, category, description, date, payment="Cash"):
    """
    Adds a new expense record to the database.
    Returns True if successful, False otherwise.

    Parameters:
        user_id     (int)   : ID of the logged-in user
        amount      (float) : Expense amount in rupees
        category    (str)   : Category of the expense
        description (str)   : Brief description of the expense
        date        (str)   : Date of expense in YYYY-MM-DD format
        payment     (str)   : Payment method used
    """
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO expenses (user_id, amount, category, description, date, payment)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, amount, category, description, date, payment))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"Error adding expense: {e}")
        return False


def get_all_expenses(user_id):
    """
    Fetches all expense records for a specific user.
    Returns a list of expense dictionaries ordered by date (latest first).

    Parameters:
        user_id (int) : ID of the logged-in user
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM expenses
        WHERE user_id = ?
        ORDER BY date DESC, created_at DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_expense_by_id(expense_id, user_id):
    """
    Fetches a single expense record by its ID.
    Returns expense dictionary or None if not found.

    Parameters:
        expense_id (int) : Unique ID of the expense
        user_id    (int) : ID of the logged-in user
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM expenses
        WHERE id = ? AND user_id = ?
    """, (expense_id, user_id))

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def update_expense(expense_id, user_id, amount, category, description, date, payment):
    """
    Updates an existing expense record in the database.
    Returns True if successful, False otherwise.

    Parameters:
        expense_id  (int)   : ID of the expense to update
        user_id     (int)   : ID of the logged-in user
        amount      (float) : Updated expense amount
        category    (str)   : Updated category
        description (str)   : Updated description
        date        (str)   : Updated date in YYYY-MM-DD format
        payment     (str)   : Updated payment method
    """
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE expenses
            SET amount = ?, category = ?, description = ?,
                date = ?, payment = ?
            WHERE id = ? AND user_id = ?
        """, (amount, category, description, date, payment, expense_id, user_id))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"Error updating expense: {e}")
        return False


def delete_expense(expense_id, user_id):
    """
    Deletes an expense record from the database.
    Returns True if successful, False otherwise.

    Parameters:
        expense_id (int) : ID of the expense to delete
        user_id    (int) : ID of the logged-in user
    """
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM expenses
            WHERE id = ? AND user_id = ?
        """, (expense_id, user_id))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"Error deleting expense: {e}")
        return False


def get_expenses_by_category(user_id, category):
    """
    Fetches all expenses for a specific category.
    Returns a list of expense dictionaries.

    Parameters:
        user_id  (int) : ID of the logged-in user
        category (str) : Category name to filter by
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM expenses
        WHERE user_id = ? AND category = ?
        ORDER BY date DESC
    """, (user_id, category))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_expenses_by_month(user_id, month):
    """
    Fetches all expenses for a specific month.
    Returns a list of expense dictionaries.

    Parameters:
        user_id (int) : ID of the logged-in user
        month   (str) : Month in YYYY-MM format (e.g. 2025-05)
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM expenses
        WHERE user_id = ? AND strftime('%Y-%m', date) = ?
        ORDER BY date DESC
    """, (user_id, month))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_category_totals(user_id):
    """
    Returns total amount spent per category for a user.
    Uses Pandas for data processing.
    Returns a dictionary {category: total_amount}.

    Parameters:
        user_id (int) : ID of the logged-in user
    """
    expenses = get_all_expenses(user_id)

    if not expenses:
        return {}

    # Load expenses into a Pandas DataFrame for easy analysis
    df = pd.DataFrame(expenses)

    # Group by category and sum the amounts
    category_totals = df.groupby("category")["amount"].sum().to_dict()

    return category_totals


def get_monthly_totals(user_id):
    """
    Returns total amount spent per month for a user.
    Uses Pandas for data processing.
    Returns a dictionary {YYYY-MM: total_amount}.

    Parameters:
        user_id (int) : ID of the logged-in user
    """
    expenses = get_all_expenses(user_id)

    if not expenses:
        return {}

    # Load into Pandas DataFrame
    df = pd.DataFrame(expenses)

    # Extract month from date column
    df["month"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m")

    # Group by month and sum amounts
    monthly_totals = df.groupby("month")["amount"].sum().to_dict()

    return monthly_totals


def get_dashboard_stats(user_id):
    """
    Returns summary statistics for the dashboard.
    Includes total spending, monthly spending, transaction count,
    average expense, and top spending category.

    Parameters:
        user_id (int) : ID of the logged-in user
    """
    expenses = get_all_expenses(user_id)

    if not expenses:
        return {
            "total_spent"      : 0,
            "month_spent"      : 0,
            "total_count"      : 0,
            "avg_expense"      : 0,
            "top_category"     : "N/A",
            "recent_expenses"  : [],
        }

    df = pd.DataFrame(expenses)

    # Total spending across all time
    total_spent = df["amount"].sum()

    # Total spending for current month only
    current_month = datetime.datetime.now().strftime("%Y-%m")
    df["month"]   = pd.to_datetime(df["date"]).dt.strftime("%Y-%m")
    month_spent   = df[df["month"] == current_month]["amount"].sum()

    # Total number of expense records
    total_count = len(df)

    # Average amount per expense
    avg_expense = df["amount"].mean()

    # Category with highest total spending
    top_category = df.groupby("category")["amount"].sum().idxmax()

    # 6 most recent expenses for dashboard display
    recent_expenses = expenses[:6]

    return {
        "total_spent"     : round(total_spent, 2),
        "month_spent"     : round(month_spent, 2),
        "total_count"     : total_count,
        "avg_expense"     : round(avg_expense, 2),
        "top_category"    : top_category,
        "recent_expenses" : recent_expenses,
    }


def search_expenses(user_id, query):
    """
    Searches expenses by description, category or amount.
    Returns a filtered list of expense dictionaries.

    Parameters:
        user_id (int) : ID of the logged-in user
        query   (str) : Search keyword entered by user
    """
    all_expenses = get_all_expenses(user_id)
    query        = query.lower().strip()

    filtered = [
        e for e in all_expenses
        if query in e["description"].lower()
        or query in e["category"].lower()
        or query in str(e["amount"])
    ]

    return filtered


# ── Test expense operations directly ──────────────────────
if __name__ == "__main__":
    print("Testing Expense Manager...")

    # Add a sample expense for user ID 1
    result = add_expense(
        user_id     = 1,
        amount      = 150.0,
        category    = "Food",
        description = "Lunch at canteen",
        date        = datetime.date.today().isoformat(),
        payment     = "Cash"
    )
    print(f"Add expense : {'Success' if result else 'Failed'}")

    # Fetch all expenses
    expenses = get_all_expenses(1)
    print(f"Total expenses found : {len(expenses)}")

    # Get dashboard statistics
    stats = get_dashboard_stats(1)
    print(f"Total spent    : Rs. {stats['total_spent']}")
    print(f"This month     : Rs. {stats['month_spent']}")
    print(f"Top category   : {stats['top_category']}")
