import docker
from flask import render_template, request, redirect, url_for, flash
from modules.auth import login_required

client = docker.from_env()

def register_manage_routes(app):

    @app.route("/manage/<container_id>", methods=["GET", "POST"])
    @login_required
    def manage_env(container_id):
        container = client.containers.get(container_id)

        # Extract current environment values
        env_raw = container.attrs["Config"]["Env"]
        env_vars = dict(item.split("=", 1) for item in env_raw if "=" in item)

        # Parse labels for type/editability
        labels = container.labels or {}
        fields = []

        for key in env_vars:
            field = {
                "key": key,
                "value": env_vars[key],
                "type": "text",
                "editable": True,
                "options": []
            }

            type_label = labels.get(f"envtype.{key}")
            editable_label = labels.get(f"editable.{key}", "true")

            if type_label:
                if type_label.startswith("dropdown["):
                    field["type"] = "dropdown"
                    options_str = type_label[len("dropdown["):-1]
                    field["options"] = [x.strip() for x in options_str.split(",")]
                else:
                    field["type"] = type_label

            field["editable"] = editable_label.lower() == "true"
            fields.append(field)

        return render_template("manage.html", container_id=container_id, container_name=container.name, fields=fields)