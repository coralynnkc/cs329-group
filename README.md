# Working Document — LLMs for Linguistic Annotation
*Last updated: 2026-04-18*

---

## Thesis

LLMs can serve as general-purpose linguistic annotation tools using prompt engineering alone — no fine-tuning, no labeled training data, no task-specific pipelines. We demonstrate this across multiple tasks, with particular attention to where supervised models *can't* generalize (new label schemas, low-resource languages, out-of-domain data).

Three claims, in order of how well we can currently defend them:

1. **Generality** — one approach works across structurally different tasks (POS, lemmatization, grammaticality, NER)
2. **No training needed** — prompting alone matches or approaches SOTA on several tasks, especially where SOTA degrades out-of-domain
3. **Multilingual** — LLMs generalize to low-resource languages where dedicated tools are sparse or absent

---

## Task × Goal Matrix

Each task is selected to illustrate a specific failure mode of existing supervised pipelines. This table maps every module to the project claims it supports.

| Task | Module | Generality | No Training Needed | Multilingual | Status |
|------|--------|:----------:|:-----------------:|:------------:|--------|
| Lemmatization | `lemmatization/` | ✓ | **primary** — matches SOTA | — | done |
| Grammaticality / CoLA binary | `grammatical/` | ✓ | **primary** — fills gap where tools are absent | — | done |
| POS tagging | `pos/` | ✓ | **primary** — competitive in-domain; OOD story pending | — | done (in-domain) |
| Grammaticality 2.0 (CoLA + BLiMP) | `grammaticality-2.0/` | ✓ | **primary** — prompt design story; MCC/F1/BLiMP | — | CoLA fully scored (all prompts × both splits); BLiMP pending |
| Pronoun resolution (EN/AM/IG/ZU + EN/DE/FR/RU) | `pronoun_resolution/testing/`, `srijon-2.0/` | ✓ | ✓ | **primary** — 7 languages; low-resource degradation | mostly done |
| NER | `ner/` | **primary** — novel schemas supervised models can't handle | ✓ | — | **done** — all 4 models fully scored (CoNLL-2003) |
| Agency-based NER (Narnia) | `narnia/` | **primary** — custom schema; no supervised baseline possible | ✓ | — | **done** — all 4 models fully scored (zero-shot) |

**Key:** ✓ = task supports this goal; **primary** = task is the main evidence for this goal; — = not applicable or not a focus.

---

## What we have

### Fully scored (results in hand)

| Task | Module | Models scored | SOTA comparison | Key result |
|------|--------|---------------|-----------------|------------|
| Lemmatization | `lemmatization/` | Chat 5.4, Gemini 3, Sonnet 4.6, Opus 4.6 | spaCy/stanza ~95–99% | sonnet/opus match SOTA (~96–97%) |
| Grammaticality / CoLA binary | `grammatical/` | Chat 5.4, Gemini 3, Sonnet 4.6, Opus 4.6 | human ~80% | sonnet 84%, opus 88%; chatgpt ~49% |
| POS tagging (in-domain) | `pos/` | Chat 5.4, Gemini 3, Sonnet 4.6, Opus 4.6 | spaCy/udpipe ~97–98% | opus 94%; sonnet 85%; chatgpt 81% |
| Grammaticality 2.0 (CoLA) | `grammaticality-2.0/` | Chat 5.4 | — | direct/anchor/repair ~88–89% acc, MCC 0.73–0.75 in-domain; checklist collapses in-domain but recovers OOD (90% acc, MCC 0.76) |
| Pronoun resolution (EN/AM/IG/ZU + EN/DE/FR/RU) | `pronoun_resolution/testing/`, `srijon-2.0/` | sonnet 4.6 (7 langs), GPT 5.4 (full EN/DE/FR/RU); partial IG/ZU | chance = 50% | EN: 87–91%; FR/DE/RU: 86–97%; IG/ZU near chance; see table below |
| NER (CoNLL-2003) | `ner/` | Chat 5.4, Gemini 3, Sonnet 4.6, Opus 4.6 | spaCy/stanza F1 ~91% | opus 0.95; gemini 0.93; sonnet 0.92; chatgpt 0.26 (failure — see note below) |
| Agency-based NER (Narnia) | `narnia/` | Chat 5.4, Gemini 3, Sonnet 4.6, Opus 4.6 | no supervised baseline (novel schema) | opus F1 0.78; chatgpt F1 0.78; sonnet F1 0.74; gemini F1 0.20 (failure) |

