"""
EXPORT MANAGER MODULE
=====================
This module handles exporting expense data in multiple formats.
All exported files are saved in the exports/ folder.

Functions:
- export_to_csv()     : Exports all expenses to a CSV file
- export_to_json()    : Exports all expenses to a JSON file
- export_to_txt()     : Exports a plain text summary report
- export_to_pdf()     : Exports a formatted PDF report
- get_export_folder() : Returns the path to the exports folder
"""

import sys
import os
import json
import csv
import datetime
import pandas as pd

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.expense_manager import get_all_expenses, get_category_totals, get_monthly_totals


def get_export_folder():
    """
    Returns the path to the exports folder.
    Creates the folder if it does not already exist.
    """
    base_dir     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    export_folder = os.path.join(base_dir, "exports")
    os.makedirs(export_folder, exist_ok=True)
    return export_folder


def export_to_csv(user_id, username):
    """
    Exports all expense records to a CSV file.
    File is saved in exports/ folder with date in filename.
    Returns the file path if successful, None otherwise.

    Parameters:
        user_id  (int) : ID of the logged-in user
        username (str) : Username for filename
    """
    try:
        expenses = get_all_expenses(user_id)

        if not expenses:
            return None

        # Generate filename with current date
        date     = datetime.date.today().strftime("%Y%m%d")
        filename = f"expenses_{username}_{date}.csv"
        filepath = os.path.join(get_export_folder(), filename)

        # Define CSV columns
        fields = ["id", "amount", "category", "description", "date", "payment", "created_at"]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for expense in expenses:
                writer.writerow({field: expense.get(field, "") for field in fields})

        return filepath

    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return None


def export_to_json(user_id, username):
    """
    Exports all expense records to a JSON file.
    File is saved in exports/ folder with date in filename.
    Returns the file path if successful, None otherwise.

    Parameters:
        user_id  (int) : ID of the logged-in user
        username (str) : Username for filename
    """
    try:
        expenses = get_all_expenses(user_id)

        if not expenses:
            return None

        date     = datetime.date.today().strftime("%Y%m%d")
        filename = f"expenses_{username}_{date}.json"
        filepath = os.path.join(get_export_folder(), filename)

        export_data = {
            "exported_by"  : username,
            "exported_at"  : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_records": len(expenses),
            "expenses"     : expenses
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, default=str)

        return filepath

    except Exception as e:
        print(f"Error exporting to JSON: {e}")
        return None


