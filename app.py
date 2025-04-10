
from flask import Flask, render_template, request, redirect, session, url_for
import docker
from modules import util

# do proper imports for the bot framework library
app = Flask(__name__)
app.secret_key = util.get_secret("SECRET_KEY", ".env")  # Replace for production
USERNAME = util.get_secret("USERNAME", ".env") # Replace for production
PASSWORD = util.get_secret("PASSWORD", ".env") # Replace for production

client = docker.from_env()

@app.route("/", methods=["GET"])
def home():
    if "logged_in" not in session:
        return redirect(url_for("login"))
    containers = client.containers.list(all=True)
    container_info = []

    for container in containers:
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
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/control/<container_id>/<action>")
def control(container_id, action):
    if "logged_in" not in session:
        return redirect(url_for("login"))
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
