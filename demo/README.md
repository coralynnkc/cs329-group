# CS329 Demo Presentation Script

**Format: ~8 min recording — one script section per slide, in order**

---

### Slide 1 — Title (~15 sec)

> **"Linguistics in NLP: Evaluating LLM Performance on Core Linguistics Tasks Across Languages"**

Welcome. This is our CS329 group project benchmarking LLM performance across core linguistics tasks — from well-defined problems like lemmatization to a novel task we designed from scratch.

---

### Slide 2 — Project Outline (~30 sec)

> **"Project Outline"**

Our four goals: baseline LLM performance across tasks and models, improve performance on difficult tasks through prompt engineering and low-resource languages, design a novel linguistic task to prove LLM generality, and develop conclusions and future directions.

---

### Slide 3 — 01 Project Motivation & Statement (~5 sec)

> **"01 — Project Motivation & Statement"**

---

### Slide 4 — "Imagine you're a linguistics professor..." (~1 min)

> **"Imagine you're a linguistics professor..."**

You want to identify what a speaker is taking for granted across 10,000 sentences — presuppositions. Can an LLM reliably do that in English? In Mandarin?

How do you do that today? You go to Dr. Choi and ask him to write a pipeline for you — heavy expenditure of resources for a single-use tool.

Our project asks: what if you didn't have to? LLMs are general-purpose annotation engines. A linguist can describe a task in plain English — define labels, give examples, explain edge cases — and an LLM applies that scheme to thousands of sentences without any training or pipeline engineering. We set out to benchmark how well this actually works, and for which kinds of tasks.

---

### Slide 5 — 02 Task-Based Analysis (~5 sec)

> **"02 — Task-Based Analysis"**

---

### Slide 6 — PROJECT: Baselining — Lemmatization, POS, NER (~45 sec)

> **"PROJECT: Baselining"**

We treat lemmatization as our proof of concept. Given an inflected word like _ate_ or _geese_, return the dictionary headword. Opus, Sonnet, and Gemini all score 96–97% accuracy. Solved — and this establishes that the prompting-based approach works in principle.

POS tagging and standard NER tell a similar story: Opus hits 94% on UD POS tags and 95% F1 on CoNLL-2003 NER with zero-shot prompting. Performance drops on out-of-domain data by about 4–5%, but these are strong baselines.

Notably, these tasks aren't perfectly defined — these label sets are considered the gold standard, yet linguistics sometimes needs to go beyond that. What if you want a label set more complex than PER, LOC, ORG?

---

### Slide 7 — PROJECT: Baselining — Presuppositions, Pronoun Resolution, Grammaticality (~30 sec)

> **"PROJECT: Baselining" (continued)**

Three harder tasks push the models further. Presuppositions across six languages: ~80–85% Macro-F1, but English scores the lowest — likely training contamination. Pronoun resolution is strong overall: 84–97% across four languages. And grammaticality on CoLA reveals that prompt choice is split-sensitive — one prompt inverts its performance between in-domain and out-of-domain data. Let's look at the numbers.

---

### Slide 8 — PROJECT: Presuppositions (~45 sec)

> **"PROJECT: Presuppositions"**

These are Macro-F1 scores across six languages. Sonnet 4.6 consistently outperforms ChatGPT 5.4 — French, German, Hindi, Russian, and Vietnamese all in the 0.82–0.92 range. English is the outlier: 0.59 for Sonnet, as low as 0.48 for ChatGPT. The neutral class collapses for both models in English, dragging the macro score down. English is where models have learned to pattern-match rather than reason.

---

### Slide 9 — PROJECT: Pronoun Resolutions (~30 sec)

> **"PROJECT: Pronoun Resolutions"**

Pronoun resolution is strong across the board — 84–97% accuracy. Russian is the highest for Sonnet at 95–97%, likely because morphological richness makes pronoun referents less ambiguous in Russian text. English is stable but not the top performer. Prompt engineering has marginal effect in English but larger effect in lower-resource settings.

---

### Slide 10 — PROJECT: Grammaticality Judgements (~45 sec)

> **"PROJECT: Grammaticality Judgements"**

Look at the `checklist` row: 56% in-domain vs 90% out-of-domain. That inversion is the finding. Every other prompt is consistent across splits — anchor, repair, and finetuned all land around 89% in-domain and 85–86% out-of-domain. Checklist alone flips. There is no single best prompt — and knowing that is itself a useful result for any linguist using LLMs to annotate data.

---

### Slide 11 — 03 Novel Task Design (~5 sec)

> **"03 — Novel Task Design"**

---

### Slide 12 — NARNIA: Task Definition (~45 sec)

> **"NARNIA: Task Definition"**

Our primary contribution is a novel NER task we designed from scratch: agency-based character recognition in _The Lion, the Witch and the Wardrobe_.

Standard NER tags Lucy as PER. We asked: is Lucy speaking, acting, being addressed, or just mentioned? We defined six labels — `ACTIVE_SPEAKER`, `ACTIVE_PERFORMER`, `ACTIVE_THOUGHT`, `ADDRESSED`, `MENTIONED_ONLY`, `MISCELLANEOUS` — and a canonical character list to handle surface form variation: the White Witch, the Queen, Her Imperial Majesty all resolve to Jadis.

