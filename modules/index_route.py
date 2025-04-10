
from flask import render_template, session
import docker
from modules.auth import login_required

client = docker.from_env()

def register_index_route(app):

    @app.route("/", methods=["GET"])
    @login_required
    def index():
        containers = client.containers.list(all=True)
        username = session.get("username")
        is_admin = session.get("role") == "admin"

        container_info = []

        for container in containers:
            labels = container.attrs['Config'].get('Labels', {})
            owners = labels.get("owner", "")
            owner_list = [o.strip() for o in owners.split(",")]

            if is_admin or username in owner_list:
                env_list = container.attrs['Config']['Env']
                env_dict = dict(item.split("=", 1) for item in env_list if "=" in item)
                container_info.append({
                    "id": container.id,
                    "name": container.name,
                    "status": container.status,
                    "env_vars": env_dict
                })

        return render_template("index.html", containers=container_info)
