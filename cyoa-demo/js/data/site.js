export const siteMeta = {
  title: "LLMs for Linguistic Analysis",
  subtitle:
    "A click-through desktop demo on where large language models help, where prompts matter, and where linguistic structure still matters most.",
  projectSummary:
    "Each pathway teaches a different methodological lesson through interaction, not lecture.",
};

export const pathways = [
  {
    id: "lemmatization",
    title: "Lemmatization",
    eyebrow: "Morphology",
    short:
      "High headline accuracy still hides structured weakness, especially on irregular forms.",
    accent: "teal",
    cta: "Explore Lemmatization",
  },
  {
    id: "pronoun",
    title: "Pronoun Resolution",
    eyebrow: "Reference",
    short:
      "Prompt tuning does not matter equally everywhere. Stable English settings are different from lower-resource ones.",
    accent: "coral",
    cta: "Explore Pronoun Resolution",
  },
  {
    id: "presuppositions",
    title: "Presuppositions",
    eyebrow: "Semantics",
    short:
      "The best prompt is not the longest one. It is the one that teaches the semantic boundary clearly.",
    accent: "gold",
    cta: "Explore Presuppositions",
  },
];

export const sharedNotes = [
  "Static site only. No backend, no database, no login.",
  "All scores, prompts, and labels are stored in local data modules for easy editing.",
  "Designed for self-guided desktop browsing and GitHub Pages deployment.",
];
