# CS329 Demo Presentation Script
**Target length: 9–10 minutes (~1,400 words spoken at ~150 wpm)**

---

## Section 1 — Motivation (1.5 min)

> **Screen: title slide**

Linguistics is fundamentally an empirical discipline. Linguists form hypotheses about how language works — how words are structured, how sentences are built, how narratives distribute agency across characters — and then they need to test those hypotheses on real corpora.

The problem is scale. Manual annotation is slow. Hiring an NLP engineer to build a custom pipeline is expensive and requires the linguist to translate their theoretical framework into someone else's technical vocabulary. And existing pre-built tools only support the tasks that were already popular enough to get built — which means anything novel, anything niche, anything that crosses theoretical boundaries, either doesn't get studied or gets studied on toy-sized datasets.

Large language models change this dynamic. A linguist can now describe a custom annotation task in plain English, give a few examples, and get that task applied to tens of thousands of sentences immediately — no training data, no pipeline, no engineer.

The question we set out to answer is: **how well does this actually work, and for which kinds of tasks?** We built a systematic benchmarking framework across six NLP tasks at increasing levels of complexity, tested four frontier models, and designed one completely novel task from scratch. This is that story.

---

## Section 2 — The Benchmarking Framework (1 min)

> **Screen: task complexity spectrum diagram**

Our framework covers six task types, ordered by linguistic complexity:

1. **Lemmatization** — return the dictionary headword of an inflected form
2. **POS tagging** — assign Universal Dependencies tags token by token
3. **Standard NER** — identify persons, organizations, locations (CoNLL-2003)
4. **Grammaticality judgment** — binary CoLA acceptability, with prompt comparison
5. **Pronoun resolution & presuppositions** — discourse-level tasks across six languages
6. **Agency NER in Narnia** — our novel task, defined from scratch

For each task, we ran three stratified samples, scored precision/recall/F1 or accuracy, and compared four models: Claude Sonnet, Claude Opus, Gemini, and ChatGPT.

---

## Section 3 — Solved Tasks: Proof of Concept (2 min)

> **Screen: lemmatization and POS results tables**

Let's start with tasks where LLMs are effectively already solved.

**Lemmatization.** Given an inflected word — say, *ate*, *geese*, *running* — return its base form. We tested 900 UniMorph English items across three samples. Opus, Gemini, and Sonnet all scored between 96–97% accuracy with near-zero edit distance. ChatGPT was the outlier at 70% — a meaningful gap that shows model tier still matters even for tasks this well-specified. But the headline is: frontier models have essentially solved morphological lemmatization through prompting alone, with no fine-tuning.

