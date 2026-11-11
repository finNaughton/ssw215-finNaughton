const actionButtons = document.querySelectorAll(".site-nav .action-button");
const contentSections = document.querySelectorAll(".content-section");
const rhythmFilter = document.querySelector("#rhythm-filter");
const rhythmCards = document.querySelectorAll(".rhythm-card");
const practicePanel = document.querySelector("#practice-panel");
const closePracticeButton = document.querySelector("#close-practice");
const practiceImage = document.querySelector("#practice-image");
const practiceStatus = document.querySelector("#practice-status");
const practiceFeedback = document.querySelector("#practice-feedback");
const startPracticeButton = document.querySelector("#start-practice");

const BEAT_INTERVAL = 0.5;
const COUNT_IN_BEATS = 4;
const TIMING_TOLERANCE_MS = 200;
const LATE_WINDOW_MS = 250;

let selectedRhythm = null;
let audioContext = null;
let clickBus = null;
let noteTimes = [];
let nextNoteIndex = 0;
let practiceActive = false;
let sessionId = 0;
let startTimer = null;
let missTimer = null;
let stopTimer = null;

function closeSections() {
  contentSections.forEach((section) => {
    section.hidden = true;
    section.classList.add("is-hidden");
  });

  actionButtons.forEach((button) => {
    button.setAttribute("aria-expanded", "false");
  });
}

function scheduleClick(when) {
  const oscillator = audioContext.createOscillator();
  const gain = audioContext.createGain();
  oscillator.frequency.value = 880;
  gain.gain.setValueAtTime(0.25, when);
  gain.gain.exponentialRampToValueAtTime(0.001, when + 0.08);
  oscillator.connect(gain);
  gain.connect(clickBus);
  oscillator.start(when);
  oscillator.stop(when + 0.08);
}

function stopMetronome() {
  if (clickBus) {
    clickBus.disconnect();
    clickBus = null;
  }
}

function resetPractice() {
  sessionId += 1;
  window.clearTimeout(startTimer);
  window.clearTimeout(missTimer);
  window.clearTimeout(stopTimer);
  startTimer = null;
  missTimer = null;
  stopTimer = null;
  stopMetronome();
  practiceActive = false;
  nextNoteIndex = 0;
  noteTimes = [];
  startPracticeButton.disabled = false;
  practiceStatus.textContent = "Choose Practice to begin.";
}

function closePractice() {
  resetPractice();
  practicePanel.hidden = true;
  practicePanel.classList.add("is-hidden");
}

function openPractice(card) {
  resetPractice();
  selectedRhythm = {
    title: card.dataset.rhythmTitle,
    ref: card.dataset.rhythmRef,
    beats: JSON.parse(card.dataset.rhythmBeats),
  };
  practiceImage.src = selectedRhythm.ref;
  practiceImage.alt = selectedRhythm.title;
  practiceFeedback.textContent = "";
  practicePanel.hidden = false;
  practicePanel.classList.remove("is-hidden");
  practicePanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function advanceNote(result) {
  practiceFeedback.textContent = result;
  nextNoteIndex += 1;
}

function settleOverdueNotes(now) {
  while (nextNoteIndex < noteTimes.length && now >= noteTimes[nextNoteIndex] + LATE_WINDOW_MS) {
    advanceNote("Missed");
  }
}

function armMissTimer() {
  window.clearTimeout(missTimer);
  missTimer = null;

  if (!practiceActive || nextNoteIndex >= noteTimes.length) {
    return;
  }

  const delay = noteTimes[nextNoteIndex] + LATE_WINDOW_MS - performance.now();
  missTimer = window.setTimeout(() => {
    missTimer = null;
    settleOverdueNotes(performance.now());
    afterNoteChange();
  }, Math.max(0, delay));
}

function afterNoteChange() {
  if (nextNoteIndex >= noteTimes.length) {
    finishPractice();
  } else {
    armMissTimer();
  }
}

function finishPractice() {
  if (!practiceActive) {
    return;
  }

  practiceActive = false;
  window.clearTimeout(missTimer);
  missTimer = null;
  const finalNoteRemaining = noteTimes[noteTimes.length - 1] - performance.now();
  stopTimer = window.setTimeout(() => {
    stopTimer = null;
    stopMetronome();
  }, Math.max(100, finalNoteRemaining + 100));
  practiceStatus.textContent = "Practice complete.";
  startPracticeButton.disabled = false;
}

function handlePracticeKeydown(event) {
  if (!practiceActive || event.repeat) {
    return;
  }

  if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
    return;
  }

  const now = performance.now();
  settleOverdueNotes(now);

  if (nextNoteIndex >= noteTimes.length) {
    afterNoteChange();
    return;
  }

  event.preventDefault();
  const difference = now - noteTimes[nextNoteIndex];

  if (difference < -TIMING_TOLERANCE_MS) {
    practiceFeedback.textContent = "Early";
  } else if (difference <= TIMING_TOLERANCE_MS) {
    advanceNote("On time");
  } else {
    advanceNote("Late");
  }

  afterNoteChange();
}

