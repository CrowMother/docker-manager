
import sqlite3
from functools import wraps
from flask import session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import docker

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def verify_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return check_password_hash(row[0], password)
    return False

def get_user_containers(username):
    client = docker.from_env()
    containers = client.containers.list(all=True)
    visible = []

    for container in containers:
        labels = container.labels or {}
        owners = labels.get("permissions.owner", "")
        if not owners:
            continue
        owner_list = [u.strip() for u in owners.split(",")]
        if username in owner_list or session.get("role") == "admin":
            visible.append(container.name)

    return visible
def get_user_role(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def requires_role(role):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get("role") != role:
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper
