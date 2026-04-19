# Working Document — LLMs for Linguistic Annotation

_Last updated: 2026-04-19_

---

## Thesis

LLMs can serve as general-purpose linguistic annotation tools using prompt engineering alone — no fine-tuning, no labeled training data, no task-specific pipelines. We demonstrate this across multiple tasks, with particular attention to where supervised models _can't_ generalize (new label schemas, low-resource languages, out-of-domain data).

Three claims, in order of how well we can currently defend them:

1. **Generality** — one approach works across structurally different tasks (POS, lemmatization, grammaticality, NER)
2. **No training needed** — prompting alone matches or approaches SOTA on several tasks, especially where SOTA degrades out-of-domain
3. **Multilingual** — LLMs generalize to low-resource languages where dedicated tools are sparse or absent

---

## Task × Goal Matrix

Each task is selected to illustrate a specific failure mode of existing supervised pipelines. This table maps every module to the project claims it supports.

| Task                                           | Module                                       |                          Generality                          |                   No Training Needed                   |                             Multilingual                             | Status                                                       |
| ---------------------------------------------- | -------------------------------------------- | :----------------------------------------------------------: | :----------------------------------------------------: | :------------------------------------------------------------------: | ------------------------------------------------------------ |
| Lemmatization                                  | `lemmatization/`                             |                              ✓                               |               **primary** — matches SOTA               |                                  —                                   | done                                                         |
| Grammaticality / CoLA binary                   | `grammatical/`                               |                              ✓                               |     **primary** — fills gap where tools are absent     |                                  —                                   | done                                                         |
| POS tagging                                    | `pos/`                                       |                              ✓                               | **primary** — competitive in-domain; OOD story pending |                                  —                                   | done (in-domain)                                             |
| Grammaticality 2.0 (CoLA + BLiMP)              | `grammaticality-2.0/`                        |                              ✓                               |    **primary** — prompt design story; MCC/F1/BLiMP     |                                  —                                   | CoLA fully scored (all prompts × both splits); BLiMP pending |
| Pronoun resolution (EN/AM/IG/ZU + EN/DE/FR/RU) | `pronoun_resolution/testing/`, `srijon-2.0/` |                              ✓                               |                           ✓                            |         **primary** — 7 languages; low-resource degradation          | mostly done                                                  |
| NER                                            | `ner/`                                       |  **primary** — novel schemas supervised models can't handle  |                           ✓                            |                                  —                                   | **done** — all 4 models fully scored (CoNLL-2003)            |
| Agency-based NER (Narnia)                      | `narnia/`                                    | **primary** — custom schema; no supervised baseline possible |                           ✓                            |                                  —                                   | **done** — zero-shot + few-shot scored for all 4 models      |
| Presuppositions (XNLI)                         | `srijon-2.0/presuppositions/`                |                              ✓                               |                           ✓                            | **primary** — 6 languages; prompt-framing effect on class boundaries | mostly done — sonnet P0/P1 + chatgpt P0/P2/P4                |
| Fancy coreference (character-name clusters)    | `coref/`                                     |  **primary** — hybrid NER + coref; no fixed-schema baseline  |                           ✓                            |                                  —                                   | **done** — zero-shot + few-shot scored (opus/sonnet/chatgpt) |

**Key:** ✓ = task supports this goal; **primary** = task is the main evidence for this goal; — = not applicable or not a focus.

---

## What we have

### Fully scored (results in hand)

