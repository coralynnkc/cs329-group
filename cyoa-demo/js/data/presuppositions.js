export const presuppositionsData = {
  id: "presuppositions",
  title: "Presupposition",
  eyebrow: "Semantics Demo",
  introExamples: [
    {
      premise: "Alex stopped smoking",
      presupposition: "Alex used to smoke",
    },
    {
      premise: "Maya's brother arrived",
      presupposition: "Maya has a brother",
    },
  ],
  challenge: {
    benchmark: "CONFER English",
    baselinePrompt: "P0",
    accuracy: 0.6933,
    macroF1: 0.6828,
  },
  promptCards: [
    {
      id: "P0",
      family: "Minimal baseline",
      description: "Lets the model infer the task from the dataset alone.",
      outputType: "Probabilities",
    },
    {
      id: "P1",
      family: "Few-shot benchmark-shaped examples",
      description:
        "Uses one concrete example of each class and keeps probability output.",
      outputType: "Probabilities",
    },
    {
      id: "P2",
      family: "Guarantee-based NLI rule",
      description:
        "Asks whether the premise guarantees the hypothesis is true, false, or unresolved.",
      outputType: "Probabilities",
    },
    {
      id: "P4",
      family: "Symmetric true/false audit",
      description:
        "Separately checks definitely true and definitely false before deciding.",
      outputType: "Probabilities",
    },
    {
      id: "P5",
      family: "Compatibility then determination",
      description:
        "Starts by asking whether the premise and hypothesis can both be true.",
      outputType: "Probabilities",
    },
    {
      id: "P6",
      family: "Independent E / C / N tests",
      description:
        "Runs separate tests for each class before deciding.",
      outputType: "Probabilities",
    },
    {
      id: "P7",
      family: "Projection-aware definitions",
      description:
        "Uses explicit presupposition and projection wording without examples.",
      outputType: "Probabilities",
    },
    {
      id: "P8",
      family: "Hard-label mirror of P7",
      description:
        "Removes probabilities from the projection-aware family.",
      outputType: "Hard label",
    },
    {
      id: "P10",
      family: "Hard-label mirror of P1",
      description:
        "Removes probabilities from the few-shot benchmark-shaped family.",
      outputType: "Hard label",
    },
    {
      id: "P12",
      family: "Hard-label mirror of P2",
      description:
        "Removes probabilities from the guarantee-based family.",
      outputType: "Hard label",
    },
  ],
  prompts: {
    P0: {
      outputType: "Probabilities",
      family: "Minimal baseline",
      accuracy: 0.6933,
      macroF1: 0.6828,
      f1E: 0.7857,
      f1N: 0.4889,
      f1C: 0.7738,
      logLoss: 0.9081,
      brier: 0.5244,
      integrity: "Full scorer coverage",
      interpretation:
        "This prompt leaves too much of the task geometry implicit. It performs decently overall, but it does not teach the model clearly what makes a case truly Neutral.",
      hint:
        "If you want to improve on this, look for a prompt that teaches the class boundary more explicitly.",
    },
    P1: {
      outputType: "Probabilities",
      family: "Few-shot examples",
      accuracy: 0.7867,
      macroF1: 0.7841,
      f1E: 0.8722,
      f1N: 0.6923,
      f1C: 0.7879,
      logLoss: 0.6815,
      brier: 0.3686,
      integrity: "Full scorer coverage",
      interpretation:
        "This prompt works because it teaches the benchmark's label geometry by example. It gives the model one concrete case of each class while preserving probability output.",
      hint:
        "Concrete examples and flexible output can be more helpful than extra scaffolding.",
    },
    P2: {
      outputType: "Probabilities",
      family: "Guarantee-based NLI",
      accuracy: 0.71,
      macroF1: 0.7094,
      f1E: 0.7845,
      f1N: 0.57,
      f1C: 0.7738,
      logLoss: 0.8589,
      brier: 0.4917,
      integrity: "Full scorer coverage",
      interpretation:
        "This prompt adds useful structure, but abstract rules alone still do not teach the boundary as clearly as examples do.",
      hint:
        "If a prompt is highly structured but still underperforms, the missing ingredient may be calibration rather than more rules.",
    },
    P4: {
      outputType: "Probabilities",
      family: "Symmetric rule-based NLI",
      accuracy: 0.4767,
      macroF1: 0.4644,
      f1E: 0.4106,
      f1N: 0.5094,
      f1C: 0.4733,
      logLoss: 1.6368,
      brier: 0.9029,
      integrity: "Full scorer coverage",
      interpretation:
        "This stricter symmetric audit appears to push Chat 5.4 into a weaker labeling strategy. The prompt is orderly, but the extra strictness does not translate into better class balance for this model.",
      hint:
        "More symmetry and more logic steps are not automatically improvements.",
    },
    P5: {
      outputType: "Probabilities",
      family: "Compatibility then determination",
      accuracy: 0.47,
      macroF1: 0.4563,
      f1E: 0.3893,
      f1N: 0.5062,
      f1C: 0.4733,
      logLoss: 1.5819,
      brier: 0.8962,
      integrity: "Full scorer coverage",
      interpretation:
        "This prompt over-builds the reasoning path. Compatibility matters, but it does not cleanly separate Neutral from Entailment.",
      hint:
        "Useful sub-questions are only helpful if they sharpen the final semantic distinction.",
    },
    P6: {
      outputType: "Probabilities",
      family: "Independent E / C / N tests",
      accuracy: 0.47,
      macroF1: 0.4563,
      f1E: 0.3893,
      f1N: 0.5062,
      f1C: 0.4733,
      logLoss: 1.5028,
      brier: 0.8689,
      integrity: "Full scorer coverage",
      interpretation:
        "More decomposition is not always better. This prompt asks for too many overlapping checks, and the extra structure does not improve class balance.",
      hint:
        "Try a prompt that teaches the boundary more directly rather than adding more diagnostic layers.",
    },
    P7: {
      outputType: "Probabilities",
      family: "Explicit presupposition definitions",
      accuracy: 0.4567,
      macroF1: 0.4042,
      f1E: 0.6875,
      f1N: 0.0355,
      f1C: 0.4895,
      logLoss: 1.8956,
      brier: 0.9854,
      integrity: "Full scorer coverage",
      interpretation:
        "Task-specific theory by itself is not enough. Explicit presupposition wording without benchmark-shaped examples does not teach the decision boundary clearly enough.",
      hint:
        "A prompt can sound more linguistically informed and still be poorly calibrated for the benchmark.",
    },
    P8: {
      outputType: "Hard label",
      family: "P7 mirror",
      accuracy: 0.3467,
      macroF1: 0.1888,
      f1E: 0.0588,
      f1N: 0.5075,
      f1C: 0,
      logLoss: null,
      brier: null,
      integrity: "Manual full-set scoring",
      interpretation:
        "This prompt removes probabilities from an already weak family and collapses even further. The model loses too much signal when it has to force a single class.",
      hint:
        "Output format is part of the method, not just the packaging.",
    },
    P10: {
      outputType: "Hard label",
      family: "P1 mirror",
      accuracy: 0.6,
      macroF1: 0.5645,
      f1E: 0.72,
      f1N: 0.2323,
      f1C: 0.7412,
      logLoss: null,
      brier: null,
      integrity: "Manual full-set scoring",
      interpretation:
        "Few-shot examples still help here, but hard labels throw away too much of the boundary information. The biggest penalty shows up on Neutral.",
      hint:
        "A strong prompt family can still weaken a lot if the output format becomes too rigid.",
    },
    P12: {
      outputType: "Hard label",
      family: "P2 mirror",
      accuracy: 0.47,
      macroF1: 0.4563,
      f1E: 0.3893,
      f1N: 0.5062,
      f1C: 0.4733,
      logLoss: null,
      brier: null,
      integrity: "Manual full-set scoring",
      interpretation:
        "This shows that output format is part of the design. The same guarantee-based idea works much worse when the model has to force a single class.",
      hint:
        "Sometimes the improvement you need is not a new reasoning rule, but a less brittle answer format.",
    },
  },
  ranking: [
    { prompt: "P1", macroF1: 0.7841, badge: "Best overall" },
    { prompt: "P2", macroF1: 0.7094 },
    { prompt: "P0", macroF1: 0.6828 },
    { prompt: "P10", macroF1: 0.5645 },
    { prompt: "P4", macroF1: 0.4644 },
    { prompt: "P5", macroF1: 0.4563 },
    { prompt: "P6", macroF1: 0.4563 },
    { prompt: "P12", macroF1: 0.4563 },
    { prompt: "P7", macroF1: 0.4042 },
    { prompt: "P8", macroF1: 0.1888 },
  ],
  classBalance: [
    { label: "P1 — Chat 5.4", f1E: 0.8722, f1N: 0.6923, f1C: 0.7879 },
    { label: "P1 — Opus 4.6", f1E: 0.8959, f1N: 0.8667, f1C: 0.995 },
    { label: "RoBERTa", f1E: 0.5, f1N: 0.9, f1C: 0.96 },
    { label: "DeBERTa", f1E: 0.45, f1N: 0.95, f1C: 0.88 },
  ],
  multilingual: {
    question:
      "Does this performance extension carry over to non-English presupposition mapping? Will prompt engineering still apply?",
    intro:
      "We tested the same prompt families on a non-English multilingual benchmark across German, French, Hindi, Russian, and Vietnamese.",
    englishDifferentials: {
      p1VsP0: 0.1013,
      p1VsP2: 0.0747,
    },
    rows: [
      {
        language: "de",
        p0Acc: 0.79,
        p1Acc: 0.85,
        p2Acc: 0.83,
        p0MacroF1: 0.8161,
        p1MacroF1: 0.8499,
        p2MacroF1: 0.8288,
        best: "P1",
      },
      {
        language: "fr",
        p0Acc: 0.85,
        p1Acc: 0.87,
        p2Acc: 0.84,
        p0MacroF1: 0.8487,
        p1MacroF1: 0.8709,
        p2MacroF1: 0.8417,
        best: "P1",
      },
      {
        language: "hi",
        p0Acc: 0.75,
        p1Acc: 0.8,
        p2Acc: 0.8,
        p0MacroF1: 0.7509,
        p1MacroF1: 0.8016,
        p2MacroF1: 0.8039,
        best: "P1 / P2 tie",
      },
      {
        language: "ru",
        p0Acc: 0.79,
        p1Acc: 0.82,
        p2Acc: 0.78,
        p0MacroF1: 0.7884,
        p1MacroF1: 0.8197,
        p2MacroF1: 0.7837,
        best: "P1",
      },
      {
        language: "vi",
        p0Acc: 0.78,
        p1Acc: 0.79,
        p2Acc: 0.78,
        p0MacroF1: 0.7831,
        p1MacroF1: 0.792,
        p2MacroF1: 0.7811,
        best: "P1",
      },
      {
        language: "Average",
        p0Acc: 0.792,
        p1Acc: 0.826,
        p2Acc: 0.806,
        p0MacroF1: 0.7974,
        p1MacroF1: 0.8268,
        p2MacroF1: 0.8078,
        best: "P1",
        isAverage: true,
      },
    ],
    multilingualDifferentials: {
      p1VsP0: 0.0294,
      p1VsP2: 0.019,
    },
    takeaway:
      "Yes: the improvement carries over on average, but less dramatically than it did on the English CONFER benchmark.",
    sidenote:
      "Sidenote: French consistently outperforms the other languages on this benchmark. Is French semantically easier to analyze presuppositionally than the other languages on this list? Food for thought.",
  },
  conclusion: {
    title: "Why This Matters",
    body:
      "This demo shows that prompt engineering is part of the method — and that more is not always better.",
    transferQuestion:
      "Are prompting strategies always generalizable for multilingual model trials?",
    transferAnswer:
      "Refer to the Pronoun Resolution pathway to find out!",
  },
};
