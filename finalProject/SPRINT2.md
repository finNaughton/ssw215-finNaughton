# Sprint 2 Report: RYTM

## Project Recap & API Surface

RYTM is a browser-based rhythm practice tool for beginner musicians. Flask
loads rhythm records from a SQLite database, renders them as selectable rhythm
cards, and provides a practice panel where the user follows a metronome and
presses keys in time with each rhythm. Currently, only Rhythms 1-3 are fully
implemented since all rhythm timings must be manually input.

| Endpoint | Verb | Request payload | Response / status |
| --- | --- | --- | --- |
| `/` | `GET` | None | HTML page containing the rhythm library; `200 OK` |
| `/api/rhythm` | `GET` | None | JSON array of rhythm objects; `200 OK` |
| `/api/rhythms` | `GET` | None | JSON array of rhythm objects; `200 OK` (alias of `/api/rhythm`) |

Each rhythm object returned by the API has this shape:

```json
{
  "id": 1,
  "title": "Rhythm 1",
  "ref": "assets/rhythms/rytm1.png",
  "difficulty": "easy",
  "beats": [0.5, 0.5, 0.5]
}
```

The `beats` array stores the number of seconds between successive notes at the
project's 120 BPM practice tempo. The browser uses the image reference and
beat timings to start the practice interaction.

## Database Schema

The application uses SQLite through Flask-SQLAlchemy. The database file is
`finalProject/backend/instance/portfolio.db`.

| Table | Column | Type | Constraints |
| --- | --- | --- | --- |
| `rhythm` | `id` | `INTEGER` | Primary key |
| `rhythm` | `title` | `VARCHAR(120)` | Required, unique |
| `rhythm` | `ref` | `VARCHAR(120)` | Required, unique |
| `rhythm` | `difficulty` | `VARCHAR(120)` | Required |
| `rhythm` | `beats` | `JSON` | Required |

When the server starts, it creates the table if necessary and seeds it from
`backend/rhythms_seed.json` only when the table is empty. Restarting the
server therefore does not duplicate the seed records.

## How to Run & Test

1. Clone the repository and move into the backend directory:
   ```bash
   git clone https://github.com/finNaughton/ssw215-finNaughton.git
   cd ssw215-finNaughton/finalProject/backend
   ```
2. Install the backend dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Start the Flask server:
   ```bash
   python app.py
   ```
4. Open `http://127.0.0.1:5000/` in a browser. Select **Practice Rhythm**,
   choose a rhythm card, click **Practice**, wait through the four-click
   count-in, and press keyboard keys in time with the displayed rhythm. The API
   can also be checked at
   `http://127.0.0.1:5000/api/rhythms`.

## AI Usage Log & Reflection

I used GitHub Copilot with prompts asking it to implement the RYTM frontend,
convert the rhythm data from file-based storage to Flask-SQLAlchemy, seed an
empty database, and review the API and user workflow against the project
specification. During review, AI called out areas that could easily become
bugs: using a path relative to the current working directory for the seed
file, duplicating seed rows after a server restart, failing to roll back a
database transaction after an integrity error, and returning an inconsistent
API shape. I fixed these by resolving paths from `app.py`, seeding only an
empty table, rolling back failed commits before surfacing the error, and
returning every record through `Rhythm.to_dict()` with an explicit `200`
status. The implemented API is read-only, so no incorrect mutation status
code was needed; the two API routes intentionally return `200 OK` for a
successful JSON array.

The file-based prototype required manually reading and rewriting a complete
JSON file whenever data changed, generating and preserving IDs manually, and
could have produced lost updates if two requests wrote at the same time. The
relational database now assigns and enforces primary keys and uniqueness while
handling persistence through transactions. This makes restart behavior and
future concurrent access more reliable than manual file I/O.