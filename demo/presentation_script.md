# CS329 Demo Presentation Script
**Format: ~5 min talk + ~5 min demo/visuals**

---

## PART 1 — TALK (~5 minutes)

---

### 1. Motivation (1 min)

Imagine you're a linguistics professor. You want to identify what a speaker is taking for granted across 10,000 sentences — presuppositions. Can an LLM reliably do that in English? In Mandarin?

How do you do that today? You go to Dr. Choi and ask him to write a pipeline for you, requiring heavy expenditure of resources for a single-use, targeted tool.

Our project asks: what if you didn't have to?

LLMs are general-purpose annotation engines. A linguist can describe a task in plain English — define labels, give examples, explain edge cases — and an LLM applies that scheme to thousands of sentences without any training or pipeline engineering. We set out to systematically benchmark how well this actually works, and for which kinds of tasks. Our four goals: baseline LLM performance across tasks and models, improve performance on difficult tasks via prompt engineering and low-resource languages, design a novel linguistic task to prove LLM generality, and develop conclusions and future directions.

---

### 2. Background: What's Already Solved (1 min)

We treat **lemmatization** as our proof of concept. Given an inflected word like *ate* or *geese*, return the dictionary headword: *eat*, *goose*. Opus, Sonnet, and Gemini all score 96–97% accuracy. Solved.

**POS tagging** and **standard NER** tell a similar story: Opus hits 94% on UD POS tags and 95% F1 on CoNLL-2003 NER with zero-shot prompting, though performance drops on out-of-domain data by about 4–5%.

These tasks establish that the prompting-based approach works *in principle*. But notably, they aren't perfectly defined — these datasets and label sets are considered a gold standard, yet linguistics sometimes needs to go beyond that. What if a different language uses different parts of speech? What if you want a label set more complex than PER, LOC, ORG?

---

### 3. Harder Tasks: Grammaticality, Presuppositions, Pronoun Resolution (1.5 min)

Grammaticality judgment is harder. CoLA sentences come from linguistics papers and test subtle phenomena — island constraints, binding violations, agreement errors. Our prompt comparison experiment across five designs shows that **prompt choice is split-sensitive**: the `checklist` prompt collapses in-domain (56% accuracy, negative MCC) but becomes the best out-of-domain (90% accuracy). `Direct` is the safest general baseline. There is no single best prompt — and knowing that is itself a useful finding for any linguist using LLMs to annotate data.

Presuppositions and pronoun resolution push the models further. For presuppositions, our improvised and fine-tuned methods achieve Macro-F1 scores of **~80–85% consistently** across six languages (DE, EN, FR, HI, RU, VI) — but English scores the lowest, and the neutral class collapses in both models. Sonnet 4.6 ranges from 0.59 (EN) to 0.88 (DE, FR, RU, VI); ChatGPT 5.4 ranges from 0.48 (EN, P4) to 0.92 (FR, P4). English is the outlier — likely training contamination, where the model has learned to pattern-match rather than reason.

Pronoun resolution is deterministic and shows strong performance overall: **English 89% (stable across prompts), French 88–91%, German 86–88%, Russian 95–97%** for Sonnet 4.6. Prompt engineering has marginal effect in English but larger effect in lower-resource settings. The Russian result — highest of any language — is striking and likely reflects the morphological richness that makes pronoun referents less ambiguous in Russian text.

---

### 4. Our Task: Agency NER in Narnia (1.5 min)

Our primary contribution is a novel NER task we designed from scratch: **agency-based character recognition in narrative text**, applied to *The Lion, the Witch and the Wardrobe*.

Standard NER tags Lucy as PER. We asked: is Lucy speaking, acting, being addressed, or just mentioned? We defined six labels: `ACTIVE_SPEAKER`, `ACTIVE_PERFORMER`, `ACTIVE_THOUGHT`, `ADDRESSED`, `MENTIONED_ONLY`, `MISCELLANEOUS`.

This operationalizes *agency* — a core concept in linguistics that concerns how language encodes control and participation in events. It lets linguists ask: who actually drives the narrative vs. who is just talked about?

We manually annotated 200 sentences as ground truth, then transformed the raw text into structured CSV data pairing sentences with entity annotations. Zero-shot: Opus 0.783 F1, Sonnet 0.741, Gemini 0.566, ChatGPT 0.586. Few-shot — eight examples in the prompt — pushed all models up: Sonnet to 0.823, Opus to 0.820, Gemini to 0.809. The hardest label zero-shot was `ADDRESSED` (vocatives like *"Oh, Mr. Tumnus!"* get misclassified as `MENTIONED_ONLY`). One labeled example fixed it: Sonnet's ADDRESSED F1 jumped from 0.53 to 0.89.

We also ran coreference resolution — mapping surface forms like "the White Witch" back to canonical characters. Opus leads at 0.884 F1 overall; ChatGPT struggles with precision (0.28 zero-shot). Few-shot improves all models significantly.

Then we scaled to the full book — 17 chapters, 2,404 sentences — and the annotations reveal real linguistic structure. Let me show you what that looks like.

---

## PART 2 — DEMO / VISUALS (~5 minutes)

---

### Visual 1: Baselining Results — Presuppositions Table (45 sec)

> **Show: "PROJECT: Presuppositions" slide**

