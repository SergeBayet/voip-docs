function makeSorter(containerId, scoreId, groups, items) {
  const container = document.getElementById(containerId);
  const score = document.getElementById(scoreId);
  let answered = 0;
  let correct = 0;

  score.setAttribute("aria-live", "polite");
  for (const item of items) {
    const row = document.createElement("div");
    row.className = "sorter-row";
    const label = document.createElement("span");
    label.className = "item";
    label.textContent = item.name;
    row.appendChild(label);

    const feedback = document.createElement("div");
    feedback.className = "fb";
    feedback.setAttribute("aria-live", "polite");
    for (const group of groups) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "opt";
      button.textContent = group.label;
      button.addEventListener("click", () => {
        if (row.dataset.done) return;
        row.dataset.done = "1";
        answered += 1;
        const isCorrect = group.key === item.answer;
        if (isCorrect) {
          button.classList.add("correct");
          correct += 1;
        } else {
          button.classList.add("wrong");
          const rightLabel = groups.find((candidate) => candidate.key === item.answer).label;
          for (const candidate of row.querySelectorAll(".opt")) {
            if (candidate.textContent === rightLabel) candidate.classList.add("correct");
          }
        }
        for (const candidate of row.querySelectorAll(".opt")) candidate.disabled = true;
        const rightLabel = groups.find((candidate) => candidate.key === item.answer).label;
        feedback.innerHTML = `${isCorrect ? "Correct." : `Incorrect. Correct answer: ${rightLabel}.`} ${item.why}`;
        feedback.classList.add("show");
        if (answered === items.length) {
          score.textContent = `Score: ${correct}/${items.length}. ${correct === items.length ? "Locked in. 🦜" : "Review the boundary you missed, then retry tomorrow."}`;
        }
      });
      row.appendChild(button);
    }
    row.appendChild(feedback);
    container.appendChild(row);
  }
}

function makeQuiz(containerId, scoreId, questions) {
  const container = document.getElementById(containerId);
  const score = document.getElementById(scoreId);
  let answered = 0;
  let correct = 0;

  score.setAttribute("aria-live", "polite");
  questions.forEach((question, index) => {
    const wrapper = document.createElement("div");
    wrapper.className = "q";
    const stem = document.createElement("div");
    stem.className = "stem";
    stem.textContent = `${index + 1}. ${question.stem}`;
    wrapper.appendChild(stem);
    const feedback = document.createElement("div");
    feedback.className = "fb";
    feedback.setAttribute("aria-live", "polite");

    for (const choice of question.choices) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "choice";
      button.textContent = choice.text;
      button.addEventListener("click", () => {
        if (wrapper.dataset.done) return;
        wrapper.dataset.done = "1";
        answered += 1;
        if (choice.correct) {
          button.classList.add("correct");
          correct += 1;
        } else {
          button.classList.add("wrong");
          const rightText = question.choices.find((candidate) => candidate.correct).text;
          for (const candidate of wrapper.querySelectorAll(".choice")) {
            if (candidate.textContent === rightText) candidate.classList.add("correct");
          }
        }
        for (const candidate of wrapper.querySelectorAll(".choice")) candidate.disabled = true;
        const rightText = question.choices.find((candidate) => candidate.correct).text;
        feedback.innerHTML = `${choice.correct ? "Correct." : `Incorrect. Correct answer: ${rightText}.`} ${question.why}`;
        feedback.classList.add("show");
        if (answered === questions.length) {
          score.textContent = `Score: ${correct}/${questions.length}. ${correct === questions.length ? "Ready to use it. 🦜" : "Explain the missed answer aloud before moving on."}`;
        }
      });
      wrapper.appendChild(button);
    }
    wrapper.appendChild(feedback);
    container.appendChild(wrapper);
  });
}

function makeOrderer(containerId, scoreId, steps) {
  const container = document.getElementById(containerId);
  const score = document.getElementById(scoreId);
  const shuffled = steps.map((text, index) => ({ text, index }))
    .sort((left, right) => (left.text.length % 3 - right.text.length % 3) || (right.index - left.index));
  let expected = 0;

  score.setAttribute("aria-live", "polite");
  for (const step of shuffled) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "choice";
    button.textContent = step.text;
    button.addEventListener("click", () => {
      if (button.disabled) return;
      if (step.index === expected) {
        button.classList.add("correct");
        button.disabled = true;
        button.textContent = `${expected + 1}. ${step.text}`;
        expected += 1;
        if (expected === steps.length) score.textContent = `All ${steps.length} steps in order. Locked in. 🦜`;
      } else {
        button.classList.add("wrong");
        window.setTimeout(() => button.classList.remove("wrong"), 600);
        score.textContent = "Not yet — which step must happen first?";
      }
    });
    container.appendChild(button);
  }
}

function initializeCourseDiagrams() {
  if (!window.mermaid) return;
  window.mermaid.initialize({
    startOnLoad: true,
    theme: "neutral",
    themeVariables: {
      fontFamily: "ui-sans-serif, system-ui, sans-serif",
      fontSize: "14px",
    },
  });
}
