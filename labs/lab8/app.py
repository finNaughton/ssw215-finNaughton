import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

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


@app.post("/api/projects")
def create_project():
    request_data = request.get_json(silent=True)
    title = request_data.get("title") if isinstance(request_data, dict) else None
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "A non-empty title is required"}), 400

    projects_db.clear()
    projects_db.extend(load_projects())
    project = {
        "id": max((item["id"] for item in projects_db), default=0) + 1,
        "title": title.strip(),
        "description": "",
        "likes": 0,
    }
    projects_db.append(project)
    save_projects(projects_db)
    return jsonify(project), 201


if __name__ == "__main__":
    app.run(debug=True)
