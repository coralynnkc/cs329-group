# Working Document — LLMs for Linguistic Annotation
*Last updated: 2026-04-17*

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
| Lemmatization (args) | `lemmatization/` | ✓ | **primary** — matches SOTA | — | done |
| Grammaticality / CoLA binary | `grammatical/` | ✓ | **primary** — fills gap where tools are absent | — | done |
| POS tagging | `pos/` | ✓ | **primary** — competitive in-domain; OOD story pending | — | done (in-domain) |
| Grammaticality 2.0 (CoLA + BLiMP) | `grammaticality-2.0/` | ✓ | **primary** — prompt design story; MCC/F1/BLiMP | — | Chat 5.4 CoLA fully scored (all prompts × both splits); BLiMP pending |
| Pronoun resolution (EN/AM/IG/ZU) | `pronoun_resolution/testing/` | ✓ | ✓ | **primary** — EN/AM/IG/ZU; low-resource degradation | mostly done |
| Pronoun resolution (EN/DE/FR/RU) | `srijon-2.0/pronoun_resolution/` | ✓ | ✓ | **primary** — P0–P4 fully scored for both models | **done** |
| NER | `ner/` | **primary** — novel schemas supervised models can't handle | ✓ | — | **done** — all 4 models fully scored (CoNLL-2003) |
| Presuppositions | `srijon-2.0/presuppositions/` | ✓ | ✓ | **secondary** — EN/DE/FR/HI/RU/VI | sonnet P0–P1 all 6 langs; chat 5.4 P0 all 6 langs + P2–P3 DE/EN/FR done |
| Coreference | `coref/` | ✓ | — | — | deprioritized |
| Lemmatization segmentation | `lemmatization/` | ✓ | ✓ | — | partial — no predictions yet |

**Key:** ✓ = task supports this goal; **primary** = task is the main evidence for this goal; — = not applicable or not a focus.

---

## What we have

### Fully scored (results in hand)

| Task | Module | Models scored | SOTA comparison | Key result |
|------|--------|---------------|-----------------|------------|
| Lemmatization (args) | `lemmatization/` | chatgpt, gemini, sonnet, opus | spaCy/stanza ~95–99% | sonnet/opus match SOTA (~96–97%) |
| Grammaticality / CoLA binary | `grammatical/` | chatgpt, gemini, sonnet, opus | human ~80% | sonnet 84%, opus 88%; chatgpt ~49% |
| POS tagging (in-domain) | `pos/` | chatgpt, gemini, sonnet, opus | spaCy/udpipe ~97–98% | opus 94%; sonnet 85%; chatgpt 81% |
| Pronoun resolution (EN/AM/IG/ZU) — P0–P4 | `pronoun_resolution/testing/` | sonnet (full EN/AM, partial IG/ZU); chatgpt P0 only; opus P0 EN only | chance = 50% | EN: 87% (P0) → 91% (P1); IG/ZU near chance |
| Pronoun resolution (EN/DE/FR/RU) — P0–P4 | `srijon-2.0/pronoun_resolution/` | sonnet 4.6 (full), GPT 5.4 (full) | chance = 50% | see table below |
| Grammaticality 2.0 (CoLA) | `grammaticality-2.0/` | Chat 5.4 | — | direct/anchor/repair ~88–89% acc, MCC 0.73–0.75 in-domain; checklist collapses in-domain but recovers OOD (90% acc, MCC 0.76) |
| NER (CoNLL-2003) | `ner/` | chatgpt, gemini, sonnet, opus | spaCy/stanza F1 ~91% | opus 0.95; gemini 0.93; sonnet 0.92; chatgpt 0.26 (failure — see note below) |
| Presuppositions (EN/DE/FR/HI/RU/VI) | `srijon-2.0/presuppositions/` | sonnet 4.6 (P0–P1, all 6 langs); chat 5.4 (P0 all 6, P2–P3 DE/EN/FR) | — | sonnet: DE/FR/HI/RU/VI all 83–88% acc (macro-F1 0.82–0.88); EN anomalously low (68–70% acc) due to neutral-class collapse; chat 5.4 similar EN failure (56–61% acc) |

