# SPEC: Developer Portfolio Welcome Page
## 1. Purpose & Scope
- A website designed to help people practice sight reading music rhythm.
- Non-Goals: no multi-page routing; no backend; no contact forms.

## 2. Invariants & Negative Constraints
- All styling MUST reside in `./style.css` (no inline style="..." attributes).
- The page MUST NOT load external CSS frameworks or CDNs (no Bootstrap, no Tailwind).
- The layout MUST collapse into a single vertical column on screens narrower than 768px.
- style.css MUST begin with the universal reset: `*, *::before, *::after { box-sizing:
border-box; }`.
- Spacing and font sizes MUST use rem. px MAY be used only for borders.
- Styling MUST use class selectors. ID selectors MUST NOT be used for styling.
- All rhythm data MUST live in a Python list of dictionaries named rhythms_db in
app.py. templates/index.html MUST NOT contain any hardcoded rhythms.
- templates/index.html MUST render one card per rhythm with a {% for %} loop.
- style.css and app.js MUST be linked with url_for('static', filename=...), never with a
plain relative path.
- No Jinja syntax ({{ }} or {% %}) may appear in static/app.js. External script files are
never processed by Flask.
- app.py MUST create the application with app = Flask(__name__), and MUST end with a
block that runs it with debug=True when the file is executed directly.
- rhythms.json MUST be the only source of rhythm data. app.py MUST NOT contain a
hardcoded list of rhythms.
- The path to rhythms.json MUST be built from the location of app.py, not from a bare
relative path.
- Every route that changes a rhythm MUST write the whole list back to rhythms.json
before it returns a response.
- rhythms.json MUST be written with json.dump(..., indent=2) so it stays readable in a
diff.

## 3. UI Content & Interface Contract
- Hero header: The website title (RYTM)
- Action Buttons: A set of 3 buttons which all open respective UI menus: Practice Rhythm, How to Use, and Credits
- Practice Rhythm takes user to a new section where they are displayed a random rhythm that they must click in time with. However, for the time being the opened menu should just display "Rhythms Coming Soon"
- How to use should give a brief overview of how to use the Practice Rhythms section. The steps should generally follow this guideline: The user will first be presented a random rhythm, they will then be able to view it over before clicking the "practice" button, then the user will hear 4 metronome clicks to get them in time with the rhythm, and finally the user will be able to press any button on their keyboard to be used as an input to click in time with the given rhythm.
- Credits should give credit to Fintan Naughton and link my GitHub: (https://github.com/finNaughton) MUST open in a new tab
- Github link must appear under the credits button
(target="_blank").
- Credits should also properly credit AI tools used in developing the site
- The page background MUST be white
- The page header MUST be black
- The action buttons should be black with white text
- The page MUST use semantic landmarks: one <header>, one <nav>, one <main>, one
<footer>, and each content group inside its own <section> with a heading.
- There MUST be exactly one <h1>, and heading levels MUST NOT skip (h1 then h2 then h3).
- The action buttons MUST have four visually distinct states: :hover, :focus-
visible, :active, and :disabled.
- All four state rules MUST live in style.css.
- Each rhythm in rhythms_db MUST have the keys: id (an integer), ref (a string with the file path to the rhythm image stored in frontend/static/assets/rhythms), and difficulty (easy, medium, hard)
- Each rendered card MUST carry the attribute data-rhythm-id holding that rhythm's id.
- Visiting http://127.0.0.1:5000/ MUST serve the page, with one card per entry in
rhythms_db.
- app.py MUST read rhythms.json and pass the resulting list to the template, so the page
shows whatever the file currently contains.
- objects in the "Choose a rhythm" section of a page MUST be able to be clicked on to open it in the practice UI.
- The practice UI opens a window on the current page and MUST NOT open a new page
- The practice UI contains an image of the rhythm with an action button underneath saying "Practice"
- items in rhythms.json MUST include a field for "beats", which is a list that stores the time in seconds between each set of beats at a bpm of 120.
- Pressing the "Practice" button plays 4 metronome clicks at 120bpm and then starts the practice, where the user must input using any button on their keyboard in time with the metronome clicks, based on the "beats" fields in rhythms.json. There should be a tolorance of about + or - .1 seconds.
- After each note, above the image of the rhythm MAY display either early, on time, late, or missed 
- There is a small "X" button in the top right corner of the practice section to close it
- Metronome clicks MUST continue throughout the round of practice, and MUST end once the final note occurs or the practice section is clicked out of

## 4. Acceptance Checklist
- [x] i can click on the practice rhythms to practice that specific rhythm
- [x] selecting the practice button below a rhythm in the practice ui begins practice mode
- [x] rhythm stays displayed during the practice mode
- [x] practice mode starts by providing 4 metronome clicks at 120 bpm
- [x] then allows the user to input to click in time with the rhythm, also at 120 bpm
- [x] metronome continues playing until all beats are done
- [x] items in rhythms.json have a "beats" field
- [x] there is a tolerance on each input for "on-time"
- [x] metronome audio MUST click exactly every .5 seconds during practice, even when beats are longer than .5 seconds.

## 5. Audit Protocol
- Inspect the generated code line by line with `git diff --staged` before committing.