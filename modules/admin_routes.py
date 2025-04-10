
from flask import render_template, request, redirect, url_for, flash
from modules.auth import requires_role
import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = "users.db"

def register_admin_routes(app):

    @app.route("/admin")
    @requires_role("admin")
    def admin_panel():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        cursor.execute("""
            SELECT u.username, p.container_name
            FROM permissions p
            JOIN users u ON u.id = p.user_id
        """)
        permissions = cursor.fetchall()
        conn.close()
        return render_template("admin.html", users=users, permissions=permissions)

    @app.route("/admin/create-user", methods=["POST"])
    @requires_role("admin")
    def create_user():
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        hashed_pw = generate_password_hash(password)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_pw, role))
            conn.commit()
            flash("User created successfully.")
        except sqlite3.IntegrityError:
            flash("Username already exists.")
        conn.close()
        return redirect(url_for("admin_panel"))

    @app.route("/admin/assign-container", methods=["POST"])
    @requires_role("admin")
    def assign_container():
        username = request.form["username"]
        container = request.form["container"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=?", (username,))
        row = cursor.fetchone()
        if not row:
            flash("User not found.")
            return redirect(url_for("admin_panel"))

        user_id = row[0]
        cursor.execute("INSERT INTO permissions (user_id, container_name) VALUES (?, ?)", (user_id, container))
        conn.commit()
        conn.close()
        flash("Permission added.")
        return redirect(url_for("admin_panel"))
    
    @app.route("/admin/edit-user/<int:user_id>", methods=["POST"])
    @requires_role("admin")
    def edit_user(user_id):
        username = request.form["username"]
        role = request.form["role"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET username = ?, role = ? WHERE id = ?", (username, role.lower(), user_id))
        conn.commit()
        conn.close()
        flash("User updated successfully.")
        return redirect(url_for("admin_panel"))

    @app.route("/admin/delete-user/<int:user_id>")
    @requires_role("admin")
    def delete_user(user_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        flash("User deleted.")
        return redirect(url_for("admin_panel"))
