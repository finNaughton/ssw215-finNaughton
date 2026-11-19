const filterInput = document.querySelector("#filter-input");
const projectCount = document.querySelector("#project-count");
const projectList = document.querySelector(".project-list");
const newTitleInput = document.querySelector("#new-title");
const addProjectButton = document.querySelector("#add-project");
const smartNotesInput = document.querySelector("#smart-notes");
const smartCreateButton = document.querySelector("#smart-create");
const repoOwnerInput = document.querySelector("#repo-owner");
const repoNameInput = document.querySelector("#repo-name");
const fetchGitHubDraftButton = document.querySelector("#fetch-github-draft");
const githubDraftPanel = document.querySelector("#github-draft-panel");
const draftFeedbackInput = document.querySelector("#draft-feedback");
const sendDraftFeedbackButton = document.querySelector("#send-draft-feedback");
const approveDraftButton = document.querySelector("#approve-draft");

let gitSessionId = null;

function renderGitHubDraft(draft) {
  document.querySelector("#draft-title").textContent = `Title: ${draft.title}`;
  document.querySelector("#draft-summary").textContent = `Summary: ${draft.summary}`;
  document.querySelector("#draft-technologies").textContent =
    `Technologies: ${draft.technologies.join(", ")}`;
  document.querySelector("#draft-difficulty").textContent =
    `Difficulty: ${draft.difficulty}`;
  githubDraftPanel.classList.remove("hidden");
}

function appendProjectCard(project) {
  const card = document.createElement("article");
  card.className = "card";
  card.dataset.projectId = project.id;
  card.innerHTML = `
    <h3 class="card-title"></h3>
    <p class="card-copy"></p>
    <p class="card-author"></p>
    <p class="card-difficulty"></p>
    <div class="card-actions">
      <button class="upvote-btn" type="button">Upvote</button>
      <span class="like-count"></span>
    </div>
  `;
  card.querySelector(".card-title").textContent = project.title;
  card.querySelector(".card-copy").textContent = project.summary || project.description;
  card.querySelector(".card-author").textContent = `By ${project.author}`;
  card.querySelector(".card-difficulty").textContent =
    `Difficulty: ${project.difficulty || "Intermediate"}`;
  card.querySelector(".like-count").textContent = project.likes;
  projectList.append(card);
  updateProjectList();
}

function updateProjectList() {
  const projectCards = Array.from(document.querySelectorAll(".card"));
  const searchTerm = filterInput.value.trim().toLowerCase();
  let visibleProjects = 0;
  const visibleProjectTitles = [];

  projectCards.forEach((card) => {
    const matches = card.textContent.toLowerCase().includes(searchTerm);
    card.classList.toggle("hidden", !matches);

    if (matches) {
      visibleProjects += 1;
      visibleProjectTitles.push(card.querySelector(".card-title").textContent.trim());
    }
  });

  projectCount.textContent = `Showing ${visibleProjects} of ${projectCards.length} projects`;
  console.log(visibleProjectTitles);
}

filterInput.addEventListener("input", updateProjectList);
updateProjectList();

projectList.addEventListener("click", async (event) => {
  if (!event.target.classList.contains("upvote-btn")) {
    return;
  }

  const button = event.target;
  const card = button.closest(".card");
  const projectId = card.dataset.projectId;

  button.disabled = true;
  try {
    const response = await fetch(`/api/projects/${projectId}/upvote`, {
      method: "POST",
    });

    if (!response.ok) {
      throw new Error(`Upvote failed with status ${response.status}`);
    }

    const project = await response.json();
    card.querySelector(".like-count").textContent = project.likes;
  } catch (error) {
    console.error(error);
  } finally {
    button.disabled = false;
  }
});

addProjectButton.addEventListener("click", async () => {
  addProjectButton.disabled = true;
  try {
    const response = await fetch("/api/projects", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ title: newTitleInput.value }),
    });

    if (!response.ok) {
      throw new Error(`Project creation failed with status ${response.status}`);
    }

    const project = await response.json();
    appendProjectCard(project);
    newTitleInput.value = "";
  } catch (error) {
    console.error(error);
  } finally {
    addProjectButton.disabled = false;
  }
});

smartCreateButton.addEventListener("click", async () => {
  smartCreateButton.disabled = true;
  try {
    const response = await fetch("/api/projects/smart", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ notes: smartNotesInput.value }),
    });

    if (!response.ok) {
      throw new Error(`Smart project creation failed with status ${response.status}`);
    }

    const project = await response.json();
    appendProjectCard(project);
    smartNotesInput.value = "";
  } catch (error) {
    console.error(error);
  } finally {
    smartCreateButton.disabled = false;
  }
});

fetchGitHubDraftButton.addEventListener("click", async () => {
  fetchGitHubDraftButton.disabled = true;
  try {
    const response = await fetch("/api/projects/git-start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        owner: repoOwnerInput.value,
        repo: repoNameInput.value,
      }),
    });
    if (!response.ok) {
      throw new Error(`GitHub draft failed with status ${response.status}`);
    }
    const result = await response.json();
    gitSessionId = result.session_id;
    renderGitHubDraft(result.draft);
  } catch (error) {
    console.error(error);
  } finally {
    fetchGitHubDraftButton.disabled = false;
  }
});

sendDraftFeedbackButton.addEventListener("click", async () => {
  if (!gitSessionId) {
    return;
  }
  sendDraftFeedbackButton.disabled = true;
  try {
    const response = await fetch("/api/projects/git-refine", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: gitSessionId,
        feedback: draftFeedbackInput.value,
      }),
    });
    if (!response.ok) {
      throw new Error(`Draft refinement failed with status ${response.status}`);
    }
    renderGitHubDraft(await response.json());
  } catch (error) {
    console.error(error);
  } finally {
    sendDraftFeedbackButton.disabled = false;
  }
});

approveDraftButton.addEventListener("click", async () => {
  if (!gitSessionId) {
    return;
  }
  approveDraftButton.disabled = true;
  try {
    const response = await fetch("/api/projects/git-commit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: gitSessionId }),
    });
    if (!response.ok) {
      throw new Error(`Draft approval failed with status ${response.status}`);
    }
    const project = await response.json();
    appendProjectCard(project);
    githubDraftPanel.classList.add("hidden");
    gitSessionId = null;
  } catch (error) {
    console.error(error);
  } finally {
    approveDraftButton.disabled = false;
  }
});