**POS tagging.** Assigning Universal Dependencies tags — NOUN, VERB, ADJ, AUX, and 13 others — token by token. Opus leads at 94% token accuracy. Sonnet and Gemini cluster around 83–85%. ChatGPT at 81%. The harder tags reveal where models struggle: the X tag (words that don't fit any category) gets near-zero F1 from every model. SCONJ (subordinating conjunctions) is consistently weak. PUNCT and CCONJ are near-perfect. This is not random — it tracks exactly what you'd expect from models trained on surface-level text patterns rather than deep syntactic structure.

**Standard NER.** CoNLL-2003 newswire NER — PER, ORG, LOC, MISC. Opus reaches 94.9% F1, Gemini 93%, Sonnet 92%, ChatGPT 90.5%. These are competitive with fine-tuned baselines from several years ago. The task is well-represented in training data and the label set is small and unambiguous.

These three tasks establish a baseline: the prompting approach works well for tasks that are well-defined, frequently seen in training, and have small, clean label sets. They're the proof of concept that LLMs can function as annotation engines.

---

## Section 4 — Harder Tasks: Where It Gets Interesting (2 min)

> **Screen: grammaticality-2.0 results table, then pronoun resolution**

### Grammaticality Judgment

CoLA asks whether an English sentence is grammatically acceptable. This sounds simple — but many CoLA sentences are drawn from linguistics papers and test subtle phenomena: island constraints, binding violations, agreement errors. The sentence "Books were sent to each other by the students" is syntactically ill-formed in a way that's easy to miss.

We ran a prompt comparison experiment using five designs on Chat 5.4 across in-domain and out-of-domain CoLA splits. The five prompts were: `direct` (just classify), `anchor` (with reference examples), `repair` (ask whether the sentence can be repaired), `finetuned` (mirroring the CoLA annotation guidelines), and `checklist` (step-by-step feature checklist).

The key finding: **prompt engineering matters, but the effect is split-sensitive.**

- In-domain: `anchor`, `repair`, and `finetuned` tie at 89% accuracy / 0.745 MCC. `checklist` collapses to 56% accuracy and a negative MCC — worse than chance.
- Out-of-domain: the ranking inverts. `checklist` becomes the best performer at 90% accuracy / 0.762 MCC.

There is no universally dominant prompt. The `direct` prompt is the safest all-purpose choice — it never collapses — but the variation shows that linguistic task performance isn't just about model capability. It's about the match between the prompt's framing and the distribution of the data. That's a finding linguists need to know before they trust LLM outputs on their corpora.

### Pronoun Resolution & Presuppositions

For pronoun resolution, we used WinoGrande-style contexts across English, French, German, and Russian. For presuppositions — whether a hypothesis is entailed, contradicted, or neutral given a premise — we used XNLI data across six languages including Hindi and Vietnamese.

These tasks require reasoning across sentence boundaries: tracking referents, inferring implication, handling negation. They also expose crosslinguistic variation. Models that perform well in English often degrade meaningfully on lower-resource languages in their training data. Quantifying that degradation is exactly the kind of analysis our pipeline enables.

---

## Section 5 — Primary Research: Agency NER in Narnia (3 min)

> **Switch to live demo or screen recording**

This brings us to our primary contribution: a novel NER task we designed entirely from scratch, with no pre-existing benchmark, no training data, and no established label set.

**The task:** Given a sentence from *The Lion, the Witch and the Wardrobe*, identify every character mention and classify the narrative role that character plays in that sentence. Not just *who* is mentioned — but *how* they're participating.

Standard NER would give you: Lucy = PER. We wanted more. We defined six agency labels:

| Label | What it captures | Example |
|-------|-----------------|---------|
| `ACTIVE_SPEAKER` | Character speaks in dialogue | *"said Lucy"* |
| `ACTIVE_PERFORMER` | Character performs a physical action | *"Edmund ran toward the door"* |
| `ACTIVE_THOUGHT` | Character has an internal state | *"Lucy was tired"* |
| `ADDRESSED` | Character is spoken to or called | *"Oh, Mr. Tumnus!"* |
| `MENTIONED_ONLY` | Third-person reference, no agency | *"They spoke of Aslan"* |
| `MISCELLANEOUS` | Group/species labels used as names | *"Son of Adam", "Daughter of Eve"* |

Why does this matter linguistically? Agency is central to how narratives construct meaning. A character who is frequently mentioned is not necessarily one who drives the plot. By distinguishing between entities that act and entities that are acted upon or simply referenced, you can study: how agency is distributed across a cast of characters, how narrative focus is constructed, how perceived importance in cultural memory (the Mandela effect angle) diverges from actual participation in the text.

These are real research questions that were essentially computationally inaccessible before LLMs. You couldn't train a model for this — there's no corpus. You couldn't use standard NER tools — they don't have these categories. The only path was to describe the task to a capable model and test whether it could apply it.

**We manually annotated 200 sentences from Narnia as ground truth.** Then we ran zero-shot and few-shot baselines across four models.

**Zero-shot results (entity-level F1):**

| Model | Precision | Recall | F1 |
|-------|-----------|--------|-----|
| Opus | 0.790 | 0.777 | 0.783 |
| Sonnet | 0.715 | 0.769 | 0.741 |
| ChatGPT | 0.526 | 0.661 | 0.586 |
| Gemini | 0.561 | 0.570 | 0.566 |

That's already surprisingly high for a task no model has ever seen. But the per-label breakdown tells the real story.

`ACTIVE_SPEAKER` is the easiest label across all models — F1 above 0.73 for everyone. The pattern "said X" is unambiguous. `MISCELLANEOUS` gets **zero F1 from every model** zero-shot. `ADDRESSED` is the sharpest discriminator: ChatGPT scores 0.851, Sonnet 0.529, Opus 0.571. The failure mode is consistent — vocatives like *"Oh, Mr. Tumnus!"* get classified as `MENTIONED_ONLY` because the model doesn't recognize the direct-address structure.

**Then we added few-shot examples.** Eight labeled sentences in the prompt — one per label, including an ADDRESSED example and two MISCELLANEOUS examples.

**Few-shot results:**

| Model | F1 |
|-------|----|
| Sonnet | 0.823 |
| Opus | 0.809 |
| Gemini | 0.809 |
| ChatGPT | 0.797 |

Every model improved. The gains are concentrated exactly where zero-shot failed:

- Sonnet ADDRESSED: 0.529 → 0.889
- Sonnet MISCELLANEOUS: 0.000 → 0.800
- Gemini overall: +0.244 — the largest single-model gain across the whole project

This is the mechanism in action. A linguist notices the model is missing vocatives. They add one example of "Oh, Mr. Tumnus!" labeled as ADDRESSED. The model immediately generalizes and fixes the failure mode across the entire evaluation set — no retraining, no data collection, no engineering.

> **[Live demo: paste 3–4 Narnia sentences into the prompt, show model output, compare to gold answers]**

---

## Section 6 — Conclusion (1 min)

> **Screen: summary slide**

Let's pull the threads together.

We've shown that LLMs are strong enough to function as general-purpose annotation engines across a wide range of NLP tasks. The simpler and more training-data-adjacent the task, the closer to human-level performance. But even on a completely novel task with no training precedent — agency NER in a single literary work — frontier models achieve 0.74–0.78 F1 out of the box and 0.80–0.82 with eight labeled examples in the prompt.

The failure modes are not random. They're systematic, learnable, and correctable through targeted prompting. That's what makes this useful in practice. A linguist doesn't need to achieve perfection — they need to understand where the model fails and how to guide it.

The broader implication: the barrier between having a research question about language and being able to answer it computationally has dropped dramatically. You no longer need to build a pipeline. You need to be able to describe what you want clearly enough for an LLM to apply it. That is a skill linguists already have.

---

## Timing Guide

| Section | Content | Target time |
|---------|---------|-------------|
| 1 | Motivation | ~1:30 |
| 2 | Framework overview | ~1:00 |
| 3 | Solved tasks (lemmatization, POS, NER) | ~2:00 |
| 4 | Harder tasks (grammaticality, pronoun/presuppositions) | ~2:00 |
| 5 | Narnia agency NER + demo | ~3:00 |
| 6 | Conclusion | ~1:00 |
| **Total** | | **~10:30 — trim as needed** |

---

## Rubric Checklist

- **Technical Achievement**: Multi-task benchmarking framework, novel annotation task (agency NER), 4-model comparison, zero/few-shot conditions, per-label breakdown, prompt engineering experiment, multilingual evaluation
- **Documentation & Communication**: Per-label analysis in README, this script, rubric-mapped conclusion
- **Project Impact**: Direct argument that LLMs enable custom annotation without engineering — with quantitative evidence for which task types and prompt designs succeed
- **Testing & QA**: 200 manually annotated gold sentences (Narnia), 3 stratified samples per task, precision/recall/F1 per label, edge-case analysis (ADDRESSED, MISCELLANEOUS, split-sensitive prompts), 4 models × 2 prompt conditions
- **UX**: Prompt-only interface — user describes the task in natural language; pipeline generates input/prediction/scoring CSVs automatically
- **Video coverage**: Project overview (motivation), key features (prompting pipeline, scoring scripts), technical highlights (per-label F1, few-shot gains, prompt comparison flip), use case (Narnia agency NER live demo)
