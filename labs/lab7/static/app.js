const filterInput = document.querySelector("#filter-input");
const projectCount = document.querySelector("#project-count");
const projectCards = Array.from(document.querySelectorAll(".card"));
const totalProjects = projectCards.length;
const upvoteButtons = document.querySelectorAll(".upvote-btn");

function updateProjectList() {
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

  projectCount.textContent = `Showing ${visibleProjects} of ${totalProjects} projects`;
  console.log(visibleProjectTitles);
}

filterInput.addEventListener("input", updateProjectList);
updateProjectList();

upvoteButtons.forEach((button) => {
  button.addEventListener("click", async () => {
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
});
