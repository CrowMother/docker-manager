
from flask import Flask, render_template, request, redirect, session, url_for, flash
import docker
import os
import modules.util as util
from modules.auth import login_required, requires_role, init_db, verify_user, get_user_containers
from modules.admin_routes import register_admin_routes
from modules.auth import get_user_role
from modules.upload_route import register_upload_routes


app = Flask(__name__)
app.secret_key = util.get_secret("SECRET_KEY", ".env")

USERNAME = util.get_secret("USERNAME", ".env")
PASSWORD = util.get_secret("PASSWORD", ".env")

client = docker.from_env()

# Initialize admin routes
register_admin_routes(app)
# Initialize File Upload routes
register_upload_routes(app)
# Initialize database
init_db()

@app.route("/", methods=["GET"])
@login_required
def index():
    username = session.get("username")
    containers = client.containers.list(all=True)
    visible_containers = get_user_containers(username)

    container_info = []
    for container in containers:
        if visible_containers and container.name not in visible_containers:
            continue
        env_list = container.attrs['Config']['Env']
        env_dict = dict(item.split("=", 1) for item in env_list if "=" in item)
        container_info.append({
            "id": container.id,
            "name": container.name,
            "status": container.status,
            "env_vars": env_dict
        })

    return render_template("index.html", containers=container_info)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if verify_user(username, password):
            session["logged_in"] = True
            session["username"] = username

            # Get and store user role
            session["role"] = get_user_role(username)

            return redirect(url_for("index"))
        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/control/<container_id>/<action>")
@login_required
def control(container_id, action):
    container = client.containers.get(container_id)
    if action == "start":
        container.start()
    elif action == "stop":
        container.stop()
    elif action == "restart":
        container.restart()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
