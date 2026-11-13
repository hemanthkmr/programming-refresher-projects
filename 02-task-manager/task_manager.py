"""Task Manager with User Authentication - Course-End Project 2 (Programming Refresher).

Users register and log in; passwords are stored only as salted hashes.
Each user's tasks are kept in a separate file that only they can reach
through the menu after logging in.
"""

import getpass
import hashlib
import json
import os
import secrets
import sys

USERS_FILE = "users.json"
TASKS_DIR = "tasks"


# ---------- file helpers ----------
def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def read_password(prompt):
    # getpass hides typing in a real terminal; fall back to input when piped (tests)
    return getpass.getpass(prompt) if sys.stdin.isatty() else input(prompt)


# ---------- 1. user authentication ----------
def hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100_000).hex()


def register():
    users = load_json(USERS_FILE, {})
    username = input("Choose a username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return
    if username.lower() in (u.lower() for u in users):
        print("That username is already taken. Please choose another.")
        return
    password = read_password("Choose a password (min 4 characters): ")
    if len(password) < 4:
        print("Password too short.")
        return
    if read_password("Confirm password: ") != password:
        print("Passwords do not match.")
        return
    salt = secrets.token_hex(16)
    users[username] = {"salt": salt, "password_hash": hash_password(password, salt)}
    save_json(USERS_FILE, users)
    print(f"User '{username}' registered successfully. You can now log in.")


def login():
    users = load_json(USERS_FILE, {})
    username = input("Username: ").strip()
    password = read_password("Password: ")
    record = users.get(username)
    if record and secrets.compare_digest(record["password_hash"], hash_password(password, record["salt"])):
        print(f"Welcome, {username}!")
        return username
    print("Invalid username or password.")
    return None


# ---------- task storage (one file per user) ----------
def tasks_path(username):
    os.makedirs(TASKS_DIR, exist_ok=True)
    safe = "".join(c for c in username if c.isalnum() or c in "-_") or "user"
    return os.path.join(TASKS_DIR, f"{safe}_tasks.json")


def load_tasks(username):
    return load_json(tasks_path(username), [])


def save_tasks(username, tasks):
    save_json(tasks_path(username), tasks)


# ---------- 2-5. task operations ----------
def add_task(username):
    description = input("Task description: ").strip()
    if not description:
        print("Description cannot be empty.")
        return
    tasks = load_tasks(username)
    next_id = max((t["id"] for t in tasks), default=0) + 1
    tasks.append({"id": next_id, "description": description, "status": "Pending"})
    save_tasks(username, tasks)
    print(f"Task {next_id} added.")


def view_tasks(username):
    tasks = load_tasks(username)
    if not tasks:
        print("You have no tasks.")
        return
    print(f"\n{'ID':>3}  {'Status':<10}  Description")
    print("-" * 50)
    for t in tasks:
        print(f"{t['id']:>3}  {t['status']:<10}  {t['description']}")


def ask_task_id():
    try:
        return int(input("Enter task ID: ").strip())
    except ValueError:
        print("Task ID must be a number.")
        return None


def mark_completed(username):
    task_id = ask_task_id()
    if task_id is None:
        return
    tasks = load_tasks(username)
    for t in tasks:
        if t["id"] == task_id:
            t["status"] = "Completed"
            save_tasks(username, tasks)
            print(f"Task {task_id} marked as Completed.")
            return
    print(f"No task with ID {task_id}.")


def delete_task(username):
    task_id = ask_task_id()
    if task_id is None:
        return
    tasks = load_tasks(username)
    remaining = [t for t in tasks if t["id"] != task_id]
    if len(remaining) == len(tasks):
        print(f"No task with ID {task_id}.")
        return
    save_tasks(username, remaining)
    print(f"Task {task_id} deleted.")


# ---------- 6. menus ----------
def task_menu(username):
    actions = {"1": add_task, "2": view_tasks, "3": mark_completed, "4": delete_task}
    while True:
        print(f"\n===== Task Manager ({username}) =====")
        print("1. Add a Task")
        print("2. View Tasks")
        print("3. Mark a Task as Completed")
        print("4. Delete a Task")
        print("5. Logout")
        choice = input("Choose an option (1-5): ").strip()
        if choice == "5":
            print(f"Logged out. Goodbye, {username}!")
            return
        action = actions.get(choice)
        if action:
            action(username)
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")


def main():
    while True:
        print("\n===== Welcome =====")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option (1-3): ").strip()
        if choice == "1":
            register()
        elif choice == "2":
            user = login()
            if user:
                task_menu(user)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2 or 3.")


if __name__ == "__main__":
    main()
