import yaml
import docker
from flask import request, redirect, url_for, flash, render_template
from modules.auth import login_required
import os

client = docker.from_env()

def register_manage_routes(app):

    @app.route("/manage/<container_id>", methods=["GET", "POST"])
    @login_required
    def manage_env(container_id):
        container = client.containers.get(container_id)
        labels = container.labels or {}

        if request.method == "POST":
            updated_env = {}
            envtypes = {k[8:]: v for k, v in labels.items() if k.startswith("envtype.")}

            for key in envtypes:
                field_type = envtypes[key]
                if field_type == "checkbox":
                    updated_env[key] = "true" if request.form.get(key) == "true" else "false"
                else:
                    updated_env[key] = request.form.get(key, "")

            try:
                compose_path = labels.get("compose.path", "docker-compose.yml")
                print(f"[DEBUG] Using compose file path: {compose_path}")


                with open(compose_path, "r") as f:
                    compose_data = yaml.safe_load(f)

                services = compose_data.get("services", {})
                matched = False

                for name, service in services.items():
                    print(f"[DEBUG] Checking service '{name}'...")
                    container_name = service.get("container_name")
                    print(f"[DEBUG] Comparing container.name: {container.name} to service.container_name: {container_name}")
                    if container_name and container.name == container_name:
                        print(f"[DEBUG] Matched container '{container.name}' under service '{name}'")
                        # Update block-style environment
                        if "environment" not in service:
                            service["environment"] = {}
                        for k, v in updated_env.items():
                            print(f"[DEBUG] Updating {k}={v}")
                            service["environment"][k] = v
                        matched = True
                        break

                if matched:
                    with open(compose_path, "w") as f:
                        yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)
                    flash("✅ Environment updated in docker-compose.yml")
                else:
                    flash("⚠️ No matching service found for container.")
            except Exception as e:
                flash(f"❌ Failed to update docker-compose.yml: {str(e)}")

            return redirect(url_for("manage_env", container_id=container_id))

        env_raw = container.attrs["Config"]["Env"]
        env_vars = dict(item.split("=", 1) for item in env_raw if "=" in item)

        fields = []
        for key in env_vars:
            type_label = labels.get(f"envtype.{key}")
            if not type_label:
                continue

            field = {
                "key": key,
                "value": env_vars[key],
                "type": "text",
                "editable": labels.get(f"editable.{key}", "true").lower() == "true",
                "options": []
            }

            if type_label.startswith("dropdown["):
                field["type"] = "dropdown"
                options_str = type_label[len("dropdown["):-1]
                field["options"] = [x.strip() for x in options_str.split(",")]
            else:
                field["type"] = type_label.lower()

            fields.append(field)

        return render_template("manage.html", container_id=container_id, container_name=container.name, fields=fields)