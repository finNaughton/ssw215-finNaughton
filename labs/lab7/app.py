import json
from pathlib import Path

from flask import Flask, jsonify, render_template, send_from_directory

app = Flask(__name__)

PROJECTS_FILE = Path(__file__).resolve().parent / "projects.json"


def load_projects():
    with PROJECTS_FILE.open(encoding="utf-8") as file:
        return json.load(file)


def save_projects(projects):
    with PROJECTS_FILE.open("w", encoding="utf-8") as file:
        json.dump(projects, file, indent=2)
        file.write("\n")


projects_db = load_projects()


@app.route("/")
def home():
    return render_template("index.html", projects=projects_db)


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory("static/assets", filename)


@app.post("/api/projects/<int:project_id>/upvote")
def upvote(project_id):
    project = next((item for item in projects_db if item["id"] == project_id), None)
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    project["likes"] += 1
    save_projects(projects_db)
    return jsonify({"id": project["id"], "likes": project["likes"]})


if __name__ == "__main__":
    app.run(debug=True)
