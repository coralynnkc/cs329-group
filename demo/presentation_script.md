# CS329 Demo Presentation Script
**Format: ~5 min talk + ~5 min demo/visuals**

---

## PART 1 — TALK (~5 minutes)

---

### 1. Motivation (1 min)

Linguists study language — syntax, morphology, narrative structure, crosslinguistic patterns. But the moment a research question requires processing more than a few hundred sentences, they hit a wall: they need to learn to code, hire a software engineer, or limit themselves to whatever pre-built tools already exist.

Our project asks: what if they didn't have to?

Large language models are general-purpose annotation engines. A linguist can describe a task in plain English — define labels, give examples, explain edge cases — and an LLM applies that scheme to thousands of sentences without any training or pipeline engineering. We set out to systematically benchmark how well this actually works, and for which kinds of tasks.

---

### 2. Background: What's Already Solved (1 min)

We treat **lemmatization** as our proof of concept. Given an inflected word like *ate* or *geese*, return the dictionary headword: *eat*, *goose*. Opus, Sonnet, and Gemini all score 96–97% accuracy. Solved.

**POS tagging** and **standard NER** tell a similar story: Opus hits 94% on UD POS tags and 95% F1 on CoNLL-2003 NER. These tasks are well-represented in training data, the label sets are small, and there's no ambiguity about what counts as a correct answer.

The reason this matters: these solved tasks establish that the prompting-based approach works *in principle*. But they're not the interesting scientific question. They're tasks the models have essentially already seen. What happens when we go further?

---

### 3. Harder Tasks: Grammaticality, Presuppositions, Pronoun Resolution (1.5 min)

Grammaticality judgment is harder. CoLA sentences come from linguistics papers and test subtle phenomena — island constraints, binding violations, agreement errors. Our prompt comparison experiment across five designs shows that **prompt choice is split-sensitive**: the `checklist` prompt collapses in-domain (56% accuracy, negative MCC) but becomes the best out-of-domain (90% accuracy). `Direct` is the safest general baseline. There is no single best prompt — and knowing that is itself a useful finding for any linguist using LLMs to annotate data.

Presuppositions and pronoun resolution are harder still — and this is where the multilingual data gets interesting. Presupposition accuracy clusters around 41–52% across all six languages — barely above random for a three-way classification task. Pronoun resolution is even more striking: **English scores the worst**, at just 36%, while French and German reach 52%.

Why would a model be worse at its strongest language? The answer is almost certainly training contamination. English WinoGrande was a major benchmark — the model has learned to pattern-match rather than reason. In lower-resource languages, it's forced to actually resolve the pronoun, which paradoxically produces better results.

---

### 4. Our Task: Agency NER in Narnia (1.5 min)

Our primary contribution is a novel NER task we designed from scratch: **agency-based character recognition in narrative text**, applied to *The Lion, the Witch and the Wardrobe*.

Standard NER tags Lucy as PER. We asked: is Lucy speaking, acting, being addressed, or just mentioned? We defined six labels: `ACTIVE_SPEAKER`, `ACTIVE_PERFORMER`, `ACTIVE_THOUGHT`, `ADDRESSED`, `MENTIONED_ONLY`, `MISCELLANEOUS`.

This operationalizes *agency* — a core concept in linguistics that concerns how language encodes control and participation in events. It lets linguists ask: who actually drives the narrative vs. who is just talked about?

We manually annotated 200 sentences as ground truth. Zero-shot: Opus 0.783 F1, Sonnet 0.741. Few-shot — eight examples in the prompt — pushed Sonnet to 0.823. The hardest label zero-shot was `ADDRESSED` (vocatives like *"Oh, Mr. Tumnus!"* get misclassified as `MENTIONED_ONLY`). One labeled example fixed it: Sonnet's ADDRESSED F1 jumped from 0.53 to 0.89. No retraining. No data collection. Just a description of the edge case.

Then we scaled to the full book — 17 chapters, 2,404 sentences — and the annotations reveal real linguistic structure. Let me show you what that looks like.

---

## PART 2 — DEMO / VISUALS (~5 minutes)

---

### Visual 1: Overall Task Accuracy Bar Chart (30 sec)

> **Show: `graph.ipynb` accuracy histogram**

This is the headline result across all tasks. POS and grammaticality approach the 80% threshold. Presuppositions and pronoun resolution fall well below it. This stratification is not surprising linguistically — it maps directly onto how much discourse context and pragmatic inference each task requires.

---

### Visual 2: Multilingual Pronoun Resolution & Presuppositions (1 min)

> **Show: model comparison spreadsheets / grouped bar chart from `graph.ipynb`**

Here are the raw numbers across languages. Pronoun resolution: French 52%, German 52%, Russian 52%, English 36%. Presuppositions: consistent 41–52% across English, French, German, Hindi, Russian, Vietnamese.

The English pronoun outlier is visible here. The presupposition numbers are nearly language-agnostic — the task is hard in the same way across all six languages.

