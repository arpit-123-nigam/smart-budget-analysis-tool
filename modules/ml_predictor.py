"""
ML PREDICTIONS MODULE
=====================
This module handles machine learning based expense predictions.
It uses Linear Regression from Scikit-learn to predict future
monthly spending based on historical expense data.

Functions:
- prepare_training_data()   : Prepares data for ML model training
- train_model()             : Trains the Linear Regression model
- predict_next_month()      : Predicts spending for next month
- predict_next_3_months()   : Predicts spending for next 3 months
- get_spending_trend()      : Returns spending trend (increasing/decreasing)
- get_prediction_insights() : Returns smart AI insights for dashboard
"""

import sys
import os
import datetime
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.expense_manager import get_all_expenses, get_monthly_totals


def prepare_training_data(user_id):
    """
    Prepares historical expense data for ML model training.
    Converts monthly totals into a numeric format suitable for regression.

    Parameters:
        user_id (int) : ID of the logged-in user

    Returns:
        X (numpy array) : Month numbers as input features
        y (numpy array) : Total spending amounts as target values
        months (list)   : List of month strings in YYYY-MM format
    """
    monthly_totals = get_monthly_totals(user_id)

    if len(monthly_totals) < 2:
        return None, None, None

    # Sort months in ascending order
    sorted_months = sorted(monthly_totals.keys())
    amounts       = [monthly_totals[m] for m in sorted_months]

    # Convert months to numeric values (1, 2, 3, ...) for regression
    X = np.array(range(1, len(sorted_months) + 1)).reshape(-1, 1)
    y = np.array(amounts)

    return X, y, sorted_months


def train_model(user_id):
    """
    Trains a Linear Regression model on historical expense data.
    Returns the trained model and training data, or None if insufficient data.

    Parameters:
        user_id (int) : ID of the logged-in user
    """
    X, y, months = prepare_training_data(user_id)

    if X is None:
        return None, None, None

    # Initialize and train the Linear Regression model
    model = LinearRegression()
    model.fit(X, y)

    return model, X, y


def predict_next_month(user_id):
    """
    Predicts the total spending for the next month.
    Returns predicted amount as float, or None if insufficient data.

    Parameters:
        user_id (int) : ID of the logged-in user
    """
    model, X, y = train_model(user_id)

    if model is None:
        return None

    # Predict for the next month number
    next_month_num = np.array([[len(X) + 1]])
    prediction     = model.predict(next_month_num)[0]

    # Ensure prediction is not negative
    return round(max(prediction, 0), 2)


def predict_next_3_months(user_id):
    """
    Predicts total spending for the next 3 months.
    Returns a dictionary with month names and predicted amounts.

    Parameters:
        user_id (int) : ID of the logged-in user
    """
    model, X, y = train_model(user_id)

    if model is None:
        return {}

    predictions  = {}
    current_len  = len(X)

    # Get current date to calculate future month names
    current_date = datetime.datetime.now()

    for i in range(1, 4):
        # Calculate future month
        future_month_num  = current_len + i
        future_date       = current_date + datetime.timedelta(days=30 * i)
        future_month_name = future_date.strftime("%b %Y")

        # Predict spending for that month
        prediction = model.predict(np.array([[future_month_num]]))[0]
        predictions[future_month_name] = round(max(prediction, 0), 2)

    return predictions


def get_spending_trend(user_id):
    """
    Analyzes the spending trend based on last 2 months of data.
    Returns "Increasing", "Decreasing", or "Stable".

    Parameters:
        user_id (int) : ID of the logged-in user
    """
    model, X, y = train_model(user_id)

    if model is None:
        return "Insufficient Data"

    # The slope of the regression line indicates trend direction
    slope = model.coef_[0]

    if slope > 50:
        return "Increasing"
    elif slope < -50:
        return "Decreasing"
    else:
        return "Stable"


