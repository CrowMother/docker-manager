
import sqlite3
import argparse
from werkzeug.security import generate_password_hash

DB_PATH = "users.db"

def create_user(username, password, role):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    hashed_pw = generate_password_hash(password)
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_pw, role))
        conn.commit()
        print(f"User '{username}' created with role '{role}'.")
    except sqlite3.IntegrityError:
        print(f"User '{username}' already exists.")
    conn.close()

def add_permission(username, container_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    if not row:
        print(f"User '{username}' does not exist.")
        return
    user_id = row[0]
    cursor.execute("INSERT INTO permissions (user_id, container_name) VALUES (?, ?)", (user_id, container_name))
    conn.commit()
    conn.close()
    print(f"Granted access to container '{container_name}' for user '{username}'.")

def list_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Username: {row[1]}, Role: {row[2]}")
    conn.close()

def list_permissions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.username, p.container_name
        FROM permissions p
        JOIN users u ON u.id = p.user_id
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(f"User: {row[0]}, Container: {row[1]}")
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="User/Permission Manager for Docker Manager")
    subparsers = parser.add_subparsers(dest="command")

    user_parser = subparsers.add_parser("add-user")
    user_parser.add_argument("username")
    user_parser.add_argument("password")
    user_parser.add_argument("--role", default="user")

    perm_parser = subparsers.add_parser("add-permission")
    perm_parser.add_argument("username")
    perm_parser.add_argument("container")

    list_users_parser = subparsers.add_parser("list-users")
    list_perms_parser = subparsers.add_parser("list-perms")

    args = parser.parse_args()

    if args.command == "add-user":
        create_user(args.username, args.password, args.role)
    elif args.command == "add-permission":
        add_permission(args.username, args.container)
    elif args.command == "list-users":
        list_users()
    elif args.command == "list-perms":
        list_permissions()
    else:
        parser.print_help()