---

### Visual 3: Narnia 200-Sentence Eval — Zero-Shot vs. Few-Shot (1 min)

> **Show: narnia README results tables, per-label F1 breakdown**

Here are the before/after numbers for the 200-sentence benchmark. Zero-shot vs. few-shot, by model and by label. The gains on ADDRESSED and MISCELLANEOUS are the story — those were the two labels where zero-shot failed systematically, and both recover dramatically with targeted examples. Gemini gains +0.244 overall, the largest single improvement in the project.

---

### Visual 4: Full-Book Agency Analysis — narnia-large charts (2.5 min)

> **Show: label distribution → top character mentions → active agency ratio → chapter density → character arcs**

Now the full-book results. 2,404 sentences, 2,361 entity mentions.

**Label distribution.** About 60% of mentions are active. The model assigns agency wherever syntactic structure permits — which is itself interesting as a finding about the text.

**Top characters by raw mention count.** Edmund and Lucy are essentially tied at ~411 mentions each, the dual POV characters. Aslan and Jadis follow at ~320 and ~310.

**Active agency ratio — this is the most interesting chart.** We normalize for frequency: what fraction of each character's mentions are active vs. passive/mentioned? Susan and Lucy lead around 74–78%. Then here's the paradox: **Aslan and Jadis bottom out at ~39%**. The two most powerful characters in the book are talked *about* far more than they act within individual sentences. Lewis constructs them as off-screen forces — their presence felt through other characters' fear and awe. The model surfaces this structural feature without being told to look for it.

**Edmund's suppressed agency.** Tied with Lucy in raw mentions, but his active ratio (64%) is the lowest Pevensie. His captivity arc in chapters 9–12 is visible directly in this number.

**Mr. Beaver punches above his weight at 73% active** — concentrated in action-dense scenes, rarely present in expository passages.

**Chapter density.** Mention-per-sentence peaks at chapters 8 and 15 — the beavers' escape planning and Aslan's resurrection and the battle. Chapter 1 is the sparsest (0.72/sentence), pure scene-setting. Entity density tracks narrative intensity across the arc.

**Character arc lines.** Lucy dominates early chapters as the discoverer of Narnia. Edmund's line peaks mid-book during his betrayal arc, then both converge toward the climax.

These findings are what the task was designed to reveal: not just who is in the text, but the structure of narrative agency — recoverable from LLM annotations at chapter scale, from a task description written in an afternoon.

---

## Timing Guide

| Segment | Content | Time |
|---------|---------|------|
| Talk 1 | Motivation | ~1:00 |
| Talk 2 | Solved tasks | ~1:00 |
| Talk 3 | Grammaticality + multilingual | ~1:30 |
| Talk 4 | Agency NER intro | ~1:30 |
| Visual 1 | Overall accuracy chart | ~0:30 |
| Visual 2 | Multilingual spreadsheets | ~1:00 |
| Visual 3 | 200-sentence benchmark tables | ~1:00 |
| Visual 4 | Full-book narnia charts | ~2:30 |
| **Total** | | **~10:30** |

---

## What to show on screen during demo

| Segment | File / location |
|---------|----------------|
| Overall accuracy chart | `srijon/scripts/graph.ipynb` → `ratio_histogram_bw.png` |
| Multilingual grouped chart | `srijon/scripts/graph.ipynb` → `grouped_accuracy.png` |
| Pronoun/presuppositions spreadsheets | model comparison CSVs in `srijon/scripts/` outputs |
| 200-sentence benchmark tables | `narnia/README.MD` results tables |
| Label distribution | `narnia-large/results/label_distribution.png` |
| Top characters | `narnia-large/results/top_characters.png` |
| Active agency ratio | `narnia-large/results/active_agency_ratio.png` |
| Chapter density | `narnia-large/results/chapter_density.png` |
| Character arcs | `narnia-large/results/character_arcs.png` |

---

## Rubric Checklist

- **Technical Achievement**: Multi-task benchmarking, novel agency NER task, 4-model comparison, zero/few-shot, per-label breakdown, prompt engineering experiment, 6-language multilingual eval, full-book 17-chapter analysis
- **Documentation & Communication**: Per-label README tables, multilingual charts, 5 narnia-large charts, this script
- **Project Impact**: LLMs enable custom linguistic annotation without engineering overhead — demonstrated end-to-end from task design to publishable literary findings
- **Testing & QA**: 200 gold-annotated sentences, 3 stratified samples per task, precision/recall/F1 per label, edge-case analysis (ADDRESSED, MISCELLANEOUS, prompt sensitivity), 4 models × 2 conditions, 2,404-sentence full-book validation
- **UX**: Prompt-only interface; CSV pipeline generates input/prediction/scoring files automatically
- **Video**: Project overview (motivation), key features (prompting + scoring pipeline), technical highlights (per-label F1, few-shot gains, Aslan/Jadis paradox, chapter density), use case (Narnia live results)
