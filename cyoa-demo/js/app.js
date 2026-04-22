import {
  button,
  choiceCard,
  escapeHtml,
  formatDecimal,
  formatPercent,
  ghostButton,
  metricCard,
  pathwayControls,
  pathwayFrame,
  progressPill,
  shell,
  tableCard,
} from "./components.js";
import { lemmatizationData } from "./data/lemmatization.js";
import { pathways, sharedNotes, siteMeta } from "./data/site.js";
import { presuppositionsData } from "./data/presuppositions.js";
import { pronounData } from "./data/pronoun.js";
import { createDefaultState, loadState, resetPathwayState, saveState } from "./state.js";

const appRoot = document.getElementById("app");
const state = loadState();

const routeConfig = {
  lemmatization: {
    steps: [
      "intro",
      "benchmark",
      "predictions",
      "grid",
      "transition",
      "hardest",
      "subgroups",
      "conclusion",
    ],
  },
  pronoun: {
    steps: [
      "intro",
      "english-setup",
      "english-prompt",
      "english-reveal",
      "african-setup",
      "african-prompt",
      "african-results",
      "robustness",
      "conclusion",
    ],
  },
  presuppositions: {
    steps: [
      "intro",
      "challenge",
      "prompt-select",
      "reveal",
      "ranking",
      "why-p1",
      "balance",
      "conclusion",
    ],
  },
};

function ensureHash() {
  if (!window.location.hash) {
    window.location.hash = "#/home";
  }
}

