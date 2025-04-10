
import tarfile
import io
import docker
from flask import request, redirect, url_for, flash, render_template
from modules.auth import requires_role

client = docker.from_env()

def register_upload_routes(app):

    @app.route("/upload", methods=["GET", "POST"])
    @requires_role("admin")
    def upload_file():
        if request.method == "POST":
            container_name = request.form["container"]
            path_in_container = request.form["path"]
            file = request.files["file"]

            if not file:
                flash("No file selected.")
                return redirect(url_for("upload_file"))

            # Create tar archive with file inside
            tarstream = io.BytesIO()
            with tarfile.open(fileobj=tarstream, mode="w") as tar:
                info = tarfile.TarInfo(name=path_in_container.split("/")[-1])
                file_bytes = file.read()
                info.size = len(file_bytes)
                tar.addfile(tarinfo=info, fileobj=io.BytesIO(file_bytes))
            tarstream.seek(0)

            try:
                container = client.containers.get(container_name)
                container.put_archive(path=path_in_container.rsplit("/", 1)[0], data=tarstream)
                flash("File uploaded successfully.")
            except Exception as e:
                flash(f"Error: {e}")

            return redirect(url_for("upload_file"))

        return render_template("upload.html")