def get_category_prediction(user_id):
    """
    Predicts next month spending for each expense category separately.
    Returns a dictionary with category names and predicted amounts.

    Parameters:
        user_id (int) : ID of the logged-in user
    """
    expenses = get_all_expenses(user_id)

    if not expenses or len(expenses) < 3:
        return {}

    df = pd.DataFrame(expenses)
    df["month"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m")

    predictions = {}
    categories  = df["category"].unique()

    for category in categories:
        cat_df         = df[df["category"] == category]
        monthly_totals = cat_df.groupby("month")["amount"].sum()

        # Need at least 2 months of data to predict
        if len(monthly_totals) < 2:
            continue

        # Prepare data for this category
        X = np.array(range(1, len(monthly_totals) + 1)).reshape(-1, 1)
        y = monthly_totals.values

        # Train model for this category
        model = LinearRegression()
        model.fit(X, y)

        # Predict next month
        next_val = model.predict(np.array([[len(X) + 1]]))[0]
        predictions[category] = round(max(next_val, 0), 2)

    return predictions


def get_prediction_insights(user_id):
    """
    Generates smart AI-based insights about spending patterns.
    Returns a list of insight strings for dashboard display.

    Parameters:
        user_id (int) : ID of the logged-in user
    """
    insights       = []
    monthly_totals = get_monthly_totals(user_id)

    if len(monthly_totals) < 2:
        insights.append("Add more expense data to get AI insights.")
        return insights

    # Sort months
    sorted_months = sorted(monthly_totals.keys())
    amounts       = [monthly_totals[m] for m in sorted_months]

    # Compare last two months
    if len(amounts) >= 2:
        last_month    = amounts[-2]
        current_month = amounts[-1]
        diff          = current_month - last_month
        diff_pct      = (diff / last_month * 100) if last_month > 0 else 0

        if diff_pct > 20:
            insights.append(
                f"Your spending increased by {abs(diff_pct):.1f}% "
                f"compared to last month."
            )
        elif diff_pct < -20:
            insights.append(
                f"Great! Your spending decreased by {abs(diff_pct):.1f}% "
                f"compared to last month."
            )
        else:
            insights.append("Your spending is stable compared to last month.")

    # Next month prediction insight
    next_pred = predict_next_month(user_id)
    if next_pred:
        insights.append(
            f"AI Prediction: You may spend approximately "
            f"Rs. {next_pred:,.0f} next month."
        )

    # Spending trend insight
    trend = get_spending_trend(user_id)
    if trend == "Increasing":
        insights.append(
            "Spending trend is Increasing. "
            "Consider reviewing your budget goals."
        )
    elif trend == "Decreasing":
        insights.append(
            "Spending trend is Decreasing. "
            "You are managing your budget well!"
        )

    # Category prediction insight
    cat_predictions = get_category_prediction(user_id)
    if cat_predictions:
        top_cat = max(cat_predictions, key=cat_predictions.get)
        insights.append(
            f"Highest predicted spend next month: "
            f"{top_cat} — Rs. {cat_predictions[top_cat]:,.0f}"
        )

    return insights


# ── Test ML predictions directly ──────────────────────────
if __name__ == "__main__":
    print("Testing ML Predictions Module...")
    print("Note: Accurate predictions need at least 2 months of data.\n")

    user_id = 1

    # Test next month prediction
    prediction = predict_next_month(user_id)
    if prediction:
        print(f"Next month predicted spending : Rs. {prediction:,.2f}")
    else:
        print("Not enough data for prediction. Add more expenses.")

    # Test 3 month prediction
    three_month = predict_next_3_months(user_id)
    if three_month:
        print("\n3 Month Predictions:")
        for month, amount in three_month.items():
            print(f"  {month} : Rs. {amount:,.2f}")

    # Test spending trend
    trend = get_spending_trend(user_id)
    print(f"\nSpending Trend : {trend}")

    # Test insights
    print("\nAI Insights:")
    insights = get_prediction_insights(user_id)
    for insight in insights:
        print(f"  - {insight}")