async function beginPractice() {
  if (!selectedRhythm || practiceActive) {
    return;
  }

  resetPractice();
  const session = sessionId;
  startPracticeButton.disabled = true;
  practiceStatus.textContent = "Get ready...";
  practiceFeedback.textContent = "";

  audioContext = audioContext || new AudioContext();
  await audioContext.resume();

  if (session !== sessionId) {
    return;
  }

  startCountInAndRhythm(session);
}

function startCountInAndRhythm(session) {
  const LEAD_SECONDS = 0.1;
  const countInEnd = (COUNT_IN_BEATS - 1) * BEAT_INTERVAL;
  const latencyMs = (audioContext.outputLatency || audioContext.baseLatency || 0) * 1000;

  const firstClickAudio = audioContext.currentTime + LEAD_SECONDS;
  const firstClickPerf = performance.now() + LEAD_SECONDS * 1000 + latencyMs;
  const rhythmRefPerf = firstClickPerf + countInEnd * 1000;

  let totalSeconds = 0;
  noteTimes = selectedRhythm.beats.map((beat) => {
    totalSeconds += Number(beat);
    return rhythmRefPerf + totalSeconds * 1000;
  });

  clickBus = audioContext.createGain();
  clickBus.connect(audioContext.destination);

  const lastNoteSeconds = countInEnd + totalSeconds;
  const clickCount = Math.floor(lastNoteSeconds / BEAT_INTERVAL + 1e-6);
  for (let i = 0; i <= clickCount; i += 1) {
    scheduleClick(firstClickAudio + i * BEAT_INTERVAL);
  }

  startTimer = window.setTimeout(() => {
    if (session !== sessionId) {
      return;
    }

    startTimer = null;
    practiceActive = true;
    practiceStatus.textContent = "Press any key in time with the rhythm.";
    armMissTimer();
  }, rhythmRefPerf - performance.now());
}

actionButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const targetSection = document.querySelector(`#${button.dataset.section}`);
    const isOpen = button.getAttribute("aria-expanded") === "true";

    closeSections();
    closePractice();

    if (!isOpen && targetSection) {
      targetSection.hidden = false;
      targetSection.classList.remove("is-hidden");
      button.setAttribute("aria-expanded", "true");
      targetSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
});

rhythmCards.forEach((card) => {
  card.addEventListener("click", () => openPractice(card));
  card.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openPractice(card);
    }
  });
});

rhythmFilter.addEventListener("input", () => {
  const searchTerm = rhythmFilter.value.trim().toLowerCase();

  rhythmCards.forEach((card) => {
    card.hidden = !card.textContent.toLowerCase().includes(searchTerm);
  });
});

startPracticeButton.addEventListener("click", beginPractice);
closePracticeButton.addEventListener("click", closePractice);
document.addEventListener("keydown", handlePracticeKeydown);