#### Multilingual pronoun resolution — full results (srijon-2.0)

| Language | Sonnet 4.6 acc (P0→P4) | GPT 5.4 acc (P0→P4) |
|----------|------------------------|----------------------|
| English  | 89% (stable P0–P4)     | 84–86%               |
| French   | 88–91%                 | 90–93%               |
| German   | 86–88%                 | 88–89%               |
| Russian  | 95–97%                 | 90–93%               |

Both models fully scored. Prompt engineering has marginal effect in English; larger effect in lower-resource settings.

### Predictions done, scoring incomplete

| Task | What exists | What's missing |
|------|-------------|----------------|
| Grammaticality 2.0 (BLiMP) | `blimp_summary.csv` exists (headers-only) | No prediction files yet |

### Partially done

| Task | Gap |
|------|-----|
| Pronoun resolution (EN/AM/IG/ZU) — Igbo | P2–P4 missing for sonnet; chatgpt only P0 |
| Pronoun resolution (EN/AM/IG/ZU) — Zulu | P2–P4 missing for sonnet; chatgpt only P0 |
| Pronoun resolution (EN/AM/IG/ZU) — Opus | only P0 for EN; nothing for AM/IG/ZU |
| Pronoun resolution challenge splits (all languages) | splits generated; no predictions yet |

### New data splits (ready for baselining)

**Challenge splits** — difficulty-stratified subsets of the train data, selected using a composite heuristic (sentence length, clause markers, blank-candidate distance). Generated for all 7 languages via `srijon-2.0/scripts/generate_challenge_splits.py`.

| Module | Languages | Challenge size | Holdout size |
|--------|-----------|---------------|--------------|
| `srijon-2.0/pronoun_resolution/` | EN, DE, FR, RU | 50 items each | remainder of train |
| `pronoun_resolution/testing/` | EN, AM, IG, ZU | ~70 items each | — |

Source, inference, and full versions of each split are generated and committed. No predictions have been run yet — these are the next baselining targets.

### Not started

- POS out-of-domain evaluation (the key argument: SOTA drops 4–5% OOD; LLMs may hold)
- Grammaticality on non-English benchmarks
- NER few-shot and novel-schema experiments
- BLiMP pairwise predictions for any model

---

## Empirical findings so far

1. **Chunking matters a lot.** Performance throttling from too-large chunks is hard to detect. Include refusal as an option rather than forcing a label.

2. **"Think like a linguist" prompts are counterproductive.** Providing explicit linguistic heuristics tends to hurt, not help — LLMs likely find richer patterns than a brief prompt can outline.

3. **Prompt engineering has weaker effect than expected for well-understood tasks.** For English grammaticality and pronoun resolution, a minimal prompt usually outperforms elaborate scaffolding.

4. **The prompt effect is not uniform across languages.** In lower-resource settings (Igbo, Zulu), prompt wording matters more — models operate closer to their uncertainty boundary.

5. **Training data matters more than architecture** (per recent literature; see `cora-notes/training_data_vs_architecture_papers.docx`).

6. **ChatGPT NER failure is qualitatively distinct.** F1 0.26 vs. 0.92–0.95 for all other models. Failure modes: massive overclassification of common words/pronouns, near-universal PER collapse for locations, and full headlines treated as single LOC spans. Likely a prompt-conformance failure specific to that model version.

7. **Presuppositions: "Neutral" label collapses for English in both models.** EN scores ~10–20 pp below all other languages; neutral recall near 0.06–0.12 vs. 0.60–0.73 for other languages. Likely a dataset artifact — EN XNLI neutrals may be subtler than translated versions.

---

## What we have left to do

### 1. Complete baselining

**Grammaticality 2.0 BLiMP** — run pairwise predictions for at least sonnet and GPT 5.4.

**Pronoun resolution (EN/AM/IG/ZU) gaps** — run missing cells:
- Sonnet: IG P2–P4, ZU P2–P4
- ChatGPT: all languages P1–P4
- Opus: AM/IG/ZU P0 at minimum

**Challenge splits** — all 7 languages now have difficulty-stratified challenge sets (50 items for srijon-2.0, ~70 for pronoun_resolution/testing). Run at least sonnet and GPT 5.4 on these to test whether hard items drive the low-resource degradation story.

