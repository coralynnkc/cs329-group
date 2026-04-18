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
| Agency-based NER (Narnia) | `narnia/` | **primary** — custom schema; no supervised baseline possible | ✓ | — | **done** — zero-shot + few-shot scored for 3/4 models |
| Presuppositions (XNLI) | `srijon-2.0/presuppositions/` | ✓ | ✓ | **primary** — 6 languages; prompt-framing effect on class boundaries | mostly done — sonnet P0/P1 + chatgpt P0/P2/P4 |
| Fancy coreference (character-name clusters) | `coref/` | **primary** — hybrid NER + coref; no fixed-schema baseline | ✓ | — | **planned** — zero-shot + few-shot |

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
| Agency-based NER (Narnia) — zero-shot | `narnia/` | Chat 5.4, Gemini 3, Sonnet 4.6, Opus 4.6 | no supervised baseline (novel schema) | opus F1 0.78; chatgpt F1 0.59; sonnet F1 0.74; gemini F1 0.57 (zero-shot) |
| Agency-based NER (Narnia) — few-shot | `narnia/` | Chat 5.4, Sonnet 4.6, Opus 4.6 (gemini pending) | — | sonnet F1 **0.82**; opus F1 0.81; chatgpt F1 0.80 — few-shot gives +5–23 pp gain |

#### Multilingual pronoun resolution — full results (srijon-2.0)

| Language | Sonnet 4.6 acc (P0→P4) | GPT 5.4 acc (P0→P4) |
|----------|------------------------|----------------------|
| English  | 89% (stable P0–P4)     | 84–86%               |
| French   | 88–91%                 | 90–93%               |
| German   | 86–88%                 | 88–89%               |
| Russian  | 95–97%                 | 90–93%               |

Both models fully scored. Prompt engineering has marginal effect in English; larger effect in lower-resource settings.

### Presuppositions — scored results

Sonnet 4.6 P0/P1 and ChatGPT 5.4 P0/P2/P4 across 6 languages (DE, EN, FR, HI, RU, VI). Full analysis in `srijon-2.0/presuppositions/README.md`.

| Model | Prompt | DE | EN | FR | HI | RU | VI |
|-------|--------|----|----|----|----|----|----|
| Sonnet 4.6 | P0 | 0.82 | 0.59 | 0.88 | 0.86 | 0.88 | 0.88 |
| Sonnet 4.6 | P1 | 0.86 | 0.62 | 0.88 | 0.87 | 0.88 | 0.88 |
| ChatGPT 5.4 | P0 | 0.86 | 0.51 | 0.85 | 0.75 | 0.79 | 0.78 |
| ChatGPT 5.4 | P2 | 0.83 | 0.57 | 0.84 | 0.80 | 0.78 | 0.78 |
| ChatGPT 5.4 | P4 | 0.84 | 0.48 | 0.92 | 0.77 | 0.81 | 0.77 |

*(Macro-F1 scores. EN consistently lowest — Neutral class collapses in both models.)*

**What's still missing:**
- Sonnet P2/P4 (not yet run)
- ChatGPT/sonnet on HI/VI — only partial
- No Opus or Gemini runs yet

### Predictions done, scoring incomplete

| Task | What exists | What's missing |
|------|-------------|----------------|
| Grammaticality 2.0 (BLiMP) | `blimp_summary.csv` exists (headers-only) | No prediction files yet |
| Agency-based NER (Narnia) — Gemini few-shot | `narnia_predictions_gemini_fewshot.csv` (199 rows) | Not yet scored — run `python narnia/scripts/score_baseline.py --model gemini --prompt fewshot` |

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

8. **Few-shot gives large gains on agency-based NER (Narnia).** Sonnet: F1 0.74 → 0.82 (+8 pp); ChatGPT: F1 0.59 → 0.80 (+21 pp); Opus: F1 0.78 → 0.81 (+3 pp). The largest gain is for the weakest zero-shot model (ChatGPT), suggesting few-shot examples mainly fix output-format failures rather than improving genuine label understanding.

9. **Presupposition prompt framing changes class boundaries, not just accuracy.** Decision-first prompts (P2/P4) improve E/N boundary but often shift C predictions into N. P0 (probability-first) is a weaker but more consistent baseline. No single prompt dominates all languages — French is easiest/most stable; English is hardest regardless of prompt.

---

## What we have left to do

### 1. Finish presuppositions

Results exist for sonnet P0/P1 and chatgpt P0/P2/P4 across 6 languages. What remains:
- Run **sonnet P2 and P4** across all 6 languages (strongest prompt-comparison story requires all prompts on both models)
- Score **Gemini** on at least P0 + P4 (one additional model for robustness)
- Write a 1-page qualitative analysis: which languages / prompt pairs fail on the E/N boundary? Use centroid to explain *why* — does the model confuse plausibility with entailment, or contradiction with neutral?
- **Key claim to make:** prompt decision-framing changes class geometry in probability space, not just accuracy; this holds cross-linguistically except English (where neutral collapses persist regardless of prompt)

### 2. Fancy coreference — "character cluster" NER

**What it is:** For each sentence, identify all ways a character is referenced — proper names, pronouns, epithets ("the Lion", "the Great King") — and group them under a canonical character label. This is a hybrid of NER (find the spans) and coreference resolution (cluster them by identity).

**Why it's interesting:** Standard NER labels span type (PER/LOC/ORG). Standard coref clusters spans by identity. Neither task alone gives you *character-centric* annotation where every mention of Aslan maps to `ASLAN`, including indirect ones. LLMs can do this zero-shot; supervised pipelines require a two-stage pipeline that was never trained for this formulation.