function parseHash() {
  const hash = window.location.hash.replace(/^#\/?/, "");
  if (!hash || hash === "home") return { view: "home", step: null };
  const [view, step] = hash.split("/");
  return { view, step: step || null };
}

function setRoute(view, step = null) {
  state.route = { view, step };
  saveState(state);
  const hash = step ? `#/${view}/${step}` : `#/${view}`;
  if (window.location.hash === hash) {
    render();
  } else {
    window.location.hash = hash;
  }
}

function getThemeClass(view) {
  if (view === "lemmatization") return "theme-teal";
  if (view === "pronoun") return "theme-coral";
  if (view === "presuppositions") return "theme-gold";
  return "theme-home";
}

function getProgressLabel(pathwayId, step) {
  const steps = routeConfig[pathwayId].steps;
  const index = Math.max(steps.indexOf(step), 0) + 1;
  return `Step ${index} of ${steps.length}`;
}

function getPreviousStep(pathwayId) {
  const p = state[pathwayId];
  if (pathwayId === "lemmatization") {
    const prev = {
      benchmark: "intro",
      predictions: "benchmark",
      grid: "predictions",
      transition: "grid",
      hardest: "transition",
      subgroups: "hardest",
      conclusion: "subgroups",
    };
    return prev[p.step] || null;
  }

  if (pathwayId === "pronoun") {
    const prev = {
      "english-setup": "intro",
      "english-prompt": "english-setup",
      "english-reveal":
        p.englishRefineChoice === "yes" ? "english-prompt" : "english-setup",
      "african-setup": "english-reveal",
      "african-prompt": "african-setup",
      "african-results":
        p.africanPromptChoice === "yes" ? "african-prompt" : "african-setup",
      robustness: "african-results",
      conclusion: "robustness",
    };
    return prev[p.step] || null;
  }

  if (pathwayId === "presuppositions") {
    if (p.step === "challenge") return "intro";
    if (p.step === "prompt-select") return p.attempts.length ? "reveal" : "challenge";
    if (p.step === "reveal") return "prompt-select";
    if (p.step === "ranking") return "reveal";
    if (p.step === "why-p1") return "ranking";
    if (p.step === "balance") return "why-p1";
    if (p.step === "conclusion") return "balance";
  }

  return null;
}

function goBack(pathwayId) {
  const prev = getPreviousStep(pathwayId);
  if (!prev) {
    setRoute("home");
    return;
  }
  state[pathwayId].step = prev;
  setRoute(pathwayId, prev);
}

function renderHome() {
  const cards = pathways
    .map(
      (pathway) => `
        <article class="pathway-card pathway-card-${escapeHtml(pathway.accent)}">
          <div class="pathway-card-top">
            ${progressPill(pathway.eyebrow)}
            <h3>${escapeHtml(pathway.title)}</h3>
          </div>
          <p>${escapeHtml(pathway.short)}</p>
          ${button(pathway.cta, "open-pathway", { pathway: pathway.id })}
        </article>
      `,
    )
    .join("");

  const notes = sharedNotes
    .map((note) => `<li>${escapeHtml(note)}</li>`)
    .join("");

  return `
    <section class="home-hero">
      ${progressPill("Interactive Desktop Demo")}
      <h1>${escapeHtml(siteMeta.title)}</h1>
      <p class="hero-subtitle">${escapeHtml(siteMeta.subtitle)}</p>
      <div class="hero-note">
        <strong>What this demo does:</strong>
        <span>${escapeHtml(siteMeta.projectSummary)}</span>
      </div>
    </section>

    <section class="home-grid">
      <div class="home-main">
        <div class="pathway-grid">${cards}</div>
      </div>
      <aside class="home-sidebar">
        <section class="panel-card">
          <div class="panel-header">
            <h3>How It Works</h3>
            <p>Choose a pathway, make a few predictions, then compare them with the benchmark reveal.</p>
          </div>
          <ul class="note-list">${notes}</ul>
        </section>
      </aside>
    </section>
  `;
}

function renderLemmatization() {
  const p = state.lemmatization;
  const controls = pathwayControls({
    canBack: p.step !== "intro",
    pathwayId: "lemmatization",
  });

  const hero = `
    <section class="hero-card">
      <p class="hero-kicker">${escapeHtml(lemmatizationData.eyebrow)}</p>
      <h2>${escapeHtml(lemmatizationData.title)}</h2>
      <p>${escapeHtml(lemmatizationData.lesson)}</p>
    </section>
  `;

  let body = "";

  if (p.step === "intro") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>What Is Lemmatization?</h3>
          <p>Lemmatization is the task of reducing a word to its dictionary form, or lemma.</p>
        </div>
        <div class="example-row">
          ${lemmatizationData.introExamples
            .map(
              (example) => `
                <div class="example-chip">
                  <span>${escapeHtml(example.form)}</span>
                  <strong>${escapeHtml(example.lemma)}</strong>
                </div>
              `,
            )
            .join("")}
        </div>
        <div class="action-row">
          ${button("Continue", "set-step", {
            pathway: "lemmatization",
            step: "benchmark",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "benchmark") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>How Good Are LLMs at This?</h3>
          <p>Current state-of-the-art lemmatization performance is very high. Our best models get close to that level.</p>
        </div>
        <h4 class="question-label">Do you think LLMs can match state-of-the-art accuracy?</h4>
        <div class="binary-row">
          ${choiceCard({
            label: "Yes",
            body: "",
            selected: p.benchmarkGuess === "yes",
            action: "set-guess",
            extra: { pathway: "lemmatization", key: "benchmarkGuess", value: "yes" },
          })}
          ${choiceCard({
            label: "No",
            body: "",
            selected: p.benchmarkGuess === "no",
            action: "set-guess",
            extra: { pathway: "lemmatization", key: "benchmarkGuess", value: "no" },
          })}
        </div>
        <div class="action-row">
          ${button("Next", "set-step", {
            pathway: "lemmatization",
            step: "predictions",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "predictions") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>What Do You Think Will Matter?</h3>
          <p>Make two quick predictions before you open the results grid.</p>
        </div>
        <div class="question-block">
          <h4>Do you think model choice will matter?</h4>
          <div class="binary-row">
            ${choiceCard({
              label: "Yes",
              body: "",
              selected: p.modelChoiceGuess === "yes",
              action: "set-guess",
              extra: { pathway: "lemmatization", key: "modelChoiceGuess", value: "yes" },
            })}
            ${choiceCard({
              label: "No",
              body: "",
              selected: p.modelChoiceGuess === "no",
              action: "set-guess",
              extra: { pathway: "lemmatization", key: "modelChoiceGuess", value: "no" },
            })}
          </div>
        </div>
        <div class="question-block">
          <h4>Do you think batch size will matter?</h4>
          <div class="binary-row">
            ${choiceCard({
              label: "Yes",
              body: "",
              selected: p.batchSizeGuess === "yes",
              action: "set-guess",
              extra: { pathway: "lemmatization", key: "batchSizeGuess", value: "yes" },
            })}
            ${choiceCard({
              label: "No",
              body: "",
              selected: p.batchSizeGuess === "no",
              action: "set-guess",
              extra: { pathway: "lemmatization", key: "batchSizeGuess", value: "no" },
            })}
          </div>
        </div>
        <div class="action-row">
          ${button("Reveal The Grid", "set-step", {
            pathway: "lemmatization",
            step: "grid",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "grid") {
    // Find min/max of all revealed cells for progressive color intensity
    const revealedScores = p.revealedCells.map((key) => {
      const [modelId, batch] = key.split(/-(\d+)$/);
      return lemmatizationData.grid[modelId]?.[batch] ?? 0;
    });
    const revMin = revealedScores.length ? Math.min(...revealedScores) : 0;
    const revMax = revealedScores.length ? Math.max(...revealedScores) : 1;
    const revRange = revMax - revMin || 0.01;

    // Find the best score among revealed cells
    const bestRevealed = revealedScores.length ? Math.max(...revealedScores) : null;

    const cells = lemmatizationData.models
      .map((model) => {
        const row = lemmatizationData.batchSizes
          .map((batch) => {
            const key = `${model.id}-${batch}`;
            const revealed = p.revealedCells.includes(key);
            const score = lemmatizationData.grid[model.id][batch];
            // Color intensity: green for high, muted for low (only among revealed)
            const intensity = revealed ? Math.round(((score - revMin) / revRange) * 100) : 0;
            const isBestRevealed = revealed && p.revealedCells.length >= 3 && score === bestRevealed;
            return `
              <button
                class="grid-cell ${revealed ? "grid-cell-revealed" : ""} ${isBestRevealed ? "grid-cell-best" : ""}"
                data-action="toggle-grid-cell"
                data-pathway="lemmatization"
                data-model="${escapeHtml(model.id)}"
                data-batch="${batch}"
                ${revealed ? `style="--cell-intensity: ${intensity}%"` : ""}
              >
                <span class="grid-meta">n = ${batch}</span>
                ${
                  revealed
                    ? `<strong>${formatPercent(score, 1)}</strong>${isBestRevealed ? "<small>Best revealed</small>" : ""}`
                    : `<strong>?</strong><small>Click to reveal</small>`
                }
              </button>
            `;
          })
          .join("");

        return `
          <div class="grid-row">
            <div class="grid-label">
              <strong>${escapeHtml(model.label)}</strong>
              <span>${escapeHtml(model.personality)}</span>
            </div>
            <div class="grid-cells">${row}</div>
          </div>
        `;
      })
      .join("");

    const revealReady = p.revealedCells.length >= 3;
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>Performance Grid</h3>
          <p>Click cells to reveal accuracy scores. Can you find the best run? Reveal at least 3 to continue.</p>
        </div>
        <div class="grid-note">The state-of-the-art metric for this task is <strong>accuracy</strong>.</div>
        <div class="grid-board">${cells}</div>
        ${revealReady ? `
        <div class="callout-banner">
          <strong>${escapeHtml(lemmatizationData.modelTakeaway)}</strong>
          <span>Some models peak higher. Others are more dependable across different batch sizes.</span>
        </div>` : ""}
        <div class="action-row">
          ${
            revealReady
              ? button("Continue", "set-step", {
                  pathway: "lemmatization",
                  step: "transition",
                })
              : `<button class="button" disabled>Reveal ${3 - p.revealedCells.length} more cell${3 - p.revealedCells.length === 1 ? "" : "s"} to continue</button>`
          }
        </div>
      </section>
    `;
  }

  if (p.step === "transition") {
    body = `
      <section class="panel-card center-card">
        <div class="panel-header">
          <h3>Why Do Certain Models Perform Better or Worse?</h3>
          <p>The performance differences you just saw are not random. They are mostly driven by how well each model handles <strong>edge cases</strong> — the harder categories of lemmatization where regular patterns break down.</p>
        </div>
        <div class="action-row">
          ${button("Explore The Edge Cases", "set-step", {
            pathway: "lemmatization",
            step: "hardest",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "hardest") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>${escapeHtml(lemmatizationData.subgroupQuestion.title)}</h3>
          <p>Pick the subgroup you think stays hardest even when overall accuracy looks good.</p>
        </div>
        <div class="option-grid">
          ${lemmatizationData.subgroupQuestion.options
            .map((option) =>
              choiceCard({
                label: option.label,
                body: option.example,
                selected: p.hardestGuess === option.id,
                action: "set-guess",
                extra: { pathway: "lemmatization", key: "hardestGuess", value: option.id },
              }),
            )
            .join("")}
        </div>
        <div class="action-row">
          ${
            p.hardestGuess
              ? button("Show Subgroup Results", "set-step", {
                  pathway: "lemmatization",
                  step: "subgroups",
                })
              : `<button class="button" disabled>Choose a category first</button>`
          }
        </div>
      </section>
    `;
  }

  if (p.step === "subgroups") {
    const userGuessedRight = p.hardestGuess === "irregular";
    const rows = lemmatizationData.subgroupTable
      .map((row) => {
        const values = lemmatizationData.subgroupCategories
          .map((category) => {
            const value = row[category];
            const hardest = category === "irregular";
            return `
              <td class="${hardest ? "hardest-cell" : ""}">
                <div class="score-bar">
                  <span style="width:${Math.round(value * 100)}%"></span>
                  <strong>${formatPercent(value, 1)}</strong>
                </div>
              </td>
            `;
          })
          .join("");
        return `
          <tr>
            <th>${escapeHtml(row.model)}<span>n = ${row.batchSize}</span></th>
            ${values}
          </tr>
        `;
      })
      .join("");

    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>Structured Weakness By Lemma Type</h3>
          <p>${escapeHtml(lemmatizationData.subgroupSliceLabel)}</p>
        </div>
        <table class="results-table subgroup-table">
          <thead>
            <tr>
              <th>Model</th>
              <th>Easy</th>
              <th>Changed</th>
              <th>Ambiguous</th>
              <th>Rare</th>
              <th>Irregular</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
        <div class="callout-banner">
          <strong>${userGuessedRight ? "Nice call" : "The surprise"}</strong>
          <span>
            ${
              userGuessedRight
                ? "Irregular forms are the toughest category across all models in this shared comparison."
                : "The hardest cases are not just the rare ones. Irregular forms are the weakest subgroup across every model in this shared comparison."
            }
          </span>
        </div>
        <p class="note-text">The models are not failing randomly. Their remaining weakness is concentrated in specific kinds of lemmas.</p>
        <div class="action-row">
          ${button("Why This Matters", "set-step", {
            pathway: "lemmatization",
            step: "conclusion",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "conclusion") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>Why This Matters</h3>
          <p>LLMs are already highly usable for lemmatization. But even for this reliable task, accuracy can't be quite perfect — and the remaining errors are concentrated, not random.</p>
        </div>
        <div class="summary-stack">
          ${metricCard("Main remaining weakness", "Irregular lemmatization", "non-standard mappings like went -> go")}
          ${metricCard("Mitigation: lookup dictionary", "Splice in a dictionary of known irregular lemmas", "catch errors the model misses at inference time")}
          ${metricCard("Mitigation: targeted training", "More model development on irregular forms", "improve the model's coverage of non-standard patterns")}
        </div>
        <div class="callout-banner">
          <strong>The bottom line</strong>
          <span>LLMs are useful for lemmatization right now — but irregular forms need extra attention. A hybrid approach (LLM + irregular-lemma dictionary) is the most practical path to near-perfect accuracy.</span>
        </div>
        <div class="action-row">
          ${button("Return Home", "go-home")}
        </div>
      </section>
    `;
  }

  return pathwayFrame({
    title: lemmatizationData.title,
    eyebrow: lemmatizationData.eyebrow,
    progressLabel: getProgressLabel("lemmatization", p.step),
    controlsHtml: controls,
    heroHtml: hero,
    bodyHtml: body,
  });
}

function renderPronoun() {
  const p = state.pronoun;
  const controls = pathwayControls({
    canBack: p.step !== "intro",
    pathwayId: "pronoun",
  });
  const hero = `
    <section class="hero-card">
      <p class="hero-kicker">${escapeHtml(pronounData.eyebrow)}</p>
      <h2>${escapeHtml(pronounData.title)}</h2>
      <p>Prompt engineering is not universally helpful. The real lesson is when prompt sensitivity becomes a robustness clue.</p>
    </section>
  `;

  let body = "";

  if (p.step === "intro") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>What Is Pronoun Resolution?</h3>
          <p>Pronoun resolution is the task of deciding which noun a pronoun refers to in context.</p>
        </div>
        <div class="quote-card">
          <p>${escapeHtml(pronounData.introExample.sentence)}</p>
          <strong>${escapeHtml(pronounData.introExample.question)}</strong>
        </div>
        <p class="note-text">These cases can look easy, but the hardest ones depend on syntax, semantics, and plausibility.</p>
        <div class="action-row">
          ${button("Continue", "set-step", {
            pathway: "pronoun",
            step: "english-setup",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "english-setup") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>English Baseline</h3>
          <p>You're using <strong>${escapeHtml(pronounData.englishSetup.model)}</strong> to evaluate the <strong>${escapeHtml(pronounData.englishSetup.dataset)}</strong>.</p>
        </div>
        <div class="callout-banner callout-banner-prominent">
          <strong>Your goal is to meet a state-of-the-art target of 0.89.</strong>
          <span>According to OpenAI's own benchmarking, that's the performance bar for this English benchmark.</span>
        </div>
        <div class="question-focus">
          <strong>Do you want to refine your prompt?</strong>
        </div>
        <div class="binary-row">
          ${choiceCard({
            label: "Yes",
            body: "Let me optimize the prompt.",
            selected: p.englishRefineChoice === "yes",
            action: "set-guess",
            extra: { pathway: "pronoun", key: "englishRefineChoice", value: "yes" },
          })}
          ${choiceCard({
            label: "No",
            body: "Run the baseline directly.",
            selected: p.englishRefineChoice === "no",
            action: "set-guess",
            extra: { pathway: "pronoun", key: "englishRefineChoice", value: "no" },
          })}
        </div>
        <div class="action-row">
          ${
            p.englishRefineChoice === "yes"
              ? button("Pick A Prompt", "set-step", {
                  pathway: "pronoun",
                  step: "english-prompt",
                })
              : p.englishRefineChoice === "no"
                ? button("Show Results", "run-pronoun-english")
                : `<button class="button" disabled>Choose yes or no first</button>`
          }
        </div>
      </section>
    `;
  }

  if (p.step === "english-prompt") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>Pick a Prompt</h3>
          <p>Choose one of the available pronoun-resolution prompts.</p>
        </div>
        <div class="option-grid">
          ${pronounData.promptOptions
            .map((option) =>
              choiceCard({
                label: `${option.label} · ${option.family}`,
                body: option.description,
                selected: p.englishPromptDraft === option.id,
                action: "set-guess",
                extra: { pathway: "pronoun", key: "englishPromptDraft", value: option.id },
              }),
            )
            .join("")}
        </div>
        <div class="action-row">
          ${
            p.englishPromptDraft
              ? button("Run Evaluation", "run-pronoun-english")
              : `<button class="button" disabled>Select a prompt first</button>`
          }
        </div>
      </section>
    `;
  }

  if (p.step === "english-reveal") {
    const headlineText = p.englishPrompt
      ? "Good try...but Prompt engineering made no difference here."
      : "Prompt engineering made no difference here.";
    body = `
      <section class="panel-card">
        <div class="callout-banner callout-banner-prominent callout-center">
          <strong>${escapeHtml(headlineText)}</strong>
          <span>In this English Sonnet 4.6 setup, prompt choice did not change the outcome. The results below are the same regardless of which prompt you use.</span>
        </div>
        <div class="panel-header">
          <h3>English Baseline Results</h3>
          <p>Performance across sample sizes — all prompt variants converge to the same scores.</p>
        </div>
        <div class="metric-row">
          ${pronounData.englishSetup.results
            .map((result) => metricCard(`n = ${result.n}`, formatPercent(result.accuracy, 1)))
            .join("")}
        </div>
        <p class="note-text">For a well-defined English pronoun-resolution task, Sonnet 4.6 is already operating in a stable enough regime that prompt variation does not change performance.</p>
        <div class="action-row">
          ${button("Continue", "set-step", {
            pathway: "pronoun",
            step: "african-setup",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "african-setup") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>New Challenge</h3>
          <p>Now you're baselining three lower-resource African languages: Amharic, Zulu, and Igbo.</p>
        </div>
        <div class="binary-row">
          ${choiceCard({
            label: "Yes",
            body: "Let me choose one prompt for all three.",
            selected: p.africanPromptChoice === "yes",
            action: "set-guess",
            extra: { pathway: "pronoun", key: "africanPromptChoice", value: "yes" },
          })}
          ${choiceCard({
            label: "No",
            body: "Baseline prompt performance should be sufficient.",
            selected: p.africanPromptChoice === "no",
            action: "set-guess",
            extra: { pathway: "pronoun", key: "africanPromptChoice", value: "no" },
          })}
        </div>
        <div class="action-row">
          ${
            p.africanPromptChoice === "yes"
              ? button("Pick A Prompt", "set-step", {
                  pathway: "pronoun",
                  step: "african-prompt",
                })
              : p.africanPromptChoice === "no"
                ? button("Show Results", "run-pronoun-african")
                : `<button class="button" disabled>Choose yes or no first</button>`
          }
        </div>
      </section>
    `;
  }

  if (p.step === "african-prompt") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>Pick a Prompt</h3>
          <p>Choose one prompt to use across these lower-resource pronoun-resolution settings.</p>
        </div>
        <div class="option-grid">
          ${pronounData.promptOptions
            .map((option) =>
              choiceCard({
                label: `${option.label} · ${option.family}`,
                body: option.description,
                selected: p.africanPromptDraft === option.id,
                action: "set-guess",
                extra: { pathway: "pronoun", key: "africanPromptDraft", value: option.id },
              }),
            )
            .join("")}
        </div>
        <div class="action-row">
          ${
            p.africanPromptDraft
              ? button("Show Results", "run-pronoun-african")
              : `<button class="button" disabled>Select a prompt first</button>`
          }
        </div>
      </section>
    `;
  }

  if (p.step === "african-results") {
    const tables = Object.entries(pronounData.lowResourceResults)
      .map(([language, rows]) => {
        const tableRows = rows
          .map((row, index) => {
            const highlight = row.prompt === p.africanPrompt;
            return `
              <tr class="${highlight ? "table-row-highlight" : ""}">
                <td>${row.prompt}</td>
                <td>${formatPercent(row.accuracy, 1)}</td>
                <td>${formatDecimal(row.macroF1, 4)}</td>
                <td>${index === 0 ? "<span class='mini-badge'>Best F1</span>" : ""}</td>
              </tr>
            `;
          })
          .join("");
        const selectedRow = rows.findIndex((row) => row.prompt === p.africanPrompt);
        return tableCard(
          language,
          p.africanPrompt
            ? `Your chosen prompt ranked #${selectedRow + 1 || "—"} for this language.`
            : "Here's how the prompts actually ranked.",
          `
            <table class="results-table">
              <thead>
                <tr>
                  <th>Prompt</th>
                  <th>Accuracy</th>
                  <th>Macro-F1</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>${tableRows}</tbody>
            </table>
          `,
        );
      })
      .join("");

    body = `
      <section class="table-layout">${tables}</section>
      <section class="panel-card pivot-card">
        <div class="panel-header">
          <h3 class="pivot-heading">What Changed?</h3>
          <p>Unlike the English baseline, prompt choice now produces <strong>real variation</strong>. The best prompt is not identical across all three languages, which means the model is <strong>likely</strong> less stable in these lower-resource settings.</p>
        </div>
        <p class="note-text"><strong>Why do prompts matter here but not in English?</strong> Let's look at the bigger pattern.</p>
        <div class="action-row">
          ${button("See The Pattern", "set-step", {
            pathway: "pronoun",
            step: "robustness",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "robustness") {
    const max = Math.max(...pronounData.robustness.map((item) => item.value));
    const scaleMarks = [0, 0.01, 0.02, 0.03];
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>Prompt Sensitivity Across Language Benchmarks</h3>
          <p>How much does prompt choice change the result? We measured the <strong>standard deviation of Macro-F1</strong> across prompts P0–P4 for each language.</p>
        </div>
        <div class="sensitivity-explanation">
          <span>Lower = more stable</span>
          <span>Higher = more sensitive to prompt choice</span>
        </div>
        <div class="sensitivity-chart">
          <div class="sensitivity-scale">
            ${scaleMarks.map((m) => `<div class="sensitivity-tick" style="left:${(m / 0.035) * 100}%"><span>${m}</span></div>`).join("")}
          </div>
          ${pronounData.robustness
            .map((item) => {
              const width = max === 0 ? 0 : Math.max(4, Math.round((item.value / 0.035) * 100));
              const isHigh = item.value >= 0.02;
              return `
                <div class="sensitivity-row">
                  <div class="sensitivity-label">
                    <strong>${escapeHtml(item.language)}</strong>
                  </div>
                  <div class="sensitivity-bar-track">
                    <div class="sensitivity-bar ${isHigh ? "sensitivity-bar-high" : ""}" style="width:${width}%"></div>
                    <span class="sensitivity-value">${formatDecimal(item.value, 4)}</span>
                  </div>
                </div>
              `;
            })
            .join("")}
        </div>
        <p class="fine-print">*These values are for Claude Sonnet 4.6 only. Different models, trained differently, may behave differently.</p>
        <div class="callout-banner callout-banner-prominent">
          <strong>For Claude Sonnet 4.6, prompt sensitivity increases as we move into lower-resource settings.</strong>
          <span>That suggests these task environments are less stable under simple prompting choices.</span>
          <span>In a stable English benchmark setting, changing the prompt did nothing. In lower-resource settings, prompt choice mattered much more. Prompt sensitivity can itself be a clue about model robustness.</span>
        </div>
        <div class="action-row">
          ${button("Return Home", "go-home")}
        </div>
      </section>
    `;
  }

  if (p.step === "conclusion") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>Why This Matters</h3>
          <p>This demo shows that prompt engineering is not always equally useful.</p>
        </div>
        <ul class="note-list">
          <li>In a stable English benchmark setting, changing the prompt did nothing.</li>
          <li>In lower-resource settings, prompt choice started to matter much more.</li>
          <li>Prompt sensitivity can itself be a clue about model robustness.</li>
        </ul>
        <p class="note-text"><strong>A strong English result does not automatically mean robust multilingual pronoun resolution.</strong></p>
        <div class="action-row">
          ${button("Return Home", "go-home")}
        </div>
      </section>
    `;
  }

  return pathwayFrame({
    title: pronounData.title,
    eyebrow: pronounData.eyebrow,
    progressLabel: getProgressLabel("pronoun", p.step),
    controlsHtml: controls,
    heroHtml: hero,
    bodyHtml: body,
  });
}

function renderPresuppositions() {
  const p = state.presuppositions;
  const controls = pathwayControls({
    canBack: p.step !== "intro",
    pathwayId: "presuppositions",
  });
  const hero = `
    <section class="hero-card">
      <p class="hero-kicker">${escapeHtml(presuppositionsData.eyebrow)}</p>
      <h2>${escapeHtml(presuppositionsData.title)}</h2>
      <p>The strongest prompt here is the one with benchmark-aligned few-shot examples and probability output — not the most theoretical one.</p>
    </section>
  `;

  let body = "";

  if (p.step === "intro") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>What Is Presupposition?</h3>
          <p>Presupposition is what a sentence takes for granted.</p>
        </div>
        <div class="example-stack">
          ${presuppositionsData.introExamples
            .map(
              (example) => `
                <div class="quote-card">
                  <p>${escapeHtml(example.premise)}</p>
                  <strong>${escapeHtml(example.presupposition)}</strong>
                </div>
              `,
            )
            .join("")}
        </div>
        <p class="note-text">In this benchmark, the model decides whether a premise entails, is neutral toward, or contradicts a presupposed hypothesis.</p>
        <div class="action-row">
          ${button("Continue", "set-step", {
            pathway: "presuppositions",
            step: "challenge",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "challenge") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>Can We Beat the Benchmark?</h3>
          <p>You're working on <strong>${escapeHtml(presuppositionsData.challenge.benchmark)}</strong>, a benchmark for presupposition reasoning. Here is the baseline result for <strong>Chat 5.4</strong>:</p>
        </div>
        <div class="metric-row">
          ${metricCard("Model", "Chat 5.4")}
          ${metricCard("Prompt", presuppositionsData.challenge.baselinePrompt)}
          ${metricCard("Accuracy", formatDecimal(presuppositionsData.challenge.accuracy, 4))}
          ${metricCard("Macro-F1", formatDecimal(presuppositionsData.challenge.macroF1, 4))}
        </div>
        <p class="note-text">Can you pick a prompt strategy that does better?</p>
        <div class="action-row">
          ${button("Let's Try", "set-step", {
            pathway: "presuppositions",
            step: "prompt-select",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "prompt-select") {
    const attemptNumber = p.attempts.length + 1;
    const triedPrompts = new Set(p.attempts.map((a) => a.promptId));
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>Pick a Prompt Strategy</h3>
          <p>Attempt ${attemptNumber} of 3</p>
        </div>
        <div class="option-grid option-grid-wide">
          ${presuppositionsData.promptCards
            .map((card) => {
              const alreadyTried = triedPrompts.has(card.id);
              return choiceCard({
                label: `${card.id} · ${card.family}`,
                body: card.description,
                selected: p.promptDraft === card.id,
                disabled: alreadyTried,
                disabledLabel: "Already tried",
                action: "set-guess",
                extra: { pathway: "presuppositions", key: "promptDraft", value: card.id },
              });
            })
            .join("")}
        </div>
        <div class="action-row">
          ${
            p.promptDraft && !triedPrompts.has(p.promptDraft)
              ? button("Run Prompt", "run-presupposition-prompt")
              : `<button class="button" disabled>Select a prompt first</button>`
          }
        </div>
      </section>
    `;
  }

  if (p.step === "reveal") {
    const latest = p.attempts[p.attempts.length - 1];
    const result = presuppositionsData.prompts[latest.promptId];
    const attemptLabel =
      p.attempts.length === 1
        ? "You've learned something about what this benchmark needs. Want to try again?"
        : p.attempts.length === 2
          ? "You're getting closer. Some prompts teach the boundary better than others."
          : "One last try. Can you find the strongest overall strategy?";

    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>${escapeHtml(latest.promptId)} Reveal</h3>
          <p>${escapeHtml(result.family)} · ${escapeHtml(result.outputType)}</p>
        </div>
        <div class="metric-row">
          ${metricCard("Accuracy", formatDecimal(result.accuracy, 4))}
          ${metricCard("Macro-F1", formatDecimal(result.macroF1, 4))}
          ${metricCard("F1-E", formatDecimal(result.f1E, 4))}
          ${metricCard("F1-N", formatDecimal(result.f1N, 4))}
          ${metricCard("F1-C", formatDecimal(result.f1C, 4))}
          ${metricCard("Log Loss", result.logLoss == null ? "—" : formatDecimal(result.logLoss, 4))}
          ${metricCard("Brier", result.brier == null ? "—" : formatDecimal(result.brier, 4))}
        </div>
        <div class="analysis-card">
          <strong>Interpretation</strong>
          <p>${escapeHtml(result.interpretation)}</p>
        </div>
        <div class="analysis-card analysis-card-soft">
          <strong>Hint</strong>
          <p>${escapeHtml(result.hint)}</p>
        </div>
        <div class="action-row">
          ${
            p.attempts.length < 3
              ? button("Try Another Prompt", "set-step", {
                  pathway: "presuppositions",
                  step: "prompt-select",
                })
              : button("See The Full Ranking", "set-step", {
                  pathway: "presuppositions",
                  step: "ranking",
                })
          }
        </div>
        <p class="fine-print">${escapeHtml(attemptLabel)}</p>
      </section>
    `;
  }

  if (p.step === "ranking") {
    const picked = new Set(p.attempts.map((attempt) => attempt.promptId));
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>Full Prompt Ranking</h3>
          <p>Macro-F1 on the Chat 5.4 CONFER English slice.</p>
        </div>
        <table class="results-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Prompt</th>
              <th>Macro-F1</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            ${presuppositionsData.ranking
              .map(
                (row, index) => `
                  <tr class="${picked.has(row.prompt) ? "table-row-highlight" : ""}">
                    <td>${index + 1}</td>
                    <td>${row.prompt}</td>
                    <td>${formatDecimal(row.macroF1, 4)}</td>
                    <td>${row.badge ? `<span class="mini-badge">${row.badge}</span>` : ""}</td>
                  </tr>
                `,
              )
              .join("")}
          </tbody>
        </table>
        <div class="action-row">
          ${button("Why Does P1 Work?", "set-step", {
            pathway: "presuppositions",
            step: "why-p1",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "why-p1") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>Why Does P1 Work Best?</h3>
          <p>P1 includes <strong>three worked examples</strong> — one for each class (Entailment, Neutral, Contradiction) — drawn from the CONFER dataset's specific context: presupposition projection through negation, conditionals, and questions.</p>
        </div>
        <div class="metric-row">
          ${metricCard("Key gain: Neutral F1", "0.49 → 0.69", "P0 → P1: +41% on the hardest class")}
          ${metricCard("Why examples help", "Label conventions", "CONFER's labels don't follow generic NLI rules")}
          ${metricCard("Why probabilities help", "Preserves uncertainty", "Hard-label P10 collapses Neutral F1 to 0.23")}
        </div>
        <div class="analysis-card">
          <strong>Concrete examples beat abstract rules</strong>
          <p>Without examples (P0), the model conflates Neutral with Entailment — it doesn't know what "unresolved presupposition" looks like in this benchmark. P1's three examples directly show the label boundaries: how a presupposition survives negation (E), how it gets suspended in a conditional (N), and how it can be incompatible with context (C).</p>
        </div>
        <div class="analysis-card analysis-card-soft">
          <strong>Why heavier prompts fail</strong>
          <p>Abstract rules (P2's guarantee-based NLI) and linguistic definitions (P7's projection-aware framing) can't capture CONFER's specific labeling conventions. P4–P6 actively confuse the model — their multi-step decompositions push accuracy below 50%. More scaffolding is not better when the scaffold doesn't match the benchmark's label geometry.</p>
        </div>
        <div class="action-row">
          ${button("Show Class Balance", "set-step", {
            pathway: "presuppositions",
            step: "balance",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "balance") {
    const cards = presuppositionsData.classBalance
      .map(
        (item) => `
          <div class="class-card">
            <h4>${escapeHtml(item.label)}</h4>
            <div class="class-bars">
              <div><span>E</span><strong>${formatDecimal(item.f1E, 4)}</strong><i style="width:${Math.round(item.f1E * 100)}%"></i></div>
              <div><span>N</span><strong>${formatDecimal(item.f1N, 4)}</strong><i style="width:${Math.round(item.f1N * 100)}%"></i></div>
              <div><span>C</span><strong>${formatDecimal(item.f1C, 4)}</strong><i style="width:${Math.round(item.f1C * 100)}%"></i></div>
            </div>
          </div>
        `,
      )
      .join("");

    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>How Balanced Is the Best Prompt?</h3>
          <p>Even strong systems make tradeoffs across Entailment, Neutral, and Contradiction.</p>
        </div>
        <div class="class-grid">${cards}</div>
        <p class="fine-print">*These prompt-benchmarking results are from an n = 300 CONFER English evaluation slice. They show strong prompt effects, but they are not meant to claim that P1 definitively beats full-dataset SOTA across the entire benchmark.</p>
        <div class="action-row">
          ${button("Why This Matters", "set-step", {
            pathway: "presuppositions",
            step: "conclusion",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "conclusion") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>Why This Matters</h3>
          <p>This demo shows that prompt engineering is part of the method — and that more is not always better.</p>
        </div>
        <ul class="note-list">
          <li>P1 won because its three worked examples taught the model CONFER's specific label conventions — especially the Entailment/Neutral boundary that other prompts collapsed.</li>
          <li>Probability output preserved the model's uncertainty structure. Hard labels destroyed it.</li>
          <li>Abstract rules and linguistic definitions couldn't capture what concrete examples could.</li>
        </ul>
        <div class="callout-banner">
          <strong>The practical lesson</strong>
          <span>For novel semantic tasks, benchmark-aligned few-shot examples with probability output beat both minimal prompting and heavy-scaffolded reasoning chains.</span>
        </div>
        <div class="action-row">
          ${button("Return Home", "go-home")}
        </div>
      </section>
    `;
  }

  return pathwayFrame({
    title: presuppositionsData.title,
    eyebrow: presuppositionsData.eyebrow,
    progressLabel: getProgressLabel("presuppositions", p.step),
    controlsHtml: controls,
    heroHtml: hero,
    bodyHtml: body,
  });
}

function render() {
  const route = parseHash();
  state.route = route;
  saveState(state);

  let content = "";
  if (route.view === "home") {
    content = renderHome();
  } else if (route.view === "lemmatization") {
    if (!route.step) {
      state.lemmatization.step = "intro";
      setRoute("lemmatization", "intro");
      return;
    }
    state.lemmatization.step = route.step;
    content = renderLemmatization();
  } else if (route.view === "pronoun") {
    if (!route.step) {
      state.pronoun.step = "intro";
      setRoute("pronoun", "intro");
      return;
    }
    state.pronoun.step = route.step;
    content = renderPronoun();
  } else if (route.view === "presuppositions") {
    if (!route.step) {
      state.presuppositions.step = "intro";
      setRoute("presuppositions", "intro");
      return;
    }
    state.presuppositions.step = route.step;
    content = renderPresuppositions();
  } else {
    setRoute("home");
    return;
  }

  appRoot.innerHTML = shell({
    themeClass: getThemeClass(route.view),
    homeHtml: route.view === "home" ? "" : "",
    contentHtml: content,
  });
}

function runPronounEnglish() {
  if (state.pronoun.englishRefineChoice === "yes") {
    state.pronoun.englishPrompt = state.pronoun.englishPromptDraft;
  } else {
    state.pronoun.englishPrompt = null;
  }
  state.pronoun.step = "english-reveal";
  setRoute("pronoun", "english-reveal");
}

function runPronounAfrican() {
  if (state.pronoun.africanPromptChoice === "yes") {
    state.pronoun.africanPrompt = state.pronoun.africanPromptDraft;
  } else {
    state.pronoun.africanPrompt = null;
  }
  state.pronoun.step = "african-results";
  setRoute("pronoun", "african-results");
}

function runPresuppositionPrompt() {
  const promptId = state.presuppositions.promptDraft;
  if (!promptId) return;
  state.presuppositions.attempts.push({ promptId });
  state.presuppositions.step = "reveal";
  setRoute("presuppositions", "reveal");
}

function toggleGridCell(model, batch) {
  const key = `${model}-${batch}`;
  const cells = state.lemmatization.revealedCells;
  if (!cells.includes(key)) {
    cells.push(key);
  }
  saveState(state);
  render();
}

function handleAction(target) {
  const action = target.dataset.action;
  if (!action || action === "noop") return;

  if (action === "go-home") {
    setRoute("home");
    return;
  }

  if (action === "open-pathway") {
    const pathway = target.dataset.pathway;
    if (pathway === "lemmatization") setRoute("lemmatization", "intro");
    if (pathway === "pronoun") setRoute("pronoun", "intro");
    if (pathway === "presuppositions") setRoute("presuppositions", "intro");
    return;
  }

  if (action === "restart-pathway") {
    const pathway = target.dataset.pathway;
    resetPathwayState(state, pathway);
    const firstStep = createDefaultState()[pathway].step;
    setRoute(pathway, firstStep);
    return;
  }

  if (action === "go-back") {
    goBack(target.dataset.pathway);
    return;
  }

  if (action === "set-step") {
    const { pathway, step } = target.dataset;
    // Clear draft when re-entering prompt-select
    if (pathway === "presuppositions" && step === "prompt-select") {
      state.presuppositions.promptDraft = null;
    }
    state[pathway].step = step;
    setRoute(pathway, step);
    return;
  }

  if (action === "set-guess") {
    const { pathway, key, value } = target.dataset;
    state[pathway][key] = value;
    saveState(state);
    render();
    return;
  }

  if (action === "toggle-grid-cell") {
    toggleGridCell(target.dataset.model, target.dataset.batch);
    return;
  }

  if (action === "run-pronoun-english") {
    runPronounEnglish();
    return;
  }

  if (action === "run-pronoun-african") {
    runPronounAfrican();
    return;
  }

  if (action === "run-presupposition-prompt") {
    runPresuppositionPrompt();
  }
}

appRoot.addEventListener("click", (event) => {
  const target = event.target.closest("[data-action]");
  if (!target) return;
  handleAction(target);
});

window.addEventListener("hashchange", render);

ensureHash();
render();
