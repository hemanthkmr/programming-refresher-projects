"""Personal Expense Tracker - Course-End Project 1 (Programming Refresher).

Log daily expenses, categorise them, track spending against a monthly
budget, and save/load everything to CSV files so the user can continue
where they left off.
"""

import csv
import os
from datetime import datetime

EXPENSES_FILE = "expenses.csv"
BUDGET_FILE = "budget.txt"
FIELDS = ["date", "category", "amount", "description"]

expenses = []
monthly_budget = 0.0


def is_valid_date(text):
    try:
        datetime.strptime(text, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_complete(expense):
    """An expense is complete when every required field has a value."""
    for field in FIELDS:
        value = expense.get(field)
        if value is None or str(value).strip() == "":
            return False
    return True


# 1. Add an expense
def add_expense():
    while True:
        date = input("Date (YYYY-MM-DD): ").strip()
        if is_valid_date(date):
            break
        print("Invalid date. Please use the format YYYY-MM-DD, e.g. 2024-09-18.")

    category = ""
    while not category:
        category = input("Category (e.g. Food, Travel): ").strip().title()
        if not category:
            print("Category cannot be empty.")

    while True:
        try:
            amount = float(input("Amount spent: ").strip())
            if amount <= 0:
                print("Amount must be greater than zero.")
                continue
            break
        except ValueError:
            print("Please enter a number, e.g. 15.50.")

    description = ""
    while not description:
        description = input("Short description: ").strip()
        if not description:
            print("Description cannot be empty.")

    expense = {"date": date, "category": category,
               "amount": round(amount, 2), "description": description}
    expenses.append(expense)
    print(f"Added: {expense}")


# 2. View expenses
def view_expenses():
    if not expenses:
        print("No expenses recorded yet.")
        return
    print(f"\n{'#':>3}  {'Date':<10}  {'Category':<12}  {'Amount':>10}  Description")
    print("-" * 65)
    shown = 0
    for number, expense in enumerate(expenses, start=1):
        if not is_complete(expense):
            print(f"{number:>3}  Skipped: entry is incomplete -> {expense}")
            continue
        print(f"{number:>3}  {expense['date']:<10}  {expense['category']:<12}  "
              f"{float(expense['amount']):>10.2f}  {expense['description']}")
        shown += 1
    print("-" * 65)
    print(f"{shown} valid expense(s) shown.")
    summarise_by_category()


def summarise_by_category():
    totals = {}
    for expense in expenses:
        if is_complete(expense):
            totals[expense["category"]] = totals.get(expense["category"], 0) + float(expense["amount"])
    if totals:
        print("Spending by category:")
        for category, total in sorted(totals.items()):
            print(f"  {category:<12} {total:>10.2f}")


# 3. Set and track the budget
def set_budget():
    global monthly_budget
    while True:
        try:
            value = float(input("Enter your total budget for the month: ").strip())
            if value < 0:
                print("Budget cannot be negative.")
                continue
            monthly_budget = round(value, 2)
            print(f"Monthly budget set to {monthly_budget:.2f}")
            return
        except ValueError:
            print("Please enter a number.")


def total_expenses():
    return sum(float(e["amount"]) for e in expenses if is_complete(e))


def track_budget():
    if monthly_budget <= 0:
        print("No monthly budget set yet.")
        set_budget()
    spent = total_expenses()
    print(f"Total spent so far: {spent:.2f} | Monthly budget: {monthly_budget:.2f}")
    if spent > monthly_budget:
        print(f"You have exceeded your budget! (over by {spent - monthly_budget:.2f})")
    else:
        print(f"You have {monthly_budget - spent:.2f} left for the month")


# 4. Save and load expenses
def save_expenses():
    with open(EXPENSES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(expenses)
    with open(BUDGET_FILE, "w", encoding="utf-8") as f:
        f.write(str(monthly_budget))
    print(f"Saved {len(expenses)} expense(s) to {EXPENSES_FILE}")


def load_expenses():
    global monthly_budget
    if os.path.exists(EXPENSES_FILE):
        with open(EXPENSES_FILE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    row["amount"] = float(row["amount"]) if row.get("amount") else None
                except ValueError:
                    row["amount"] = None
                expenses.append(row)
        print(f"Loaded {len(expenses)} expense(s) from {EXPENSES_FILE}")
    if os.path.exists(BUDGET_FILE):
        try:
            with open(BUDGET_FILE, encoding="utf-8") as f:
                monthly_budget = float(f.read().strip() or 0)
        except ValueError:
            monthly_budget = 0.0


# 5. Interactive menu
def show_menu():
    print("\n===== Personal Expense Tracker =====")
    print("1. Add expense")
    print("2. View expenses")
    print("3. Track budget")
    print("4. Save expenses")
    print("5. Exit")


def main():
    load_expenses()
    while True:
        show_menu()
        choice = input("Choose an option (1-5): ").strip()
        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            track_budget()
        elif choice == "4":
            save_expenses()
        elif choice == "5":
            save_expenses()
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")


if __name__ == "__main__":
    main()