| Task                                                           | Module                                       | Models scored                                                   | SOTA comparison                       | Key result                                                                                                                    |
| -------------------------------------------------------------- | -------------------------------------------- | --------------------------------------------------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Lemmatization                                                  | `lemmatization/`                             | Chat 5.4, Gemini 3, Sonnet 4.6, Opus 4.6                        | spaCy/stanza ~95–99%                  | sonnet/opus match SOTA (~96–97%)                                                                                              |
| Grammaticality / CoLA binary                                   | `grammatical/`                               | Chat 5.4, Gemini 3, Sonnet 4.6, Opus 4.6                        | human ~80%                            | sonnet 84%, opus 88%; chatgpt ~49%                                                                                            |
| POS tagging (in-domain)                                        | `pos/`                                       | Chat 5.4, Gemini 3, Sonnet 4.6, Opus 4.6                        | spaCy/udpipe ~97–98%                  | opus 94%; sonnet 85%; chatgpt 81%                                                                                             |
| Grammaticality 2.0 (CoLA)                                      | `grammaticality-2.0/`                        | Chat 5.4                                                        | —                                     | direct/anchor/repair ~88–89% acc, MCC 0.73–0.75 in-domain; checklist collapses in-domain but recovers OOD (90% acc, MCC 0.76) |
| Pronoun resolution (EN/AM/IG/ZU + EN/DE/FR/RU)                 | `pronoun_resolution/testing/`, `srijon-2.0/` | sonnet 4.6 (7 langs), GPT 5.4 (full EN/DE/FR/RU); partial IG/ZU | chance = 50%                          | EN: 87–91%; FR/DE/RU: 86–97%; IG/ZU near chance; see table below                                                              |
| NER (CoNLL-2003)                                               | `ner/`                                       | Chat 5.4, Gemini 3, Sonnet 4.6, Opus 4.6                        | spaCy/stanza F1 ~91%                  | opus 0.95; gemini 0.93; sonnet 0.92; chatgpt 0.26 (failure — see note below)                                                  |
| Agency-based NER (Narnia) — zero-shot                          | `narnia/`                                    | Chat 5.4, Gemini 3, Sonnet 4.6, Opus 4.6                        | no supervised baseline (novel schema) | opus F1 0.78; chatgpt F1 0.59; sonnet F1 0.74; gemini F1 0.57 (zero-shot)                                                     |
| Agency-based NER (Narnia) — few-shot                           | `narnia/`                                    | Chat 5.4, Gemini 3, Sonnet 4.6, Opus 4.6                        | —                                     | sonnet F1 **0.82**; gemini F1 0.81; opus F1 0.81; chatgpt F1 0.80 — few-shot gives +5–23 pp gain                              |
| Fancy coreference / character-cluster NER (Narnia) — zero-shot | `coref/`                                     | Opus 4.6, Sonnet 4.6, Chat 5.4                                  | no supervised baseline (novel schema) | opus F1 **0.88**; sonnet F1 0.74; chatgpt F1 0.41 (same over-prediction failure as CoNLL NER)                                 |
| Fancy coreference / character-cluster NER (Narnia) — few-shot  | `coref/`                                     | Opus 4.6, Sonnet 4.6, Chat 5.4                                  | —                                     | opus F1 0.82; sonnet F1 0.80; chatgpt F1 0.55 — few-shot fixes epithet resolution for sonnet; chatgpt precision stays low     |

#### Multilingual pronoun resolution — full results (srijon-2.0)

| Language | Sonnet 4.6 acc (P0→P4) | GPT 5.4 acc (P0→P4) |
| -------- | ---------------------- | ------------------- |
| English  | 89% (stable P0–P4)     | 84–86%              |
| French   | 88–91%                 | 90–93%              |
| German   | 86–88%                 | 88–89%              |
| Russian  | 95–97%                 | 90–93%              |

Both models fully scored. Prompt engineering has marginal effect in English; larger effect in lower-resource settings.

### Presuppositions — scored results

Sonnet 4.6 P0/P1 and ChatGPT 5.4 P0/P2/P4 across 6 languages (DE, EN, FR, HI, RU, VI). Full analysis in `srijon-2.0/presuppositions/README.md`.

