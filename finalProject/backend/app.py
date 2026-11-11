import json
from pathlib import Path

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

APP_ROOT = Path(__file__).resolve().parent.parent

app = Flask(__name__)
app.template_folder = str(APP_ROOT / "frontend" / "templates")
app.static_folder = str(APP_ROOT / "frontend" / "static")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{(Path(app.instance_path) / 'portfolio.db').as_posix()}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
SEED_FILE = Path(__file__).resolve().parent / "rhythms_seed.json"


class Rhythm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, unique=True)
    ref = db.Column(db.String(120), nullable=False, unique=True)
    difficuly = db.Column("difficulty", db.String(120), nullable=False)
    beats = db.Column(db.JSON, nullable=False, default=[0.5])

    @property
    def difficulty(self):
        return self.difficuly

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "ref": self.ref,
            "difficulty": self.difficulty,
            "beats": self.beats,
        }


def init_seed_data():
    if db.session.query(Rhythm).count() != 0:
        return

    with SEED_FILE.open(encoding="utf-8") as seed_file:
        seed_rhythms = json.load(seed_file)

    for rhythm in seed_rhythms:
        db.session.add(
            Rhythm(
                id=rhythm["id"],
                title=rhythm["title"],
                ref=rhythm["ref"],
                difficuly=rhythm["difficulty"],
                beats=rhythm["beats"],
            )
        )

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise


with app.app_context():
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.create_all()
    init_seed_data()


@app.get("/")
def index():
    rhythms = db.session.execute(db.select(Rhythm).order_by(Rhythm.id)).scalars().all()
    return render_template("index.html", rhythms=rhythms)


@app.get("/api/rhythm")
@app.get("/api/rhythms")
def get_rhythms():
    rhythms = db.session.execute(db.select(Rhythm).order_by(Rhythm.id)).scalars().all()
    return jsonify([rhythm.to_dict() for rhythm in rhythms]), 200


if __name__ == "__main__":
    app.run(debug=True)
