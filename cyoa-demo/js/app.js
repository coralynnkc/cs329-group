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
import { pathways, siteMeta } from "./data/site.js";
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
      "bridge",
      "pos-intro",
      "pos-reveal",
      "pos-tags",
      "pos-decomposition",
      "ner-reveal",
      "narnia-labels",
      "narnia-benchmark-predict",
      "narnia-benchmark",
      "narnia-child",
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
    const steps = routeConfig.lemmatization.steps;
    const index = steps.indexOf(p.step);
    return index > 0 ? steps[index - 1] : null;
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

  return `
    <section class="home-hero">
      ${progressPill("Interactive Demo")}
      <h1>${escapeHtml(siteMeta.title)}</h1>
      <p class="hero-subtitle">${escapeHtml(siteMeta.subtitle)}</p>
    </section>

    <section class="home-grid">
      <div class="home-main">
        <div class="pathway-grid">${cards}</div>
      </div>
      <aside class="home-sidebar">
        <section class="panel-card">
          <div class="panel-header">
            <h3>How It Works</h3>
            <p>How good are you at predicting LLM performance? Choose a pathway, test your intuition, and learn about linguistics and LLM applications!</p>
            <p>Don't know where to start? Enter the Wardrobe and take the pathway to Narnia!</p>
          </div>
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
  const scoreToneClass = (value, thresholds = {}) => {
    const { high = 0.9, medium = 0.8, low = 0.65 } = thresholds;
    if (value >= high) return "score-chip-high";
    if (value >= medium) return "score-chip-medium";
    if (value >= low) return "score-chip-warm";
    return "score-chip-low";
  };
  const posHardTagHits = lemmatizationData.pos.actualHardestTags.filter((tag) =>
    p.posHardTagGuesses.includes(tag),
  );
  const narniaQuizCorrect =
    p.narniaLabelGuess && p.narniaLabelGuess === lemmatizationData.narnia.quiz.correct;

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
          <p>${escapeHtml(lemmatizationData.benchmarkPrompt)}</p>
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
          <span>Generally, all these models do well and hover around the same performance metrics. Some models have better one-off performance. Others are more dependable across different batch sizes.</span>
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
          <p>The performance differences you just saw are not only randomness. They are largely driven by how well each model handles <strong>edge cases</strong> — the harder categories of lemmatization where regular patterns break down.</p>
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
          <strong>${userGuessedRight ? "Nice call" : "Non-Standard Categories Drive Performance Differentials"}</strong>
          <span>
            ${
              userGuessedRight
                ? "Irregular forms are the toughest category across all models in this shared comparison."
                : "Irregular lemmatization is clearly the hardest category. It's also statistically uncommon. But when models already perform well, the edge cases (ie. irregular forms) tend to define top-tier performance."
            }
          </span>
        </div>
        <p class="note-text">The models are not failing randomly. The failures are concentrated in specific types of lemmas.</p>
        <div class="action-row">
          ${button("Zoom Out", "set-step", {
            pathway: "lemmatization",
            step: "bridge",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "bridge") {
    body = `
      <section class="panel-card center-card">
        <div class="panel-header">
          <h3>${escapeHtml(lemmatizationData.bridge.title)}</h3>
          <p>${escapeHtml(lemmatizationData.bridge.body)}</p>
        </div>
        <div class="concept-grid">
          ${lemmatizationData.bridge.concepts
            .map(
              (concept) => `
                <article class="concept-card">
                  <h4>${escapeHtml(concept.title)}</h4>
                  <p>${escapeHtml(concept.body)}</p>
                </article>
              `,
            )
            .join("")}
        </div>
        <div class="action-row">
          ${button("Try Task Decomposition", "set-step", {
            pathway: "lemmatization",
            step: "pos-intro",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "pos-intro") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>${escapeHtml(lemmatizationData.pos.title)}</h3>
          <p>${escapeHtml(lemmatizationData.pos.definition)}</p>
        </div>
        <div class="example-stack example-stack-tight">
          <div class="quote-card">
            <p>${escapeHtml(lemmatizationData.pos.example.sentenceA)}</p>
            <strong>${escapeHtml(lemmatizationData.pos.example.tagsA)}</strong>
          </div>
          <div class="quote-card">
            <p>${escapeHtml(lemmatizationData.pos.example.sentenceB)}</p>
            <strong>${escapeHtml(lemmatizationData.pos.example.tagsB)}</strong>
          </div>
        </div>
        <div class="callout-banner callout-banner-prominent">
          <strong>POS tagging is effectively a solved task for fine-tuned systems.</strong>
          <span>State-of-the-art performance is about ${formatDecimal(lemmatizationData.pos.sota.f1, 2)} F1 and ${formatDecimal(lemmatizationData.pos.sota.acc, 2)} accuracy.</span>
        </div>
        <div class="question-focus">
          <strong>${escapeHtml(lemmatizationData.pos.benchmarkQuestion)}</strong>
        </div>
        <div class="binary-row">
          ${choiceCard({
            label: "Yes",
            body: "They should be able to reach benchmark range.",
            selected: p.posBenchmarkGuess === "yes",
            action: "set-guess",
            extra: { pathway: "lemmatization", key: "posBenchmarkGuess", value: "yes" },
          })}
          ${choiceCard({
            label: "No",
            body: "They'll get close, but the ceiling is still tough.",
            selected: p.posBenchmarkGuess === "no",
            action: "set-guess",
            extra: { pathway: "lemmatization", key: "posBenchmarkGuess", value: "no" },
          })}
        </div>
        <div class="action-row">
          ${
            p.posBenchmarkGuess
              ? button("Reveal POS Results", "set-step", {
                  pathway: "lemmatization",
                  step: "pos-reveal",
                })
              : `<button class="button" disabled>Choose an answer first</button>`
          }
        </div>
      </section>
    `;
  }

  if (p.step === "pos-reveal") {
    const rows = lemmatizationData.pos.benchmarks
      .map(
        (row) => `
          <tr>
            <th>${escapeHtml(row.model)}</th>
            <td><span class="score-chip ${scoreToneClass(row.accuracy, { high: 0.95, medium: 0.9, low: 0.82 })}">${formatDecimal(row.accuracy, 4)}</span></td>
            <td><span class="score-chip ${scoreToneClass(row.macroF1, { high: 0.95, medium: 0.9, low: 0.8 })}">${formatDecimal(row.macroF1, 4)}</span></td>
          </tr>
        `,
      )
      .join("");

    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>LLMs get close (even with a basic prompt!), but the ceiling is hard</h3>
          <p>General-purpose LLMs can do POS tagging well, but tippy-top F1 and accuracy are still difficult to match without fine-tuning. Why?</p>
        </div>
        <table class="results-table benchmark-table">
          <thead>
            <tr>
              <th>Model</th>
              <th>Accuracy</th>
              <th>Macro-F1</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
        <p class="note-text">Accuracy and F1 approach SOTA for this benchmark for Opus 4.6! But where are the models failing?</p>
        <div class="action-row">
          ${button("Why Is The Ceiling Hard To Match?", "set-step", {
            pathway: "lemmatization",
            step: "pos-tags",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "pos-tags") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>Where Does POS Get Hard?</h3>
          <p>${escapeHtml(lemmatizationData.pos.tagQuestion)}</p>
        </div>
        <div class="tag-picker-status">
          <strong>${p.posHardTagGuesses.length} / 3 selected</strong>
          <span>Pick three tags from the mini label map below.</span>
        </div>
        <div class="tag-choice-grid">
          ${lemmatizationData.pos.tagChoices
            .map(
              (choice) => `
                <button
                  class="tag-choice-card ${p.posHardTagGuesses.includes(choice.id) ? "tag-choice-card-selected" : ""}"
                  data-action="toggle-multi-select"
                  data-pathway="lemmatization"
                  data-key="posHardTagGuesses"
                  data-value="${escapeHtml(choice.id)}"
                  data-limit="3"
                >
                  <strong>${escapeHtml(choice.label)}</strong>
                  <span>${escapeHtml(choice.description)}</span>
                </button>
              `,
            )
            .join("")}
        </div>
        <div class="action-row">
          ${
            p.posHardTagGuesses.length === 3
              ? button("Reveal The Hardest Tags", "set-step", {
                  pathway: "lemmatization",
                  step: "pos-decomposition",
                })
              : `<button class="button" disabled>Pick exactly 3 tags</button>`
          }
        </div>
      </section>
    `;
  }

  if (p.step === "pos-decomposition") {
    const heatmapRows = lemmatizationData.pos.tagHeatmap
      .map(
        (row) => `
          <tr>
            <th>${escapeHtml(row.model)}</th>
            ${lemmatizationData.pos.tagChoices
              .map((choice) => {
                const value = row.tags[choice.id];
                return `<td><span class="score-chip ${scoreToneClass(value, { high: 0.88, medium: 0.72, low: 0.45 })}">${formatPercent(value, 1)}</span></td>`;
              })
              .join("")}
          </tr>
        `,
      )
      .join("");

    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>Answer: Task Decomposition</h3>
          <p>POS tagging looks like one task, but the error profile says otherwise.</p>
        </div>
        <div class="callout-banner">
          <strong>
            ${
              posHardTagHits.length === 3
                ? "Nice call."
                : `You found ${posHardTagHits.length} of the 3 hardest tags.`
            }
          </strong>
          <span>The hardest tags here are <strong>${escapeHtml(lemmatizationData.pos.actualHardestTags.join(", "))}</strong>.</span>
        </div>
        <table class="results-table heatmap-table">
          <thead>
            <tr>
              <th>Model</th>
              ${lemmatizationData.pos.tagChoices
                .map((choice) => `<th>${escapeHtml(choice.label)}</th>`)
                .join("")}
            </tr>
          </thead>
          <tbody>${heatmapRows}</tbody>
        </table>
        <div class="decomposition-layout">
          <div class="analysis-card">
            <strong>What this shows</strong>
            ${lemmatizationData.pos.decompositionNotes
              .map((note) => `<p>${escapeHtml(note)}</p>`)
              .join("")}
          </div>
          <div class="decomposition-node-list">
            ${lemmatizationData.pos.decompositionNodes
              .map((node) => `<div class="decomposition-node">${escapeHtml(node)}</div>`)
              .join("")}
          </div>
        </div>
        <div class="action-row">
          ${button("Now Build The Task Back Up", "set-step", {
            pathway: "lemmatization",
            step: "ner-reveal",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "ner-reveal") {
    const rows = lemmatizationData.ner.benchmarks
      .map(
        (row) => `
          <tr>
            <th>${escapeHtml(row.model)}</th>
            <td><span class="score-chip ${scoreToneClass(row.f1, { high: 0.945, medium: 0.92, low: 0.88 })}">${formatDecimal(row.f1, 4)}</span></td>
            <td>${escapeHtml(row.note)}</td>
          </tr>
        `,
      )
      .join("");

    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>${escapeHtml(lemmatizationData.ner.title)}</h3>
          <p>${escapeHtml(lemmatizationData.ner.definition)}</p>
        </div>
        <div class="callout-banner callout-banner-prominent">
          <strong>Standard NER is perhaps the strongest fit for general LLMs.</strong>
          <span>Benchmark standards land around ${escapeHtml(lemmatizationData.ner.sotaF1Range)} F1.</span>
        </div>
        <table class="results-table benchmark-table">
          <thead>
            <tr>
              <th>Model</th>
              <th>F1</th>
              <th>Read</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
        <p class="note-text">${escapeHtml(lemmatizationData.ner.takeaway)}</p>
        <div class="action-row">
          ${button("Compose A New NER Task", "set-step", {
            pathway: "lemmatization",
            step: "narnia-labels",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "narnia-labels") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>${escapeHtml(lemmatizationData.narnia.title)}</h3>
          <p>${escapeHtml(lemmatizationData.narnia.intro)}</p>
        </div>
        <div class="label-grid">
          ${lemmatizationData.narnia.labels
            .map(
              (label) => `
                <article class="label-card">
                  <strong>${escapeHtml(label.id)}</strong>
                  <p>${escapeHtml(label.description)}</p>
                </article>
              `,
            )
            .join("")}
        </div>
        <div class="analysis-card">
          <strong>${escapeHtml(lemmatizationData.narnia.quiz.prompt)}</strong>
          <p class="quiz-sentence">${escapeHtml(lemmatizationData.narnia.quiz.sentence)}</p>
          <div class="option-grid option-grid-wide">
            ${lemmatizationData.narnia.quiz.options
              .map((option) =>
                choiceCard({
                  label: option,
                  body: "",
                  selected: p.narniaLabelGuess === option,
                  action: "set-guess",
                  extra: { pathway: "lemmatization", key: "narniaLabelGuess", value: option },
                }),
              )
              .join("")}
          </div>
          ${
            p.narniaLabelGuess
              ? `
                <div class="callout-banner ${narniaQuizCorrect ? "" : "callout-banner-soft-coral"}">
                  <strong>${narniaQuizCorrect ? "Exactly." : "Close, but not quite."}</strong>
                  <span>${escapeHtml(lemmatizationData.narnia.quiz.explanation)}</span>
                </div>
              `
              : ""
          }
        </div>
        <div class="action-row">
          ${
            p.narniaLabelGuess
              ? button("Test The Custom Benchmark", "set-step", {
                  pathway: "lemmatization",
                  step: "narnia-benchmark-predict",
                })
              : `<button class="button" disabled>Answer the label question first</button>`
          }
        </div>
      </section>
    `;
  }

  if (p.step === "narnia-benchmark-predict") {
    body = `
      <section class="panel-card center-card">
        <div class="panel-header">
          <h3>Will A Better Prompt Help Here?</h3>
          <p>${escapeHtml(lemmatizationData.narnia.benchmarkQuestion)}</p>
        </div>
        <div class="callout-banner">
          <strong>${escapeHtml(lemmatizationData.narnia.note)}</strong>
          <span>Because this is a small, custom literary benchmark, prompt design may matter more than it did in the standard NER setting.</span>
        </div>
        <div class="binary-row">
          ${choiceCard({
            label: "Yes",
            body: "A few-shot prompt should help.",
            selected: p.narniaFewshotGuess === "yes",
            action: "set-guess",
            extra: { pathway: "lemmatization", key: "narniaFewshotGuess", value: "yes" },
          })}
          ${choiceCard({
            label: "No",
            body: "The task should stay about the same.",
            selected: p.narniaFewshotGuess === "no",
            action: "set-guess",
            extra: { pathway: "lemmatization", key: "narniaFewshotGuess", value: "no" },
          })}
        </div>
        <div class="action-row">
          ${
            p.narniaFewshotGuess
              ? button("Reveal The Narnia Results", "set-step", {
                  pathway: "lemmatization",
                  step: "narnia-benchmark",
                })
              : `<button class="button" disabled>Choose an answer first</button>`
          }
        </div>
      </section>
    `;
  }

  if (p.step === "narnia-benchmark") {
    const rows = lemmatizationData.narnia.benchmarks
      .map((row) => {
        const gain = row.fewShot - row.zeroShot;
        return `
          <tr>
            <th>${escapeHtml(row.model)}</th>
            <td><span class="score-chip ${scoreToneClass(row.zeroShot, { high: 0.8, medium: 0.7, low: 0.58 })}">${formatDecimal(row.zeroShot, 4)}</span></td>
            <td><span class="score-chip ${scoreToneClass(row.fewShot, { high: 0.8, medium: 0.7, low: 0.58 })}">${formatDecimal(row.fewShot, 4)}</span></td>
            <td><span class="score-chip ${scoreToneClass(gain, { high: 0.18, medium: 0.08, low: 0.03 })}">+${formatDecimal(gain, 4)}</span></td>
          </tr>
        `;
      })
      .join("");

    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>Custom Literary NER Benefits From Prompting</h3>
          <p>Once the task becomes more niche, prompt engineering starts helping again.</p>
        </div>
        <table class="results-table benchmark-table">
          <thead>
            <tr>
              <th>Model</th>
              <th>Zero-shot F1</th>
              <th>Few-shot F1</th>
              <th>Gain</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
        <div class="callout-banner">
          <strong>Establishing a sufficient baseline for our custom task...</strong>
          <span>${escapeHtml(lemmatizationData.narnia.applicationCopy)}</span>
        </div>
        <p class="fine-print">${escapeHtml(lemmatizationData.narnia.note)}</p>
        <div class="action-row">
          ${button("One Last Prediction", "set-step", {
            pathway: "lemmatization",
            step: "narnia-child",
          })}
        </div>
      </section>
    `;
  }

  if (p.step === "narnia-child") {
    body = `
      <section class="panel-card center-card">
        <div class="panel-header">
          <h3>OUR FINAL QUESTION!</h3>
          <p>${escapeHtml(lemmatizationData.narnia.childQuestion)}</p>
        </div>
        <div class="binary-row binary-row-wrap">
          ${lemmatizationData.narnia.childOptions
            .map((child) =>
              choiceCard({
                label: child,
                body: "",
                selected: p.narniaChildGuess === child,
                action: "set-guess",
                extra: { pathway: "lemmatization", key: "narniaChildGuess", value: child },
              }),
            )
            .join("")}
        </div>
        ${
          p.narniaChildGuess
            ? `
              <div class="callout-banner">
                <strong>You picked ${escapeHtml(p.narniaChildGuess)}.</strong>
                <span>${escapeHtml(lemmatizationData.narnia.childTease)}</span>
              </div>
            `
            : ""
        }
        <div class="action-row">
          ${
            p.narniaChildGuess
              ? button("See The TLDR", "set-step", {
                  pathway: "lemmatization",
                  step: "conclusion",
                })
              : `<button class="button" disabled>Pick a child first</button>`
          }
        </div>
      </section>
    `;
  }

  if (p.step === "conclusion") {
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>${escapeHtml(lemmatizationData.conclusion.title)}</h3>
          <p>${escapeHtml(lemmatizationData.conclusion.body)}</p>
        </div>
        <div class="summary-stack">
          ${metricCard("Build down", "Task decomposition", "Use sub-task structure to find where difficulty really lives.")}
          ${metricCard("Build up", "Task composition", "Use strong base tasks to create more interesting annotation schemes.")}
          ${metricCard("Practical rule", "Match task, data, and prompt", "Thse combinations make LLM applications interesting")}
        </div>
        <div class="callout-banner">
          <strong>Keep Exploring</strong>
          <span>Check out our Narnia results or learn about the application of LLMs among more difficult linguistic tasks.</span>
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
          <h3>Can We Beat Our Own Benchmark?</h3>
          <p>You're working on <strong>${escapeHtml(presuppositionsData.challenge.benchmark)}</strong>, a benchmark for presupposition reasoning. Here is the baseline result for <strong>Chat 5.4 with a minimal prompt</strong>:</p>
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
    body = `
      <section class="panel-card">
        <div class="panel-header">
          <h3>Pick a Prompt Strategy</h3>
          <p>Attempt ${attemptNumber} of 3</p>
        </div>
        <div class="option-grid option-grid-wide">
          ${presuppositionsData.promptCards
            .map((card) =>
              choiceCard({
                label: `${card.id} · ${card.family}`,
                body: card.description,
                selected: p.promptDraft === card.id,
                action: "set-guess",
                extra: { pathway: "presuppositions", key: "promptDraft", value: card.id },
              }),
            )
            .join("")}
        </div>
        <div class="action-row">
          ${
            p.promptDraft
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
    if (pathway === "lemmatization" && step === "grid") {
      state.lemmatization.revealedCells = [];
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

  if (action === "toggle-multi-select") {
    const { pathway, key, value } = target.dataset;
    const limit = Number(target.dataset.limit || 0);
    const current = Array.isArray(state[pathway][key]) ? [...state[pathway][key]] : [];
    const existingIndex = current.indexOf(value);

    if (existingIndex >= 0) {
      current.splice(existingIndex, 1);
    } else if (!limit || current.length < limit) {
      current.push(value);
    }

    state[pathway][key] = current;
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