| Model       | Prompt | DE   | EN   | FR   | HI   | RU   | VI   |
| ----------- | ------ | ---- | ---- | ---- | ---- | ---- | ---- |
| Sonnet 4.6  | P0     | 0.82 | 0.59 | 0.88 | 0.86 | 0.88 | 0.88 |
| Sonnet 4.6  | P1     | 0.86 | 0.62 | 0.88 | 0.87 | 0.88 | 0.88 |
| ChatGPT 5.4 | P0     | 0.86 | 0.51 | 0.85 | 0.75 | 0.79 | 0.78 |
| ChatGPT 5.4 | P2     | 0.83 | 0.57 | 0.84 | 0.80 | 0.78 | 0.78 |
| ChatGPT 5.4 | P4     | 0.84 | 0.48 | 0.92 | 0.77 | 0.81 | 0.77 |

_(Macro-F1 scores. EN consistently lowest — Neutral class collapses in both models.)_

**What's still missing:**

- Sonnet P2/P4 (not yet run)
- ChatGPT/sonnet on HI/VI — only partial
- No Opus or Gemini runs yet

### Incomplete / not started

| Task | Gap |
| ---- | ---- |
| Grammaticality 2.0 (BLiMP) | no prediction files yet (`blimp_summary.csv` is headers-only) |
| Pronoun resolution — Igbo | sonnet P2–P4 missing; chatgpt only P0 |
| Pronoun resolution — Zulu | sonnet P2–P4 missing; chatgpt only P0 |
| Pronoun resolution — Opus | only P0 for EN; nothing for AM/IG/ZU |
| Challenge splits (all 7 languages) | splits generated, no predictions yet |
| POS out-of-domain | not started (key argument: SOTA drops 4–5% OOD; LLMs may hold) |
| BLiMP pairwise predictions | not started |

---

## Empirical findings so far

1. **Chunking matters a lot.** Performance throttling from too-large chunks is hard to detect. Include refusal as an option rather than forcing a label.

2. **"Think like a linguist" prompts are counterproductive.** Providing explicit linguistic heuristics tends to hurt, not help — LLMs likely find richer patterns than a brief prompt can outline.

3. **Prompt engineering has weaker effect than expected for well-understood tasks.** For English grammaticality and pronoun resolution, a minimal prompt usually outperforms elaborate scaffolding.

4. **The prompt effect is not uniform across languages.** In lower-resource settings (Igbo, Zulu), prompt wording matters more — models operate closer to their uncertainty boundary.

5. **Training data matters more than architecture** (per recent literature; see `cora-notes/training_data_vs_architecture_papers.docx`).

6. **ChatGPT NER failure is qualitatively distinct.** F1 0.26 vs. 0.92–0.95 for all other models. Failure modes: massive overclassification of common words/pronouns, near-universal PER collapse for locations, and full headlines treated as single LOC spans. Likely a prompt-conformance failure specific to that model version.

7. **Presuppositions: "Neutral" label collapses for English in both models.** EN scores ~10–20 pp below all other languages; neutral recall near 0.06–0.12 vs. 0.60–0.73 for other languages. Likely a dataset artifact — EN XNLI neutrals may be subtler than translated versions.

8. **Few-shot gives large gains on agency-based NER (Narnia).** Sonnet: F1 0.74 → 0.82 (+8 pp); ChatGPT: F1 0.59 → 0.80 (+21 pp); Opus: F1 0.78 → 0.81 (+3 pp). The largest gain is for the weakest zero-shot model (ChatGPT), suggesting few-shot examples mainly fix output-format failures rather than improving genuine label understanding.

9. **Epithet resolution is the hard part of character-cluster NER.** Opus handles "the Faun → Mr. Tumnus", "the White Witch → Jadis" reliably zero-shot (F1 0.88); sonnet fails on these (Jadis: F1 0.000 zero-shot) but few-shot examples fix it (Jadis: F1 0.800). ChatGPT's over-prediction failure persists zero-shot and few-shot — same qualitative failure as its CoNLL NER result.

10. **Presupposition prompt framing changes class boundaries, not just accuracy.** Decision-first prompts (P2/P4) improve E/N boundary but often shift C predictions into N. P0 (probability-first) is a weaker but more consistent baseline. No single prompt dominates all languages — French is easiest/most stable; English is hardest regardless of prompt.

