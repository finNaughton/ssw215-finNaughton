const filterInput = document.querySelector("#filter-input");
const projectCount = document.querySelector("#project-count");
const projectCards = Array.from(document.querySelectorAll(".card"));
const totalProjects = projectCards.length;

function updateProjectList() {
  const searchTerm = filterInput.value.trim().toLowerCase();
  let visibleProjects = 0;

  projectCards.forEach((card) => {
    const matches = card.textContent.toLowerCase().includes(searchTerm);
    card.classList.toggle("is-hidden", !matches); // hand edited by FN

    if (matches) {
      visibleProjects += 1;
    }
  });

  projectCount.textContent = `Showing ${visibleProjects} of ${totalProjects} projects`;
}

filterInput.addEventListener("input", updateProjectList);
updateProjectList();
