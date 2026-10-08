# SPEC: Developer Portfolio Welcome Page
## 1. Purpose & Scope
- A personal portfolio welcome page for Fintan Naughton, a first-year software
engineering student.
- Non-Goals: no multi-page routing; no backend; no contact forms.
## 2. Invariants & Negative Constraints
- All styling MUST reside in `./style.css` (no inline style="..." attributes).
- The page MUST NOT load external CSS frameworks or CDNs (no Bootstrap, no Tailwind).
- The avatar image MUST use the relative path `./assets/avatar.jpg`.
- The layout MUST collapse into a single vertical column on screens narrower than 768px.
- style.css MUST begin with the universal reset: `*, *::before, *::after { box-sizing:
border-box; }`.
- Spacing and font sizes MUST use rem. px MAY be used only for borders.
- Styling MUST use class selectors. ID selectors MUST NOT be used for styling.
- All JavaScript MUST live in ./app.js. index.html MUST NOT contain inline onclick
attributes or any <script> block with code inside it.
- app.js MUST be loaded from <head> with <script src="./app.js" defer></script>.
- Showing and hiding MUST be done by adding and removing a CSS class. app.js MUST NOT set
styles directly through .style.
## 3. UI Content & Interface Contract
- Hero header: my full name "Fintan Naughton", the subtitle "First year software engineering student interested in the intersection between software and music.", and
this bio: "a 2-sentence bio".
- Action link: a button labelled "See my projects" that links to `#projects`.
- Projects section with id="projects": lists these items: An all purpose digital rotating picture frame containing all student essentials. Research assistant for CLONE, an AI powered refactoring tool.
- Social link: GitHub (https://github.com/finNaughton) MUST open in a new tab
(target="_blank").
- The page background MUST be a dark navy blue
- The header MUST be a slightly lighter shade of blue and SHOULD have white text
- The box containing the information in the header MUST be the only part in a lighter blue; the rest of the background surrounding this box of information MUST remain a dark navy blue
- The page MUST use semantic landmarks: one <header>, one <nav>, one <main>, one
<footer>, and each content group inside its own <section> with a heading.
- There MUST be exactly one <h1>, and heading levels MUST NOT skip (h1 then h2 then h3).
- <nav> MUST contain a link to the projects section and a link to my GitHub profile.
- Each project MUST be an <article class="card"> inside a container that uses display:
flex, flex-wrap: wrap and gap.
- The "See my projects" button MUST have four visually distinct states: :hover, :focus-
visible, :active, and :disabled.
- A second button labelled "Contact me (coming soon)" MUST be present with the HTML
disabled attribute, and MUST NOT look clickable.
- All four state rules MUST live in style.css.
- Above the projects there MUST be a text input with id="filter-input", and a <label>
bound to it reading "Filter projects".
- There MUST be an element with id="project-count" that reads "Showing X of Y projects".
- As the user types, cards whose text does not contain what was typed MUST be hidden by
adding the class "hidden", and the count MUST update immediately — no button, no page
reload.
- Emptying the box MUST bring every card back.
- style.css MUST define .hidden { display: none; }.

## 4. Acceptance Checklist
- [x] app.js is loaded from <head> with defer, and index.html has no inline onclick and
no code inside a <script> tag.
- [x] Typing in the filter box hides and shows cards live, without pressing anything.
- [x] The "Showing X of Y projects" line updates as I type.
- [x] Emptying the box brings every card back.
- [x] app.js contains no .style assignments — hiding is done with the "hidden" class.
- [x] The DevTools Console shows no red errors when the page loads.


## 5. Audit Protocol
- Inspect the generated code line by line with `git diff --staged` before committing.