---

## What we have left to do

### 1. Finish presuppositions

Results exist for sonnet P0/P1 and chatgpt P0/P2/P4 across 6 languages. What remains:

- Run **sonnet P2 and P4** across all 6 languages (strongest prompt-comparison story requires all prompts on both models)
- Score **Gemini** on at least P0 + P4 (one additional model for robustness)
- Write a 1-page qualitative analysis: which languages / prompt pairs fail on the E/N boundary? Use centroid to explain _why_ — does the model confuse plausibility with entailment, or contradiction with neutral?
- **Key claim to make:** prompt decision-framing changes class geometry in probability space, not just accuracy; this holds cross-linguistically except English (where neutral collapses persist regardless of prompt)

### 2. Narnia large — corpus-level annotation (WIP)

**Goal:** Run agency-based NER + character clustering on the full Narnia corpus to generate character-level agency statistics ("Aslan is active in 73% of his appearances"). See `narnia-large/` for current state.

**Script to write:** `narnia-large/scripts/annotate_corpus.py` — takes `--model`, `--chapter`, `--batch-size`, `--dry-run` (cost estimate before committing API spend). Do a cost estimate before running on the full corpus.

### 3. Complete baselining (lower priority)

**Grammaticality 2.0 BLiMP** — run pairwise predictions for at least sonnet and GPT 5.4.

**Pronoun resolution (EN/AM/IG/ZU) gaps** — run missing cells:

- Sonnet: IG P2–P4, ZU P2–P4
- ChatGPT: all languages P1–P4
- Opus: AM/IG/ZU P0 at minimum

**Challenge splits** — run at least sonnet and GPT 5.4 to test whether hard items drive the low-resource degradation story.

**POS out-of-domain** — run existing models on an out-of-domain source. SOTA degrades ~4–5% OOD; LLMs should hold or degrade less.

---

## Argument structure (how results tie together)

```
Lemmatization             → "solved" anchor: prompting = SOTA, no training needed
Grammaticality            → "no tool exists": LLMs fill a gap, prompt design matters
POS tagging               → "LLMs competitive OOD where SOTA degrades"
Pronoun resolution        → "multilingual": English strong, low-resource languages degrade gracefully
Presuppositions           → "multilingual + prompt framing": 6 languages; prompt structure changes class geometry; English hardest
NER (CoNLL-2003)          → "generality": strong baseline (opus F1 0.95); supervised schema
NER (Narnia / agency)     → "generality proof of concept": custom schema, no supervised baseline; few-shot sonnet F1 0.82
Fancy coref (Narnia)      → "novel schema": character-cluster NER; hybrid of NER + coref; no supervised baseline; opus F1 0.88; few-shot fixes epithet failures
Corpus-level insights     → "proof of concept → application": agency statistics over full Narnia corpus
```

The through-line for the paper: each task is chosen to illustrate a different failure mode of existing supervised pipelines. LLMs via prompting address all of them from a single interface.

---

## Deprioritized

- **Grammaticality on non-English benchmarks** — no clear dataset; skip
- **NER few-shot novel-schema experiments beyond Narnia** — Narnia already covers this story
- **Standard coreference on OntoNotes/PreCo** — requires fine-tuning to be competitive; the fancy character-cluster version (Task 4 above) is more interesting and more defensible

---

## Open decisions

- [ ] Is Claire running sonnet grammaticality 2.0?
- [ ] Investigate EN presuppositions neutral-class collapse further — dataset artifact or model prior? (see Empirical Finding 7)
- [ ] Decide: run sonnet P2/P4 presuppositions, or call presuppositions done with current results?
- [ ] Write `narnia-large/scripts/annotate_corpus.py` — takes `--model`, `--chapter`, `--batch-size`, `--dry-run`; do a cost estimate before running on full corpus
- [ ] Gold character-cluster annotations for Narnia: derive from `narnia_answers.csv` or re-annotate?
