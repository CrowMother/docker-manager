
import docker
import tarfile
import io
from flask import request, redirect, url_for, flash, render_template
from modules.auth import requires_role
from modules.auth import get_user_containers
from flask import session

client = docker.from_env()

def register_upload_routes(app):

    @app.route("/upload", methods=["GET", "POST"])
    @requires_role("admin")
    def upload_file():
        if request.method == "POST":
            container_name = request.form["container"]
            label_key = request.form["labelkey"]
            file = request.files["file"]

            if not file or not container_name or not label_key:
                flash("Missing file, container, or label key.")
                return redirect(url_for("upload_file"))

            try:
                container = client.containers.get(container_name)
                labels = container.labels or {}
                dest_path = labels.get(label_key)

                if not dest_path:
                    flash(f"No label found for key: {label_key}")
                    return redirect(url_for("upload_file"))

                tarstream = io.BytesIO()
                with tarfile.open(fileobj=tarstream, mode="w") as tar:
                    filename = dest_path.split("/")[-1]
                    info = tarfile.TarInfo(name=filename)
                    file_bytes = file.read()
                    info.size = len(file_bytes)
                    tar.addfile(tarinfo=info, fileobj=io.BytesIO(file_bytes))
                tarstream.seek(0)

                container.put_archive(path=dest_path.rsplit("/", 1)[0], data=tarstream)
                flash("File uploaded successfully.")
            except Exception as e:
                flash(f"Upload failed: {e}")

            return redirect(url_for("upload_file"))

        

        username = session.get("username")
        all_containers = client.containers.list(all=True)
        user_containers = [
            {"name": c.name, "labels": c.labels or {}}
            for c in all_containers if c.name in get_user_containers(username)
        ]
        return render_template("upload.html", containers=user_containers)


