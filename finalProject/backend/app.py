from pathlib import Path

from flask import Flask, render_template


APP_ROOT = Path(__file__).resolve().parent.parent

app = Flask(__name__)
app.template_folder = str(APP_ROOT / "frontend" / "templates")
app.static_folder = str(APP_ROOT / "frontend" / "static")


rhythms_db = [
    {
        "id": rhythm_id,
        "title": f"Rhythm {rhythm_id}",
        "ref": f"assets/rhythms/rytm{rhythm_id}.png",
        "difficulty": "easy" if rhythm_id <= 35 else "medium",
    }
    for rhythm_id in range(1, 43)
]


@app.get("/")
def index():
    return render_template("index.html", rhythms=rhythms_db)


if __name__ == "__main__":
    app.run(debug=True)