**Plan:**
- Zero-shot: prompt the model to return `{character_name: [list of spans]}` for each sentence
- Few-shot: 2–3 examples showing name + pronoun + epithet clustering
- Metrics: use existing `coref/` infrastructure (MUC, B³, CEAFₑ, CoNLL F1) — this gives "fancy" validation
- Data: same 199-sentence Narnia mini eval set; gold clusters derivable from existing `narnia_answers.csv` annotations

### 3. Narnia corpus — linguistic insight generation (token-efficient)

**Goal:** Run agency-based NER + character clustering on the *full* Narnia corpus (`narnia.txt`) to generate insights like "Aslan is active in 73% of his appearances" or "Edmund is mostly passive in Book 1, active in Book 2."

**How to do it without killing tokens:**

1. **Pre-split the corpus.** Chunk `narnia.txt` into batches of ~20–30 sentences. Do this locally in a script — no model call needed.

2. **Batch, don't loop.** Send each batch as a single prompt asking the model to process all sentences and return a JSON array. Never call the model once per sentence.
   ```
   "Below are 25 sentences from Narnia. For each sentence_id, return: {sentence_id, entities: [{span, character, role}]}"
   ```

3. **Use a cheap model for bulk annotation.** Haiku 4.5 is ~20× cheaper than Opus. Run the full corpus through Haiku first; only re-run flagged/uncertain sentences with Sonnet.

4. **Save incrementally.** Write results to `narnia_full_results.jsonl` after each batch — one JSON object per line — so a crash doesn't lose everything.

5. **Estimate token cost before running.** `narnia.txt` is ~X words. At ~750 words/1k tokens, with ~150-token prompt overhead per batch of 25 sentences, the full corpus is roughly Y batches × Z tokens = W total. Run a cost estimate script before committing.
   ```python
   # rough_cost.py
   import tiktoken, math
   with open("narnia/narnia.txt") as f: text = f.read()
   words = len(text.split())
   batches = math.ceil(words / (25 * 20))  # ~20 words/sentence
   tokens_per_batch = 600  # prompt + 25 sentences + output
   print(f"{batches} batches × {tokens_per_batch} tokens ≈ {batches*tokens_per_batch/1000:.1f}k tokens")
   ```

6. **Aggregate with pandas.** Once all batches are saved, a simple groupby-character-role count gives the linguistic insight table — no model calls needed at aggregation time.

**Script to write:** `narnia/scripts/annotate_full_corpus.py` — takes `--model haiku|sonnet`, `--batch-size N`, `--output path`, `--dry-run` (estimates cost without calling the API).

### 4. Clustered coreference

**Goal:** Evaluate coreference resolution with proper cluster metrics (MUC, B³, CEAFₑ) rather than per-span F1. The `coref/` directory already has the infrastructure; it just needs harder test cases and real data.

**Plan:**
- Port the Narnia character-cluster annotations (from Task 2 above) into the coref evaluation format
- Run sonnet and chatgpt zero-shot and few-shot
- Report CoNLL F1 = average of MUC + B³ + CEAFₑ
- Compare against a supervised coref baseline (spaCy `en_core_web_trf` coref pipeline, or neuralcoref) — these will fail on Narnia epithets/nicknames, which proves the point

### 5. 10-minute demo outline

**Target audience:** CS329 class — knows NLP, may not know the full project.

**Structure:**

| Time | Segment | Content |
|------|---------|---------|
| 0:00–1:00 | Hook | One slide: "Can an LLM annotate any linguistic schema with no training?" — show a Narnia sentence annotated three ways: POS, NER, agency |
| 1:00–2:30 | Thesis + task map | Three claims (generality / no training / multilingual) → task × goal matrix, one sentence per task |
| 2:30–4:30 | Core results | Four tasks in 2 minutes: lemmatization = SOTA match; CoLA = beats human; NER = opus 0.95; Narnia agency = custom schema, no supervised baseline |
| 4:30–6:00 | Narnia deep dive | Show zero-shot vs. few-shot F1 bar chart; show a sentence where the model gets agency right (and one where it fails); linguistic insight teaser ("Aslan is active 73% of the time") |
| 6:00–7:30 | Multilingual story | Pronoun resolution: EN 87–91%, FR/DE/RU 86–97%, IG/ZU near chance — one chart; presuppositions: EN hardest, neutral collapse |
| 7:30–9:00 | Prompt engineering | One finding per task: "think like a linguist" hurts; few-shot fixes format failures; decision-framing changes class geometry |
| 9:00–10:00 | Conclusion + limitations | What we can claim; what we can't; where supervised still wins |

**Slides needed:** ~10–12 (one per segment, plus title/conclusion). Keep results as charts — avoid tables in the demo.

### 6. Complete baselining (lower priority)

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
Fancy coref (Narnia)      → "novel schema": character-cluster NER; hybrid of NER + coref; no supervised baseline
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
- [ ] Score Gemini few-shot Narnia predictions (file exists at `narnia/narnia_predictions_gemini_fewshot.csv`)
- [ ] Decide: run sonnet P2/P4 presuppositions, or call presuppositions done with current results?
- [ ] Write `narnia/scripts/annotate_full_corpus.py` — do a cost estimate before running on full corpus
- [ ] Gold character-cluster annotations for Narnia: derive from `narnia_answers.csv` or re-annotate?
