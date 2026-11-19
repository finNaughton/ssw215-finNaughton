import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
database_path = Path(app.instance_path) / "portfolio.db"
database_path.parent.mkdir(parents=True, exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path.as_posix()}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
SEED_FILE = Path(__file__).resolve().parent / "projects_seed.json"


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    projects = db.relationship("Project", backref="author")


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False, default="")
    likes = db.Column(db.Integer, default=0, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "likes": self.likes,
            "author": self.author.name,
        }


def init_seed_data():
    if db.session.query(Project).count() != 0:
        return

    with SEED_FILE.open(encoding="utf-8") as file:
        seed_projects = json.load(file)

    author = Author(name="Fintan Naughton")
    db.session.add(author)
    db.session.flush()

    for project in seed_projects:
        db.session.add(
            Project(
                id=project["id"],
                title=project["title"],
                description=project["description"],
                likes=project["likes"],
                author_id=author.id,
            )
        )
    db.session.commit()


with app.app_context():
    db.create_all()
    init_seed_data()


@app.route("/")
def home():
    projects = db.session.execute(db.select(Project).order_by(Project.id)).scalars().all()
    return render_template("index.html", projects=projects)


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory("static/assets", filename)


@app.post("/api/projects/<int:project_id>/upvote")
def upvote(project_id):
    project = db.session.get(Project, project_id)
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    project.likes += 1
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Unable to update project"}), 400
    return jsonify({"id": project.id, "likes": project.likes})


@app.get("/api/projects")
def get_projects():
    projects = db.session.execute(db.select(Project).order_by(Project.id)).scalars().all()
    return jsonify([project.to_dict() for project in projects])


@app.post("/api/projects")
def create_project():
    request_data = request.get_json(silent=True)
    title = request_data.get("title") if isinstance(request_data, dict) else None
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "A non-empty title is required"}), 400

    author = db.session.execute(db.select(Author).order_by(Author.id)).scalars().first()
    if author is None:
        return jsonify({"error": "No project author is available"}), 400

    project = Project(
        title=title.strip(),
        description="",
        likes=0,
        author_id=author.id,
    )
    db.session.add(project)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "A project with that title already exists"}), 400
    return jsonify(project.to_dict()), 201


if __name__ == "__main__":
    app.run(debug=True)
