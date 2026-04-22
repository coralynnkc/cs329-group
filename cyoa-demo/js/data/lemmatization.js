export const lemmatizationData = {
  id: "lemmatization",
  title: "Lemmatization",
  eyebrow: "Morphology Demo",
  lesson:
    "LLMs are already very good at lemmatization, but the remaining errors are concentrated rather than random.",
  introExamples: [
    { form: "running", lemma: "run" },
    { form: "mice", lemma: "mouse" },
  ],
  benchmarkPrompt:
    "Current state-of-the-art lemmatization performance is very high. Our best models get close to that level. Do you think LLMs can match state-of-the-art accuracy?",
  models: [
    { id: "sonnet_4.6", label: "Sonnet 4.6", personality: "Steady" },
    { id: "opus_4.6", label: "Opus 4.6", personality: "Strong peak" },
    { id: "gpt_5.3", label: "GPT-5.3", personality: "More variable" },
    { id: "gpt_5.4", label: "GPT-5.4", personality: "Steady" },
    { id: "gemini_3", label: "Gemini 3", personality: "Highest peak" },
  ],
  batchSizes: [100, 200, 300, 500],
  grid: {
    "sonnet_4.6": { 100: 0.93, 200: 0.94, 300: 0.9233, 500: 0.932 },
    "opus_4.6": { 100: 0.95, 200: 0.965, 300: 0.8567, 500: 0.86 },
    "gpt_5.3": { 100: 0.85, 200: 0.795, 300: 0.54, 500: 0.472 },
    "gpt_5.4": { 100: 0.93, 200: 0.94, 300: 0.92, 500: 0.93 },
    "gemini_3": { 100: 0.91, 200: 0.965, 300: 0.8633, 500: 0.972 },
  },
  bestRun: {
    model: "Gemini 3",
    batchSize: 500,
    score: 0.972,
  },
  modelTakeaway:
    "Gemini 3 gets the best single run, while GPT-5.4 and Sonnet 4.6 are the steadier choices.",
  subgroupQuestion: {
    title: "Which Kind of Lemmatization Is Hardest?",
    options: [
      {
        id: "easy",
        label: "Easy",
        example: "straightforward identity or regular mapping",
      },
      {
        id: "changed",
        label: "Changed",
        example: "spelling changes, but predictably",
      },
      {
        id: "ambiguous",
        label: "Ambiguous",
        example: "one surface form can map to more than one lemma",
      },
      {
        id: "rare",
        label: "Rare",
        example: "infrequent forms",
      },
      {
        id: "irregular",
        label: "Irregular",
        example: "non-standard lemma mapping",
      },
    ],
  },
  subgroupSliceLabel:
    "Shared n = 300 slice for like-with-like comparison across models",
  subgroupCategories: ["easy", "changed", "ambiguous", "rare", "irregular"],
  subgroupTable: [
    {
      model: "Gemini 3",
      batchSize: 300,
      easy: 0.9833,
      changed: 0.9667,
      ambiguous: 0.95,
      rare: 0.85,
      irregular: 0.5667,
    },
    {
      model: "GPT-5.4",
      batchSize: 300,
      easy: 0.9667,
      changed: 0.9333,
      ambiguous: 0.95,
      rare: 0.95,
      irregular: 0.8,
    },
    {
      model: "Sonnet 4.6",
      batchSize: 300,
      easy: 0.9667,
      changed: 0.9667,
      ambiguous: 0.95,
      rare: 0.9333,
      irregular: 0.8,
    },
    {
      model: "Opus 4.6",
      batchSize: 300,
      easy: 0.9667,
      changed: 0.9667,
      ambiguous: 0.95,
      rare: 0.8333,
      irregular: 0.5667,
    },
    {
      model: "GPT-5.3",
      batchSize: 300,
      easy: 0.5667,
      changed: 0.5,
      ambiguous: 0.6167,
      rare: 0.5667,
      irregular: 0.45,
    },
  ],
};