#### Multilingual pronoun resolution — full results (srijon-2.0)

| Language | Sonnet 4.6 acc (P0→P4) | GPT 5.4 acc (P0→P4) |
|----------|------------------------|----------------------|
| English  | 89% (stable P0–P4)     | 84–86%               |
| French   | 88–91%                 | 90–93%               |
| German   | 86–88%                 | 88–89%               |
| Russian  | 95–97%                 | 90–93%               |

Both models fully scored. Prompt engineering has marginal effect in English; larger effect in lower-resource settings (see Empirical Findings below).

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
| Lemmatization segmentation | mini CSVs exist, zero prediction files (`seg_predictions_*.csv`) |

### Not started

- POS out-of-domain evaluation (the key argument: SOTA drops 4–5% OOD; LLMs may hold)
- Grammaticality on non-English benchmarks
- NER few-shot and novel-schema experiments
- BLiMP pairwise predictions for any model

---

## Empirical findings so far

From `heuristics.md` (consolidated lessons from running experiments):

1. **Chunking matters a lot.** Performance throttling from too-large chunks is hard to detect. Include refusal as an option rather than forcing a label. Use task-specific validation to distinguish difficulty from chunking artifacts.

2. **"Think like a linguist" prompts are counterproductive.** Providing explicit linguistic heuristics or telling models to reason linguistically tends to hurt, not help. Hypothesis: LLMs find more complex patterns than we can outline in a brief prompt; explicit framing interferes with that.

3. **Prompt engineering has weaker effect than expected for well-understood tasks.** For English grammaticality, pronoun resolution, etc., a minimal, clear prompt usually outperforms elaborate prompt scaffolding.

4. **The prompt effect is not uniform across languages.** In English, both models are already strong, so prompt changes shift scores marginally. In lower-resource settings (especially Igbo and Zulu in the African WinoGrande experiments), prompt wording matters more — models appear to operate closer to their uncertainty boundary, making small prompt changes move Macro-F1 more dramatically.

5. **Training data matters more than architecture** (per recent literature; see `cora-notes/training_data_vs_architecture_papers.docx`).

6. **ChatGPT NER failure is qualitatively distinct from other models.** ChatGPT scored F1 0.26 vs. 0.92–0.95 for all other models. Inspection of `ner/mini/ner_predictions_chatgpt.csv` reveals three failure modes: (a) massive overclassification — pronouns ("We", "He", "It"), common words ("But", "Previously", "Results"), and temporal expressions ("Saturday", "Friday", "August") are all labeled as entities; (b) near-universal PER collapse — locations like "Jamaica", "Poland", "Germany" are labeled PER instead of LOC; (c) full headlines treated as single LOC entities (e.g., "SOCCER -- BELARUS BEAT ESTONIA IN WORLD CUP QUALIFIER" → one LOC span). This yields ~180 false positives per 100-sentence sample. The failure likely reflects the version of ChatGPT used producing a non-conforming output format or simply not following the structured annotation instructions; other models in the same family (GPT 5.4 in pronoun/grammaticality experiments) perform normally.

7. **Presuppositions: "Neutral" (N) label collapses for English in both models.** Sonnet and chat 5.4 both score EN presuppositions ~10–20 pp below all other languages. Inspection of class-level recall shows neutral (N) recall near 0.06–0.12 for EN vs. 0.60–0.73 for other languages — the model consistently misclassifies N as E (entailment). Entailment and contradiction are handled well (recall ~1.0). This is likely a dataset artifact: the English XNLI examples may have subtler neutrals than the translated versions, or the model's English NLI priors are over-confident on entailment.

---

## What we have left to do

### 1. Complete baselining

**Grammaticality 2.0 BLiMP** — run pairwise predictions for at least sonnet and GPT 5.4.

