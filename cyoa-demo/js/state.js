const STORAGE_KEY = "ling-llm-demo-state";

export function createDefaultState() {
  return {
    route: { view: "home", step: null },
    lemmatization: {
      step: "intro",
      benchmarkGuess: null,
      modelChoiceGuess: null,
      batchSizeGuess: null,
      revealedCells: [],
      hardestGuess: null,
    },
    pronoun: {
      step: "intro",
      englishRefineChoice: null,
      englishPromptDraft: null,
      englishPrompt: null,
      africanPromptChoice: null,
      africanPromptDraft: null,
      africanPrompt: null,
    },
    presuppositions: {
      step: "intro",
      promptDraft: null,
      attempts: [],
    },
  };
}

export function loadState() {
  const base = createDefaultState();
  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return base;
    const saved = JSON.parse(raw);
    return {
      ...base,
      ...saved,
      route: saved.route || base.route,
      lemmatization: { ...base.lemmatization, ...(saved.lemmatization || {}) },
      pronoun: { ...base.pronoun, ...(saved.pronoun || {}) },
      presuppositions: {
        ...base.presuppositions,
        ...(saved.presuppositions || {}),
      },
    };
  } catch {
    return base;
  }
}

export function saveState(state) {
  window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function resetPathwayState(state, pathwayId) {
  const fresh = createDefaultState()[pathwayId];
  state[pathwayId] = fresh;
}