This operationalizes _agency_: who actually drives the narrative vs. who is just talked about.

---

### Slide 13 — NARNIA: Data Transformation (~20 sec)

> **"NARNIA: Data Transformation"**

We transformed raw Narnia text into structured CSV data — each sentence paired with entity annotations and canonical character names. This is what gets fed to the model, and what the scoring pipeline evaluates against our 200 manually annotated ground-truth sentences.

---

### Slide 14 — NARNIA: NER Baseline Results (~45 sec)

> **"NARNIA: NER Baseline Results"**

Zero-shot: Opus 0.783 F1, Sonnet 0.741, Gemini 0.566, ChatGPT 0.586. Few-shot — eight examples in the prompt — pushed all models up: Sonnet to 0.823, Opus to 0.820, Gemini to 0.809.

Look at `MISCELLANEOUS`: 0.000 zero-shot across the board. It's a catch-all that needs examples to activate. And `ADDRESSED` — vocatives like _"Oh, Mr. Tumnus!"_ get misclassified as `MENTIONED_ONLY` zero-shot. One labeled example fixed it: Sonnet's ADDRESSED F1 jumped from 0.53 to 0.89.

---

### Slide 15 — NARNIA: Coreference Baseline Results (~30 sec)

> **"NARNIA: Coreference Baseline Results"**

We also ran coreference resolution — mapping surface forms back to canonical characters. Opus leads at 0.884 F1. Per-character, Bacchus, Ivy, Margaret, and Betty all hit 1.000 — minor characters with unambiguous surface forms. The hard cases are Jadis and Mr. Tumnus, where surface form variation trips up smaller models. Few-shot improves all models significantly.

---

### Slide 16 — NARNIA: Corpus Analysis — Label Distribution (~1 min)

> **"NARNIA: Corpus Analysis Results" — label distribution chart**

Then we scaled to the full book — 17 chapters, 2,404 sentences. Active Speaker 29.2%, Active Performer 22.2%, Active Thought 8.7%, Addressed 8.6%, Mentioned Only 30.4%, Misc 0.8%. About 60% of mentions are active. The model assigns agency wherever syntactic structure permits — which is itself interesting as a finding about the text.

---

### Slide 17 — NARNIA: Corpus Analysis — Agency per Character (~1.5 min)

> **"NARNIA: Corpus Analysis Results" — agency breakdown per character**

Edmund and Lucy are essentially tied at ~408 mentions each — the dual POV characters. Aslan and Jadis follow. Now look at the composition: Edmund and Lucy have large blocks of Active Speaker and Active Performer. Aslan and Jadis have comparatively large grey bars — Mentioned Only. The two most powerful characters in the book are talked _about_ far more than they act within individual sentences. Lewis constructs them as off-screen forces, their presence felt through other characters' fear and awe. The model surfaces this structural feature without being told to look for it.

Mr. Beaver punches above his weight in active mentions — concentrated in action-dense scenes, rarely present in expository passages.

This is what the task was designed to reveal: not just who is in the text, but the structure of narrative agency — recoverable from LLM annotations at chapter scale, from a task description written in an afternoon.

---

### Slide 18 — Thank You (~10 sec)

> **"Thank You!"**

Thanks for watching. Full results, scoring scripts, and the annotated dataset are all in the repo.

---

## Timing Guide

| Slide | Content                              | Time   |
| ----- | ------------------------------------ | ------ |
| 1     | Title                                | ~0:15  |
| 2     | Project Outline                      | ~0:30  |
| 3–4   | Motivation                           | ~1:05  |
| 5–7   | Baselining overview                  | ~1:20  |
| 8     | Presuppositions table                | ~0:45  |
| 9     | Pronoun resolution table             | ~0:30  |
| 10    | Grammaticality table                 | ~0:45  |
| 11–13 | Novel task intro + data              | ~1:10  |
| 14    | NER baseline results                 | ~0:45  |
| 15    | Coreference baseline results         | ~0:30  |
| 16    | Corpus analysis — label distribution | ~1:00  |
| 17    | Corpus analysis — agency per char    | ~1:30  |
| 18    | Thank you                            | ~0:10  |
| **Total** |                                 | **~10:15** |

---

## Rubric Checklist

- **Technical Achievement**: Multi-task benchmarking, novel agency NER task, 4-model comparison, zero/few-shot, per-label breakdown, prompt engineering experiment, 6-language multilingual eval, full-book 17-chapter analysis, coreference resolution
- **Documentation & Communication**: Per-label README tables, multilingual tables, corpus analysis charts, coreference per-character breakdown, this script
- **Project Impact**: LLMs enable custom linguistic annotation without engineering overhead — demonstrated end-to-end from task design to publishable literary findings
- **Testing & QA**: 200 gold-annotated sentences, 3 stratified samples per task, precision/recall/F1 per label, edge-case analysis (ADDRESSED, MISCELLANEOUS, prompt sensitivity), 4 models × 2 conditions, 2,404-sentence full-book validation
- **UX**: Prompt-only interface; CSV pipeline generates input/prediction/scoring files automatically
- **Video**: Project overview (motivation), key features (prompting + scoring pipeline), technical highlights (per-label F1, few-shot gains, Aslan/Jadis narrative structure, English presupposition outlier), use case (Narnia live results)
