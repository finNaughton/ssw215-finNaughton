import json
from pathlib import Path

from flask import Flask, render_template


APP_ROOT = Path(__file__).resolve().parent.parent
RHYTHMS_PATH = Path(__file__).resolve().parent / "rhythms.json"

app = Flask(__name__)
app.template_folder = str(APP_ROOT / "frontend" / "templates")
app.static_folder = str(APP_ROOT / "frontend" / "static")


def load_rhythms():
    with RHYTHMS_PATH.open("r", encoding="utf-8") as rhythms_file:
        return json.load(rhythms_file)


def save_rhythms(rhythms):
    with RHYTHMS_PATH.open("w", encoding="utf-8") as rhythms_file:
        json.dump(rhythms, rhythms_file, indent=2)


rhythms_db = load_rhythms()


@app.get("/")
def index():
    return render_template("index.html", rhythms=rhythms_db)


if __name__ == "__main__":
    app.run(debug=True)
