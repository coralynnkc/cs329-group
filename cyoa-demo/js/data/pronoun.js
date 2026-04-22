export const pronounData = {
  id: "pronoun",
  title: "Pronoun Resolution",
  eyebrow: "Reference Demo",
  introExample: {
    sentence: "Kevin thanked Joseph because he got the job.",
    question: 'Who does "he" refer to?',
  },
  englishSetup: {
    model: "Claude Sonnet 4.6",
    dataset: "Winogrande English pronoun resolution dataset",
    sota: "0.89",
    results: [
      { n: 100, accuracy: 0.91 },
      { n: 250, accuracy: 0.852 },
      { n: 500, accuracy: 0.876 },
    ],
  },
  promptOptions: [
    {
      id: "P0",
      label: "P0",
      family: "Minimal baseline",
      description: "Lets the model infer the task from the dataset alone.",
    },
    {
      id: "P1",
      label: "P1",
      family: "Two-shot examples",
      description: "Adds a tiny exemplar set without much extra prompt overhead.",
    },
    {
      id: "P2",
      label: "P2",
      family: "Four-shot examples",
      description: "Adds more demonstrations while keeping the task format fixed.",
    },
    {
      id: "P3",
      label: "P3",
      family: "Candidate tracking",
      description: "Uses an internal step-by-step candidate check before deciding.",
    },
    {
      id: "P4",
      label: "P4",
      family: "Expanded definition",
      description: "Frames the task more explicitly as contextual interpretation.",
    },
  ],
  lowResourceResults: {
    Amharic: [
      { prompt: "P2", accuracy: 0.7889, macroF1: 0.7844 },
      { prompt: "P0", accuracy: 0.7778, macroF1: 0.7768 },
      { prompt: "P3", accuracy: 0.7778, macroF1: 0.776 },
      { prompt: "P4", accuracy: 0.7778, macroF1: 0.775 },
      { prompt: "P1", accuracy: 0.7444, macroF1: 0.7437 },
    ],
    Zulu: [
      { prompt: "P1", accuracy: 0.6, macroF1: 0.6 },
      { prompt: "P2", accuracy: 0.6, macroF1: 0.5998 },
      { prompt: "P4", accuracy: 0.5556, macroF1: 0.5587 },
      { prompt: "P0", accuracy: 0.5556, macroF1: 0.5584 },
      { prompt: "P3", accuracy: 0.5556, macroF1: 0.5584 },
    ],
    Igbo: [
      { prompt: "P2", accuracy: 0.5889, macroF1: 0.5801 },
      { prompt: "P0", accuracy: 0.5778, macroF1: 0.5778 },
      { prompt: "P1", accuracy: 0.5667, macroF1: 0.5623 },
      { prompt: "P3", accuracy: 0.5333, macroF1: 0.5326 },
      { prompt: "P4", accuracy: 0.5111, macroF1: 0.5078 },
    ],
  },
  robustness: [
    { language: "English", value: 0 },
    { language: "Russian", value: 0.0084 },
    { language: "German", value: 0.0102 },
    { language: "French", value: 0.013 },
    { language: "Amharic", value: 0.0158 },
    { language: "Zulu", value: 0.0227 },
    { language: "Igbo", value: 0.0312 },
  ],
};
