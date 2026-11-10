const actionButtons = document.querySelectorAll(".action-button");
const contentSections = document.querySelectorAll(".content-section");
const rhythmFilter = document.querySelector("#rhythm-filter");
const rhythmCards = document.querySelectorAll(".rhythm-card");

function closeSections() {
  contentSections.forEach((section) => {
    section.hidden = true;
    section.classList.add("is-hidden");
  });

  actionButtons.forEach((button) => {
    button.setAttribute("aria-expanded", "false");
  });
}

actionButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const targetSection = document.querySelector(`#${button.dataset.section}`);
    const isOpen = button.getAttribute("aria-expanded") === "true";

    closeSections();

    if (!isOpen && targetSection) {
      targetSection.hidden = false;
      targetSection.classList.remove("is-hidden");
      button.setAttribute("aria-expanded", "true");
      targetSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
});

rhythmFilter.addEventListener("input", () => {
  const searchTerm = rhythmFilter.value.trim().toLowerCase();

  rhythmCards.forEach((card) => {
    const matches = card.textContent.toLowerCase().includes(searchTerm);
    card.hidden = !matches;
  });
});
