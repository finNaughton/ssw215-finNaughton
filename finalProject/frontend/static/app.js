const actionButtons = document.querySelectorAll(".action-button");
const contentSections = document.querySelectorAll(".content-section");

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
