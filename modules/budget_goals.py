"""
BUDGET GOALS MODULE
===================
This module handles all budget goal operations.
Users can set monthly spending limits for each category.
The system tracks actual spending vs set goals and raises alerts.

Functions:
- set_budget_goal()         : Sets or updates a budget goal
- get_budget_goals()        : Fetches all goals for a user
- get_goal_by_category()    : Fetches goal for a specific category
- delete_budget_goal()      : Deletes a budget goal
- check_budget_status()     : Compares actual spending vs goals
- get_overspent_categories(): Returns categories where limit exceeded
- get_alert_messages()      : Returns alert messages for dashboard
"""

import sys
import os
import datetime
import pandas as pd

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_setup import get_connection


def set_budget_goal(user_id, category, amount, month=None):
    """
    Sets or updates a monthly budget goal for a specific category.
    If a goal already exists for that category and month, it updates it.
    Returns True if successful, False otherwise.

    Parameters:
        user_id  (int)   : ID of the logged-in user
        category (str)   : Expense category name
        amount   (float) : Maximum spending limit in rupees
        month    (str)   : Month in YYYY-MM format (default: current month)
    """
    try:
        # Default to current month if not provided
        if month is None:
            month = datetime.datetime.now().strftime("%Y-%m")

        conn   = get_connection()
        cursor = conn.cursor()

        # Check if goal already exists for this category and month
        cursor.execute("""
            SELECT id FROM budgets
            WHERE user_id = ? AND category = ? AND month = ?
        """, (user_id, category, month))

        existing = cursor.fetchone()

        if existing:
            # Update existing goal
            cursor.execute("""
                UPDATE budgets SET amount = ?
                WHERE user_id = ? AND category = ? AND month = ?
            """, (amount, user_id, category, month))
        else:
            # Insert new goal
            cursor.execute("""
                INSERT INTO budgets (user_id, category, amount, month)
                VALUES (?, ?, ?, ?)
            """, (user_id, category, amount, month))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"Error setting budget goal: {e}")
        return False


def get_budget_goals(user_id, month=None):
    """
    Fetches all budget goals for a user for a specific month.
    Returns a list of goal dictionaries.

    Parameters:
        user_id (int) : ID of the logged-in user
        month   (str) : Month in YYYY-MM format (default: current month)
    """
    if month is None:
        month = datetime.datetime.now().strftime("%Y-%m")

    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM budgets
        WHERE user_id = ? AND month = ?
        ORDER BY category ASC
    """, (user_id, month))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_goal_by_category(user_id, category, month=None):
    """
    Fetches the budget goal for a specific category and month.
    Returns goal dictionary or None if not set.

    Parameters:
        user_id  (int) : ID of the logged-in user
        category (str) : Category name
        month    (str) : Month in YYYY-MM format (default: current month)
    """
    if month is None:
        month = datetime.datetime.now().strftime("%Y-%m")

    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM budgets
        WHERE user_id = ? AND category = ? AND month = ?
    """, (user_id, category, month))

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def delete_budget_goal(user_id, category, month=None):
    """
    Deletes a budget goal for a specific category and month.
    Returns True if successful, False otherwise.

    Parameters:
        user_id  (int) : ID of the logged-in user
        category (str) : Category name
        month    (str) : Month in YYYY-MM format (default: current month)
    """
    try:
        if month is None:
            month = datetime.datetime.now().strftime("%Y-%m")

        conn   = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM budgets
            WHERE user_id = ? AND category = ? AND month = ?
        """, (user_id, category, month))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"Error deleting budget goal: {e}")
        return False


def check_budget_status(user_id, month=None):
    """
    Compares actual spending against budget goals for each category.
    Returns a list of status dictionaries with spending details.

    Parameters:
        user_id (int) : ID of the logged-in user
        month   (str) : Month in YYYY-MM format (default: current month)

    Returns list of:
        {
            category    : category name
            goal        : budget limit set by user
            spent       : actual amount spent
            remaining   : amount remaining in budget
            percentage  : percentage of budget used
            status      : "Safe" / "Warning" / "Exceeded"
        }
    """
    if month is None:
        month = datetime.datetime.now().strftime("%Y-%m")

    # Import here to avoid circular imports
    from modules.expense_manager import get_expenses_by_month

    # Fetch all goals and expenses for the month
    goals    = get_budget_goals(user_id, month)
    expenses = get_expenses_by_month(user_id, month)

    if not goals:
        return []

    # Calculate actual spending per category using Pandas
    status_list = []

    if expenses:
        df            = pd.DataFrame(expenses)
        category_spent = df.groupby("category")["amount"].sum().to_dict()
    else:
        category_spent = {}

    for goal in goals:
        category   = goal["category"]
        goal_amt   = goal["amount"]
        spent      = category_spent.get(category, 0.0)
        remaining  = goal_amt - spent
        percentage = (spent / goal_amt * 100) if goal_amt > 0 else 0

        # Determine status based on percentage used
        if percentage >= 100:
            status = "Exceeded"     # Budget limit crossed
        elif percentage >= 80:
            status = "Warning"      # 80% or more used
        else:
            status = "Safe"         # Under control

        status_list.append({
            "category"   : category,
            "goal"       : round(goal_amt, 2),
            "spent"      : round(spent, 2),
            "remaining"  : round(remaining, 2),
            "percentage" : round(percentage, 1),
            "status"     : status,
        })

    return status_list


def get_overspent_categories(user_id, month=None):
    """
    Returns only the categories where spending has exceeded the goal.
    Used for sending alerts to the user.

    Parameters:
        user_id (int) : ID of the logged-in user
        month   (str) : Month in YYYY-MM format (default: current month)
    """
    all_status = check_budget_status(user_id, month)
    return [s for s in all_status if s["status"] == "Exceeded"]


def get_alert_messages(user_id, month=None):
    """
    Generates alert messages based on budget status.
    Returns a list of alert message strings for dashboard display.

    Parameters:
        user_id (int) : ID of the logged-in user
        month   (str) : Month in YYYY-MM format (default: current month)
    """
    all_status = check_budget_status(user_id, month)
    messages   = []

    for s in all_status:
        if s["status"] == "Exceeded":
            messages.append(
                f"ALERT: {s['category']} budget exceeded! "
                f"Spent Rs.{s['spent']} of Rs.{s['goal']} goal."
            )
        elif s["status"] == "Warning":
            messages.append(
                f"WARNING: {s['category']} budget is {s['percentage']}% used. "
                f"Only Rs.{s['remaining']} remaining."
            )

    return messages


# ── Test budget goals directly ─────────────────────────────
if __name__ == "__main__":
    print("Testing Budget Goals Module...")

    # Set sample budget goals for user ID 1
    goals = [
        ("Food", 3000),
        ("Transport", 1500),
        ("Shopping", 2000),
        ("Bills", 2500),
    ]

    for category, amount in goals:
        result = set_budget_goal(1, category, amount)
        print(f"Set goal for {category}: Rs.{amount} -> {'Success' if result else 'Failed'}")

    # Check budget status
    print("\nBudget Status:")
    status = check_budget_status(1)
    for s in status:
        print(f"  {s['category']:<15} Goal: Rs.{s['goal']:<8} "
              f"Spent: Rs.{s['spent']:<8} Status: {s['status']}")

    # Get alert messages
    print("\nAlert Messages:")
    alerts = get_alert_messages(1)
    if alerts:
        for alert in alerts:
            print(f"  {alert}")
    else:
        print("  No alerts at this time.")
