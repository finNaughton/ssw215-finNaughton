from flask import Flask, jsonify, render_template, send_from_directory

app = Flask(__name__)

projects_db = [
    {
        "id": 1,
        "title": "Raspberry Pi digital rotating picture frame",
        "description": "An all purpose digital rotating picture frame containing all student essentials.",
        "likes": 0,
    },
    {
        "id": 2,
        "title": "CLONE research assistant",
        "description": "Research assistant for CLONE, an AI powered refactoring tool.",
        "likes": 0,
    },
    {
        "id": 3,
        "title": "Arduino based digital picture frame",
        "description": "A digital picture frame using an Arduino to draw images",
        "likes": 0,
    },
]


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
    return jsonify({"id": project["id"], "likes": project["likes"]})


if __name__ == "__main__":
    app.run(debug=True)