**POS out-of-domain** — run existing models on an out-of-domain source. This is the clearest head-to-head: SOTA degrades ~4–5% OOD; LLM should hold or degrade less.

### 2. NER — generality proof of concept

**Zero-shot baselining is done (all 4 models).** Results: opus F1 0.78, chatgpt F1 0.78, sonnet F1 0.74, gemini F1 0.20 (collapse — similar to chatgpt CoNLL failure pattern).

The argument: supervised NER is trained on fixed schemas (PER, LOC, ORG) and cannot adapt when the label set changes. LLMs handle novel, theory-driven annotation schemes without retraining. Our demo is **agency-based NER in narrative texts** — a custom schema that no supervised model has been trained on.

**Task:** Given sentences from *The Chronicles of Narnia*, classify each named entity by its agentive role:
- **Active entity** — drives the event (e.g., "Lucy opened the wardrobe.")
- **Passive entity** — acted upon (e.g., "Edmund was captured by the Witch.")
- **Mentioned indirectly** — referenced without participation (e.g., "They spoke of Aslan in hushed tones.")

This operationalizes linguistic agency (thematic roles, transitivity, voice) as an NER-style annotation task — something no fixed-schema supervised model can do without retraining on a new label set.

**Why this proves generality:** The schema is custom and theory-driven. Supervised models trained on CoNLL or OntoNotes cannot perform this task at all. LLMs handle it via prompting alone, demonstrating that the same interface generalizes to arbitrary user-defined annotation schemes.

**Next steps (optional):**
- Few-shot (2–4 examples per type): test in-context learning sensitivity
- Comparison baseline: standard NER tools (spaCy, stanza) applied to the same text — they extract entities but cannot assign agency labels
- Per-role F1 breakdown (active / passive / mentioned)

**Prompting techniques to explore (from `cora-notes/prompting_notes_0416_revised.pdf`):**
- Text-to-text with special tokens: `[ENTITY]...[/ENTITY]` inline markup
- Chain-of-thought: reason first, then produce entity list
- Code-based extraction: ask model to output a Python dict / dataclass

### 3. Prompt engineering — qualitative analysis

Goal: don't just show accuracy numbers; show *which constructions* improve with better prompts and explain why.

**Grammaticality:**
- BLiMP gives per-construction-type breakdowns (subject-verb agreement, island constraints, binding, etc.)
- Document where MCC improves from direct → checklist → repair prompt
- Expected finding from literature: better on agreement/word order violations; worse on island constraints and center embedding

**Pronoun resolution:**
- P0 vs. P1 (two-shot) comparison already in hand for EN: 87% → 91%
- Igbo/Zulu near-chance even with few-shot — worth documenting as the multilingual failure mode
- Run P2–P4 for remaining languages to complete the prompt × language matrix

**NER:**
- Position bias and overclassification are the known failure modes — document their frequency per prompt type

---

## Argument structure (how results tie together)

```
Lemmatization         → "solved" anchor: prompting = SOTA, no training needed
Grammaticality        → "no tool exists": LLMs fill a gap, prompt design matters
POS tagging           → "LLMs competitive OOD where SOTA degrades"
Pronoun resolution    → "multilingual": English strong, low-resource languages degrade gracefully
NER (CoNLL-2003)      → "generality": strong baseline (opus F1 0.95); supervised schema
NER (Narnia / agency) → "generality proof of concept": custom agency schema, no supervised baseline; opus/chatgpt F1 ~0.78, gemini collapses
```

The through-line for the paper: each task is chosen to illustrate a different failure mode of existing supervised pipelines. LLMs via prompting address all of them from a single interface.

---

## Deprioritized

- **Presupposition** — sparse literature (~20 papers), risky positioning. Sonnet P0–P1 all 6 languages + chat 5.4 P0–P3 for DE/EN/FR now done. Key finding: P2 best for E/N boundary, P4 best all-around; English hardest (neutral collapses), French most stable. Only pursue further if another task is dropped. See `srijon-2.0/presuppositions/README.md` for full analysis.
- **Coreference** — requires training to be competitive; deprioritize

---

## Open decisions
- [ ] Is Claire running sonnet gramticality 2.0?
- [ ] Investigate EN presuppositions neutral-class collapse further — dataset artifact or model prior? (see Empirical Finding 7)
