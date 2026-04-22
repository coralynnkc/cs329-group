export const lemmatizationData = {
  id: "lemmatization",
  title: "Lemmatization, POS Tagging, NER, and ...Narnia?",
  eyebrow: "Morphology Demo",
  lesson:
    "LLMs are already very good at discrete linguistic tasks, but the bigger lesson is about task design: some linguistic problems can be broken down to be accurately analyzed, and others can be built up to be interestingly applied.",
  introExamples: [
    { form: "running", lemma: "run" },
    { form: "mice", lemma: "mouse" },
  ],
  benchmarkPrompt:
    "Current state-of-the-art lemmatization performance is very high. Our general, commercial models able to easily perform at that level?",
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
    "Gemini 3 gets the best single run, while GPT-5.4 and Sonnet 4.6 are more stable.",
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
        example: "spelling changes",
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
  bridge: {
    title: "Lemmatization Illustrates a Bigger Lesson",
    body:
      "Some tasks get clearer when we break them down into smaller decisions. Others get more interesting when we build them up into richer annotation schemes.",
    concepts: [
      {
        title: "Task Decomposition",
        body: "Breaking a task down into smaller subproblems so we can see where the real anlaytical difficulty lives.",
      },
      {
        title: "Task Composition",
        body: "Building a richer task up from simpler ones so we can study something more linguistically interesting.",
      },
    ],
  },
  pos: {
    title: "Task Decomposition: POS Tagging",
    definition:
      "POS tagging assigns each word its grammatical category in context.",
    example: {
      sentenceA: "I read the book .",
      tagsA: "PRON VERB DET NOUN PUNCT",
      sentenceB: "Book the flight .",
      tagsB: "VERB DET NOUN PUNCT",
    },
    benchmarkQuestion:
      "Do you think general-purpose LLMs can meet POS benchmarks?",
    sota: {
      f1: 0.97,
      acc: 0.96,
    },
    benchmarks: [
      { model: "ChatGPT 5.4", accuracy: 0.8067, macroF1: 0.7636 },
      { model: "Gemini 3", accuracy: 0.8263, macroF1: 0.7383 },
      { model: "Sonnet 4.6", accuracy: 0.8503, macroF1: 0.7126 },
      { model: "Opus 4.6", accuracy: 0.9396, macroF1: 0.8547 },
    ],
    tagQuestion:
      "Pick the 3 POS tags you expect to be hardest for general-purpose LLMs.",
    tagChoices: [
      { id: "SCONJ", label: "SCONJ", description: "subordinating conjunction" },
      { id: "INTJ", label: "INTJ", description: "interjection" },
      { id: "X", label: "X", description: "other / hard-to-classify token" },
      { id: "SYM", label: "SYM", description: "symbol" },
      { id: "ADJ", label: "ADJ", description: "adjective" },
      { id: "PROPN", label: "PROPN", description: "proper noun" },
      { id: "ADV", label: "ADV", description: "adverb" },
      { id: "AUX", label: "AUX", description: "auxiliary verb" },
      { id: "CCONJ", label: "CCONJ", description: "coordinating conjunction" },
    ],
    actualHardestTags: ["X", "SCONJ", "INTJ"],
    tagHeatmap: [
      {
        model: "ChatGPT 5.4",
        tags: {
          SCONJ: 0.4224,
          INTJ: 0.5833,
          X: 0.2857,
          SYM: 0.625,
          ADJ: 0.5882,
          PROPN: 0.7321,
          ADV: 0.7056,
          AUX: 0.9083,
          CCONJ: 0.9304,
        },
      },
      {
        model: "Gemini 3",
        tags: {
          SCONJ: 0.6154,
          INTJ: 0.7,
          X: 0.0,
          SYM: 0.4545,
          ADJ: 0.7977,
          PROPN: 0.8262,
          ADV: 0.7955,
          AUX: 0.8639,
          CCONJ: 0.8372,
        },
      },
      {
        model: "Sonnet 4.6",
        tags: {
          SCONJ: 0.5257,
          INTJ: 0.3333,
          X: 0.1905,
          SYM: 0.6,
          ADJ: 0.81,
          PROPN: 0.8495,
          ADV: 0.6944,
          AUX: 0.8762,
          CCONJ: 0.924,
        },
      },
      {
        model: "Opus 4.6",
        tags: {
          SCONJ: 0.6353,
          INTJ: 0.9474,
          X: 0.0,
          SYM: 0.7059,
          ADJ: 0.9125,
          PROPN: 0.8953,
          ADV: 0.8592,
          AUX: 0.9472,
          CCONJ: 0.9854,
        },
      },
    ],
    decompositionNotes: [
      "POS tagging is not one decision. It hides ambiguity. Failures cluster around lexical ambiguity and rare label behavior."
    ],
    decompositionNodes: [
      "Lexical ambiguity",
      "Function-word distinctions",
      "Rare labels",
      "Token formatting noise",
    ],
  },
  ner: {
    title: "Task Composition: Standard NER",
    definition:
      "Named Entity Recognition is our last 'LLM-solved task.' It identifies spans or entities like people, locations, and organizations in text.",
    labels: ["PER", "ORG", "LOC", "MISC"],
    sotaF1Range: "0.95–0.97",
    benchmarks: [
      { model: "ChatGPT 5.4", f1: 0.905, note: "strong" },
      { model: "Gemini 3", f1: 0.9301, note: "very strong" },
      { model: "Sonnet 4.6", f1: 0.9196, note: "very strong" },
      { model: "Opus 4.6", f1: 0.9495, note: "closest to benchmark ceiling" },
    ],
    takeaway:
      "This is a task LLMs are generally well-suited for. Which means we can use it in applications — and even build richer tasks on top of it.",
  },
  narnia: {
    title: "Agentic NER: a Custom Task Categor",
    intro:
      "Instead of confining ourselves to PERSON / ORGANIZATION / LOCATION labels, we can create a new label set for narrative agency in The Lion, the Witch, and the Wardrobe.",
    labels: [
      {
        id: "ACTIVE_SPEAKER",
        description: "character is mentioned in the context of speaking dialogue",
      },
      {
        id: "ACTIVE_PERFORMER",
        description: "character performs a physical action",
      },
      {
        id: "ACTIVE_THOUGHT",
        description: "character thinks or feels something",
      },
      {
        id: "ADDRESSED",
        description: "character is spoken to directly",
      },
      {
        id: "MENTIONED_ONLY",
        description: "character is mentioned but not acting",
      },
      {
        id: "MISCELLANEOUS",
        description: "role or mention that does not cleanly fit the others",
      },
    ],
    quiz: {
      prompt: "Quick check: what label should Lucy get here?",
      sentence: '"Badgers!" said Lucy .',
      options: ["ACTIVE_SPEAKER", "ACTIVE_PERFORMER", "ADDRESSED", "MENTIONED_ONLY"],
      correct: "ACTIVE_SPEAKER",
      explanation:
        "Because Lucy is explicitly the speaker, this is ACTIVE_SPEAKER rather than just a mention.",
    },
    benchmarkQuestion:
      "Do you think a few-shot prompt helps on this custom literary NER task?",
    benchmarks: [
      { model: "ChatGPT 5.4", zeroShot: 0.5861, fewShot: 0.797 },
      { model: "Gemini 3", zeroShot: 0.5656, fewShot: 0.8092 },
      { model: "Sonnet 4.6", zeroShot: 0.741, fewShot: 0.8231 },
      { model: "Opus 4.6", zeroShot: 0.7833, fewShot: 0.8092 },
    ],
    note: "Manually labeled benchmark: n = 200 sentences",
    applicationCopy:
      "This is where custom task composition becomes useful. Once the task fits the corpus and the labels fit the research question, LLMs can help linguists ask genuinely new questions about narrative structure and character agency.",
    childQuestion:
      "Which of the four Pevensie children do you think is structurally most agentic?",
    childOptions: ["Peter", "Susan", "Edmund", "Lucy"],
    childTease: "Stick around for our second demo to find out :) ",
  },
  conclusion: {
    title: "What's the TLDR?",
    body:
      "Task decomposition (building down) and task composition (building up) go both ways for linguistics and LLMs.",
    takeaway:
      "The key is to match an appropriately interesting task to an appropriately suited dataset with an appropriately explained, tuned, and formatted prompt. When those conditions line up, LLMs can be genuinely useful.",
  },
};
