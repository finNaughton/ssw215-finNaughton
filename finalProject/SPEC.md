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
- <nav> MUST contain a link to my GitHub profile.
- The action buttons MUST have four visually distinct states: :hover, :focus-
visible, :active, and :disabled.
- All four state rules MUST live in style.css.

## 4. Acceptance Checklist
- [x] Exactly one <h1>, one <header>, one <nav>, one <main>, one <footer>.
- [x] style.css begins with the box-sizing reset.
- [x] No inline style="..." attributes anywhere in index.html.
- [x] No ID selectors (#something) in style.css.
- [x] No horizontal scrollbar when the browser is narrowed to 375px.
- [x] Page background color is correct
- [x] Hovering the buttons visibly changes them.
- [x] Tabbing to the buttons shows a clear focus ring.
- [x] Holding the mouse down on it looks different again.
- [x] Only HTML, CSS, and JavaScript are used
- [ ] Github link MUST be within the credits menu

## 5. Audit Protocol
- Inspect the generated code line by line with `git diff --staged` before committing.