**Pronoun resolution (EN/AM/IG/ZU) gaps** — run missing cells:
- Sonnet: IG P2–P4, ZU P2–P4
- ChatGPT: all languages P1–P4
- Opus: AM/IG/ZU P0 at minimum

**Lemmatization segmentation** — send `seg_input.csv` to each model, save `seg_predictions_<model>.csv`, run `python lemmatization/scripts/score_baseline.py --model <model>`

**POS out-of-domain** — run existing models on an out-of-domain source. This is the clearest head-to-head: SOTA degrades ~4–5% OOD; LLM should hold or degrade less.

### 3. NER — generality proof of concept

The argument: supervised NER is trained on fixed schemas (PER, LOC, ORG) and cannot adapt when the label set changes. LLMs handle novel, theory-driven annotation schemes without retraining. Our demo is **agency-based NER in narrative texts** — a custom schema that no supervised model has been trained on.

**Task:** Given sentences from *The Chronicles of Narnia*, classify each named entity by its agentive role:
- **Active entity** — drives the event (e.g., "Lucy opened the wardrobe.")
- **Passive entity** — acted upon (e.g., "Edmund was captured by the Witch.")
- **Mentioned indirectly** — referenced without participation (e.g., "They spoke of Aslan in hushed tones.")

This operationalizes linguistic agency (thematic roles, transitivity, voice) as an NER-style annotation task — something no fixed-schema supervised model can do without retraining on a new label set.

**Why this proves generality:** The schema is custom and theory-driven. Supervised models trained on CoNLL or OntoNotes cannot perform this task at all. LLMs handle it via prompting alone, demonstrating that the same interface generalizes to arbitrary user-defined annotation schemes.

**Experimental design:**
1. Zero-shot: provide entity role definitions, return tagged spans
2. Few-shot (2–4 examples per type): test in-context learning sensitivity
3. Comparison baseline: standard NER tools (spaCy, stanza) applied to the same text — they extract entities but cannot assign agency labels

**Eval metrics:** F1 with strict span match; also relaxed (type-only) match. Report per-entity-type breakdown.

**Prompting techniques to test (from `cora-notes/prompting_notes_0416_revised.pdf`):**
- Text-to-text with special tokens: `[ENTITY]...[/ENTITY]` inline markup
- Chain-of-thought: reason first, then produce entity list
- Code-based extraction: ask model to output a Python dict / dataclass

### 4. Prompt engineering — qualitative analysis

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
NER                   → "generality": agency-based custom schema in narratives, supervised models can't adapt without retraining
```

The through-line for the paper: each task is chosen to illustrate a different failure mode of existing supervised pipelines. LLMs via prompting address all of them from a single interface.

---

## Deprioritized

- **Presupposition** — sparse literature (~20 papers), risky positioning. Sonnet P0–P1 all 6 languages + chat 5.4 P0–P3 for DE/EN/FR now done; only pursue further if another task is dropped
- **Coreference** — requires training to be competitive; deprioritize
- **Lemmatization segmentation** — worth running for completeness but not a primary contribution

---

## Open decisions

- [x] ~~Confirm NER datasets~~ — using CoNLL-2003 (`eng.testa`) for standard baseline; novel-schema (agency) experiment still pending
- [x] ~~Confirm which models to run NER on~~ — all 4 models scored (chatgpt, gemini, sonnet, opus)
- [ ] Decide whether to rerun NER with ChatGPT using a corrected prompt (current results are anomalous — see Empirical Finding 6)
- [ ] Decide strict vs. relaxed span match for NER novel-schema experiment and document rationale
- [ ] Decide whether to include gradient grammaticality judgments (Pearson/Spearman with BLiMP) or keep binary-only
- [ ] Decide whether to run Sonnet on grammaticality-2.0 CoLA (currently only GPT 5.4 predictions exist)
- [ ] Decide whether to include srijon-2.0 presuppositions in the paper or keep as supplemental
- [ ] Investigate EN presuppositions neutral-class collapse further — dataset artifact or model prior? (see Empirical Finding 7)