def export_to_txt(user_id, username):
    """
    Exports a plain text summary report of all expenses.
    Includes category totals, monthly totals and overall summary.
    Returns the file path if successful, None otherwise.

    Parameters:
        user_id  (int) : ID of the logged-in user
        username (str) : Username for filename
    """
    try:
        expenses        = get_all_expenses(user_id)
        category_totals = get_category_totals(user_id)
        monthly_totals  = get_monthly_totals(user_id)

        if not expenses:
            return None

        total_spent = sum(e["amount"] for e in expenses)
        date        = datetime.date.today().strftime("%Y%m%d")
        filename    = f"summary_{username}_{date}.txt"
        filepath    = os.path.join(get_export_folder(), filename)

        with open(filepath, "w", encoding="utf-8") as f:
            # Header
            f.write("=" * 60 + "\n")
            f.write("     SMART BUDGET ANALYSIS TOOL — EXPENSE REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"  Generated For : {username}\n")
            f.write(f"  Generated On  : {datetime.datetime.now().strftime('%d %b %Y %H:%M:%S')}\n")
            f.write(f"  Developed By  : Arpit Nigam\n")
            f.write("=" * 60 + "\n\n")

            # Overall Summary
            f.write("OVERALL SUMMARY\n")
            f.write("-" * 40 + "\n")
            f.write(f"  Total Expenses   : Rs. {total_spent:,.2f}\n")
            f.write(f"  Total Records    : {len(expenses)}\n")
            avg = total_spent / len(expenses) if expenses else 0
            f.write(f"  Average Expense  : Rs. {avg:,.2f}\n\n")

            # Category Wise Totals
            f.write("SPENDING BY CATEGORY\n")
            f.write("-" * 40 + "\n")
            for category, amount in sorted(category_totals.items(), key=lambda x: -x[1]):
                pct = (amount / total_spent * 100) if total_spent > 0 else 0
                f.write(f"  {category:<18} Rs. {amount:>10,.2f}  ({pct:.1f}%)\n")

            # Monthly Wise Totals
            f.write("\nSPENDING BY MONTH\n")
            f.write("-" * 40 + "\n")
            for month, amount in sorted(monthly_totals.items()):
                f.write(f"  {month}        Rs. {amount:>10,.2f}\n")

            # All Expense Records
            f.write("\nALL EXPENSE RECORDS\n")
            f.write("-" * 60 + "\n")
            f.write(f"  {'Date':<12} {'Category':<15} {'Amount':>10}  {'Description'}\n")
            f.write("-" * 60 + "\n")
            for e in expenses:
                f.write(
                    f"  {e['date']:<12} {e['category']:<15} "
                    f"Rs.{e['amount']:>8,.2f}  {e['description']}\n"
                )

            # Footer
            f.write("\n" + "=" * 60 + "\n")
            f.write("  Smart Budget Analysis Tool with Predictive Analytics\n")
            f.write("  Developed by Arpit Nigam\n")
            f.write("=" * 60 + "\n")

        return filepath

    except Exception as e:
        print(f"Error exporting to TXT: {e}")
        return None


def export_to_pdf(user_id, username):
    """
    Exports a formatted PDF report of all expenses.
    Uses fpdf2 library for PDF generation.
    Returns the file path if successful, None otherwise.

    Parameters:
        user_id  (int) : ID of the logged-in user
        username (str) : Username for filename
    """
    try:
        from fpdf import FPDF
    except ImportError:
        print("fpdf2 not installed. Run: pip install fpdf2")
        return None

    try:
        expenses        = get_all_expenses(user_id)
        category_totals = get_category_totals(user_id)

        if not expenses:
            return None

        total_spent = sum(e["amount"] for e in expenses)
        date        = datetime.date.today().strftime("%Y%m%d")
        filename    = f"report_{username}_{date}.pdf"
        filepath    = os.path.join(get_export_folder(), filename)

        # Initialize PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Title
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Smart Budget Analysis Tool", ln=True, align="C")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, "Expense Report", ln=True, align="C")
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 6, f"Generated for: {username}  |  Date: {datetime.date.today()}", ln=True, align="C")
        pdf.cell(0, 6, "Developed by: Arpit Nigam", ln=True, align="C")
        pdf.ln(5)

        # Summary Section
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Overall Summary", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, f"Total Spent   : Rs. {total_spent:,.2f}", ln=True)
        pdf.cell(0, 7, f"Total Records : {len(expenses)}", ln=True)
        pdf.ln(4)

        # Category Totals Table
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Spending by Category", ln=True)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(90, 7, "Category", border=1)
        pdf.cell(50, 7, "Amount (Rs.)", border=1)
        pdf.cell(50, 7, "Percentage", border=1, ln=True)

        pdf.set_font("Helvetica", "", 10)
        for category, amount in sorted(category_totals.items(), key=lambda x: -x[1]):
            pct = (amount / total_spent * 100) if total_spent > 0 else 0
            pdf.cell(90, 7, category, border=1)
            pdf.cell(50, 7, f"Rs. {amount:,.2f}", border=1)
            pdf.cell(50, 7, f"{pct:.1f}%", border=1, ln=True)

        pdf.ln(5)

        # Expense Records Table
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "All Expense Records", ln=True)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(28, 7, "Date", border=1)
        pdf.cell(38, 7, "Category", border=1)
        pdf.cell(30, 7, "Amount", border=1)
        pdf.cell(30, 7, "Payment", border=1)
        pdf.cell(64, 7, "Description", border=1, ln=True)

        pdf.set_font("Helvetica", "", 9)
        for e in expenses:
            pdf.cell(28, 7, str(e["date"]), border=1)
            pdf.cell(38, 7, e["category"], border=1)
            pdf.cell(30, 7, f"Rs.{e['amount']:,.2f}", border=1)
            pdf.cell(30, 7, e.get("payment", "Cash"), border=1)
            desc = str(e["description"])[:28]
            pdf.cell(64, 7, desc, border=1, ln=True)

        # Footer
        pdf.ln(5)
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(0, 6, "Smart Budget Analysis Tool with Predictive Analytics | Developed by Arpit Nigam", align="C")

        pdf.output(filepath)
        return filepath

    except Exception as e:
        print(f"Error exporting to PDF: {e}")
        return None


# ── Test export functions directly ────────────────────────
if __name__ == "__main__":
    print("Testing Export Manager...")

    user_id  = 1
    username = "admin"

    # Test CSV export
    csv_path = export_to_csv(user_id, username)
    print(f"CSV Export  : {'Success -> ' + csv_path if csv_path else 'Failed'}")

    # Test JSON export
    json_path = export_to_json(user_id, username)
    print(f"JSON Export : {'Success -> ' + json_path if json_path else 'Failed'}")

    # Test TXT export
    txt_path = export_to_txt(user_id, username)
    print(f"TXT Export  : {'Success -> ' + txt_path if txt_path else 'Failed'}")

    # Test PDF export
    pdf_path = export_to_pdf(user_id, username)
    print(f"PDF Export  : {'Success -> ' + pdf_path if pdf_path else 'Failed (install fpdf2)'}")
