from flask import Flask, render_template, send_from_directory

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
    { #hand-edited by FN
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


if __name__ == "__main__":
    app.run(debug=True)
