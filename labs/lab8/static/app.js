const filterInput = document.querySelector("#filter-input");
const projectCount = document.querySelector("#project-count");
const projectList = document.querySelector(".project-list");
const newTitleInput = document.querySelector("#new-title");
const addProjectButton = document.querySelector("#add-project");

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
    const card = document.createElement("article");
    card.className = "card";
    card.dataset.projectId = project.id;
    card.innerHTML = `
      <h3 class="card-title"></h3>
      <p class="card-copy"></p>
      <div class="card-actions">
        <button class="upvote-btn" type="button">Upvote</button>
        <span class="like-count"></span>
      </div>
    `;
    card.querySelector(".card-title").textContent = project.title;
    card.querySelector(".card-copy").textContent = project.description;
    card.querySelector(".like-count").textContent = project.likes;
    projectList.append(card);
    newTitleInput.value = "";
    updateProjectList();
  } catch (error) {
    console.error(error);
  } finally {
    addProjectButton.disabled = false;
  }
});
