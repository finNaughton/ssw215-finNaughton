import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from ai_service import (
    ModelRefusalError,
    ProviderUnavailableError,
    extract_project,
    create_git_draft,
    refine_git_draft,
    refine_git_draft_blind,
    get_git_draft,
)
from github_service import (
    GitHubUnavailableError,
    ReadmeTooShortError,
    RepositoryNotFoundError,
    fetch_repository_readme,
)

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
    summary = db.Column(db.Text, nullable=False, default="")
    technologies = db.Column(db.Text, nullable=False, default="")
    difficulty = db.Column(db.String(20), nullable=False, default="Intermediate")
    likes = db.Column(db.Integer, default=0, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "summary": self.summary,
            "technologies": self.technologies,
            "difficulty": self.difficulty,
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
                summary=project.get("summary", ""),
                technologies=project.get("technologies", ""),
                likes=project["likes"],
                author_id=author.id,
            )
        )
    db.session.commit()


with app.app_context():
    db.create_all()
    columns = db.session.execute(db.text("PRAGMA table_info(project)")).fetchall()
    if columns and not any(column[1] == "difficulty" for column in columns):
        db.session.execute(
            db.text(
                "ALTER TABLE project ADD COLUMN difficulty "
                "VARCHAR(20) NOT NULL DEFAULT 'Intermediate'"
            )
        )
        db.session.commit()
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


@app.post("/api/projects/smart")
def smart_create_project():
    request_data = request.get_json(silent=True)
    notes = request_data.get("notes") if isinstance(request_data, dict) else None
    if not isinstance(notes, str) or len(notes.strip()) < 20:
        return jsonify({"error": "At least 20 characters of notes are required"}), 400

    author = db.session.execute(db.select(Author).order_by(Author.id)).scalars().first()
    if author is None:
        return jsonify({"error": "No project author is available"}), 400

    try:
        extraction = extract_project(notes.strip())
    except ModelRefusalError:
        return jsonify({"error": "The model refused to create a project"}), 422
    except ProviderUnavailableError:
        return jsonify({"error": "The AI provider is unavailable"}), 503

    summary = extraction.summary.strip()
    project = Project(
        title=extraction.title.strip(),
        description=summary,
        summary=summary,
        technologies=", ".join(
            technology.strip()
            for technology in extraction.technologies
            if technology.strip()
        ),
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


@app.post("/api/projects/git-start")
def git_start_project():
    request_data = request.get_json(silent=True)
    owner = request_data.get("owner") if isinstance(request_data, dict) else None
    repo = request_data.get("repo") if isinstance(request_data, dict) else None
    if not isinstance(owner, str) or not owner.strip() or not isinstance(repo, str) or not repo.strip():
        return jsonify({"error": "A repository owner and name are required"}), 400

    try:
        readme = fetch_repository_readme(owner.strip(), repo.strip())
    except RepositoryNotFoundError:
        return jsonify({"error": "Repository not found"}), 404
    except ReadmeTooShortError:
        return jsonify({"error": "README is shorter than 20 characters"}), 400
    except GitHubUnavailableError:
        return jsonify({"error": "GitHub is unavailable"}), 503

    try:
        session_id, draft = create_git_draft(readme)
    except ModelRefusalError:
        return jsonify({"error": "The model refused to create a draft"}), 422
    except ProviderUnavailableError:
        return jsonify({"error": "The AI provider is unavailable"}), 503

    return jsonify({
        "session_id": session_id,
        "draft": draft.model_dump(),
    }), 201


@app.post("/api/projects/git-refine")
def git_refine_project():
    request_data = request.get_json(silent=True)
    session_id = request_data.get("session_id") if isinstance(request_data, dict) else None
    feedback = request_data.get("feedback") if isinstance(request_data, dict) else None
    if not isinstance(session_id, str) or not isinstance(feedback, str):
        return jsonify({"error": "session_id and feedback are required"}), 400

    if get_git_draft(session_id) is None:
        return jsonify({"error": "Session not found"}), 404

    try:
        draft = refine_git_draft(session_id, feedback)
    except ModelRefusalError:
        return jsonify({"error": "The model refused to refine the draft"}), 422
    except ProviderUnavailableError:
        return jsonify({"error": "The AI provider is unavailable"}), 503

    return jsonify(draft.model_dump()), 200


@app.post("/api/projects/git-refine-blind")
def git_refine_project_blind():
    request_data = request.get_json(silent=True)
    session_id = request_data.get("session_id") if isinstance(request_data, dict) else None
    feedback = request_data.get("feedback") if isinstance(request_data, dict) else None
    if not isinstance(session_id, str) or not isinstance(feedback, str):
        return jsonify({"error": "session_id and feedback are required"}), 400

    if get_git_draft(session_id) is None:
        return jsonify({"error": "Session not found"}), 404

    try:
        draft = refine_git_draft_blind(session_id, feedback)
    except ModelRefusalError:
        return jsonify({"error": "The model refused to refine the draft"}), 422
    except ProviderUnavailableError:
        return jsonify({"error": "The AI provider is unavailable"}), 503

    return jsonify(draft.model_dump()), 200


@app.post("/api/projects/git-commit")
def git_commit_project():
    request_data = request.get_json(silent=True)
    session_id = request_data.get("session_id") if isinstance(request_data, dict) else None
    if not isinstance(session_id, str):
        return jsonify({"error": "session_id is required"}), 400

    draft = get_git_draft(session_id)
    if draft is None:
        return jsonify({"error": "Session not found"}), 404

    author = db.session.execute(db.select(Author).order_by(Author.id)).scalars().first()
    if author is None:
        return jsonify({"error": "No project author is available"}), 400

    project = Project(
        title=draft.title.strip(),
        description=draft.summary.strip(),
        summary=draft.summary.strip(),
        technologies=", ".join(
            technology.strip()
            for technology in draft.technologies
            if technology.strip()
        ),
        difficulty=draft.difficulty,
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