These are the Macro-F1 scores across six languages. Sonnet 4.6 consistently outperforms ChatGPT 5.4, with French, German, Hindi, Russian, and Vietnamese all in the 0.82–0.92 range. English is the outlier — 0.59 for Sonnet, as low as 0.48 for ChatGPT. The neutral class collapses for both models in English, dragging the macro score down.

---

### Visual 2: Pronoun Resolution & Grammaticality Tables (1 min)

> **Show: "PROJECT: Pronoun Resolutions" slide, then "PROJECT: Grammaticality Judgements" slide**

Pronoun resolution is strong across the board — 84–97% accuracy. Russian is the highest for Sonnet at 95–97%; English is stable but not the top performer.

For grammaticality, look at the `checklist` row: 56% in-domain vs 90% out-of-domain. That inversion is the finding. Every other prompt is consistent across splits; checklist alone flips. Anchor, repair, and finetuned all land around 89% in-domain and 85–86% out-of-domain.

---

### Visual 3: Narnia NER & Coreference Baseline Results (1 min)

> **Show: "NARNIA: NER Baseline Results" slide, then "NARNIA: Coreference Baseline Results" slide**

NER: zero-shot vs few-shot, all four models. Sonnet and Opus lead zero-shot; all models improve meaningfully with few-shot. MISCELLANEOUS is 0.000 zero-shot across the board — it's a catch-all category that needs examples to activate.

Coreference: Opus is the clear winner at 0.884 F1. Per-character, Bacchus, Ivy, Margaret, and Betty all hit 1.000 — minor characters with unambiguous surface forms. The hard cases are Jadis (the White Witch / the Queen) and Mr. Tumnus, where surface form variation trips up smaller models.

---

### Visual 4: Full-Book Agency Analysis — Corpus Charts (2.5 min)

> **Show: "NARNIA: Corpus Analysis Results" — label distribution chart, then agency breakdown per character**

Now the full-book results. 2,404 sentences, over 2,300 entity mentions.

**Label distribution.** Active Speaker 29.2%, Active Performer 22.2%, Active Thought 8.7%, Addressed 8.6%, Mentioned Only 30.4%, Misc 0.8%. About 60% of mentions are active. The model assigns agency wherever syntactic structure permits — which is itself interesting as a finding about the text.

**Agency breakdown per character.** Edmund and Lucy are essentially tied at ~408 mentions each, the dual POV characters. Aslan and Jadis follow. Now look at the composition: Edmund and Lucy have large blocks of Active Speaker and Active Performer. Aslan and Jadis have comparatively large grey bars — Mentioned Only. The two most powerful characters in the book are talked *about* far more than they act within individual sentences. Lewis constructs them as off-screen forces — their presence felt through other characters' fear and awe. The model surfaces this structural feature without being told to look for it.

Mr. Beaver punches above his weight in active mentions — concentrated in action-dense scenes, rarely present in expository passages.

These findings are what the task was designed to reveal: not just who is in the text, but the structure of narrative agency — recoverable from LLM annotations at chapter scale, from a task description written in an afternoon.

---

## Timing Guide

| Segment | Content | Time |
|---------|---------|------|
| Talk 1 | Motivation | ~1:00 |
| Talk 2 | Solved tasks | ~1:00 |
| Talk 3 | Grammaticality + multilingual | ~1:30 |
| Talk 4 | Agency NER intro | ~1:30 |
| Visual 1 | Presuppositions table | ~0:45 |
| Visual 2 | Pronoun resolution + grammaticality | ~1:00 |
| Visual 3 | NER + coreference baseline tables | ~1:00 |
| Visual 4 | Full-book corpus charts | ~2:30 |
| **Total** | | **~10:15** |

---

## What to show on screen during demo

| Segment | Slide |
|---------|-------|
| Presuppositions table | "PROJECT: Presuppositions" slide |
| Pronoun resolution table | "PROJECT: Pronoun Resolutions" slide |
| Grammaticality table | "PROJECT: Grammaticality Judgements" slide |
| NER baseline results | "NARNIA: NER Baseline Results" slide |
| Coreference baseline results | "NARNIA: Coreference Baseline Results" slide |
| Label distribution | "NARNIA: Corpus Analysis Results" (chart 1) |
| Agency breakdown per character | "NARNIA: Corpus Analysis Results" (chart 2) |

---

## Rubric Checklist

- **Technical Achievement**: Multi-task benchmarking, novel agency NER task, 4-model comparison, zero/few-shot, per-label breakdown, prompt engineering experiment, 6-language multilingual eval, full-book 17-chapter analysis, coreference resolution
- **Documentation & Communication**: Per-label README tables, multilingual tables, corpus analysis charts, coreference per-character breakdown, this script
- **Project Impact**: LLMs enable custom linguistic annotation without engineering overhead — demonstrated end-to-end from task design to publishable literary findings
- **Testing & QA**: 200 gold-annotated sentences, 3 stratified samples per task, precision/recall/F1 per label, edge-case analysis (ADDRESSED, MISCELLANEOUS, prompt sensitivity), 4 models × 2 conditions, 2,404-sentence full-book validation
- **UX**: Prompt-only interface; CSV pipeline generates input/prediction/scoring files automatically
- **Video**: Project overview (motivation), key features (prompting + scoring pipeline), technical highlights (per-label F1, few-shot gains, Aslan/Jadis narrative structure, English presupposition outlier), use case (Narnia live results)
