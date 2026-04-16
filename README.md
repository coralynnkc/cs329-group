# Working Document — LLMs for Linguistic Annotation
*Last updated: 2026-04-16*

---

## Thesis

LLMs can serve as general-purpose linguistic annotation tools using prompt engineering alone — no fine-tuning, no labeled training data, no task-specific pipelines. We demonstrate this across multiple tasks, with particular attention to where supervised models *can't* generalize (new label schemas, low-resource languages, out-of-domain data).

Three claims, in order of how well we can currently defend them:

1. **Generality** — one approach works across structurally different tasks (POS, lemmatization, grammaticality, NER)
2. **No training needed** — prompting alone matches or approaches SOTA on several tasks, especially where SOTA degrades out-of-domain
3. **Multilingual** — LLMs generalize to low-resource languages where dedicated tools are sparse or absent

---

## What we have

### Fully baselined (results in hand, 4 models)

| Task | Module | Models scored | SOTA comparison | Status |
|------|--------|---------------|-----------------|--------|
| Lemmatization (args) | `lemmatization/` | chatgpt, gemini, sonnet, opus | spaCy/stanza ~95–99% | **done** — sonnet/opus match SOTA |
| Grammaticality / CoLA binary | `grammatical/` | chatgpt, gemini, sonnet, opus | human ~80%; LLMs 58–86% | **done** |
| POS tagging (in-domain) | `pos/` | chatgpt, gemini, sonnet, opus | spaCy/udpipe ~97–98%; LLMs 85–94% | **done** |
| Pronoun resolution (EN, AM, IG, ZU) — P0–P4 | `pronoun_resolution/testing/` | sonnet (full P0–P4 EN/AM, partial IG/ZU); ChatGPT (partial); Opus (partial) | WinoGrande chance = 50% | **mostly done**, gaps below |

### Partially done

| Task | Gap |
|------|-----|
| Pronoun resolution — Igbo | P2–P4 missing for sonnet; ChatGPT only P0 |
| Pronoun resolution — Zulu | P2–P4 missing for sonnet; ChatGPT only P0 |
| Pronoun resolution — Opus | only P0 for EN; nothing for AM/IG/ZU |
| Lemmatization segmentation | mini CSVs exist, zero prediction files (`seg_predictions_*.csv`) |
| grammaticality-2.0 (CoLA + BLiMP) | mini CSVs exist, `cola_summary.csv` is empty — no predictions run yet |

### Not started

- **NER** — no directory, no data, no scripts
- POS out-of-domain evaluation (the key argument: SOTA drops 4–5%, LLMs may hold)
- Grammaticality on non-English benchmarks

---

## What we have left to do

### 1. Complete baselining

**Pronoun resolution gaps** — run and score missing cells:
- Sonnet: IG P2–P4, ZU P2–P4
- ChatGPT: all languages P1–P4 (only P0 done)
- Opus: AM/IG/ZU P0 at minimum

**Lemmatization segmentation** — send `seg_input.csv` to each model, save `seg_predictions_<model>.csv`, run `python lemmatization/scripts/score_baseline.py --model <model>`

**grammaticality-2.0** — this is the strongest prompting story for grammaticality (MCC, F1 breakdown, prompt variants). Run at least:
- Sonnet × {direct, checklist, repair, fewshot} on `in_domain_dev` and `out_of_domain_dev`
- Opus × {direct, checklist} for comparison
- Use `grammaticality-2.0/prompts/cola_*.txt` prompt files; save predictions as `mini/predictions_<model>_<prompt>_<split>.csv`; score with `python grammaticality-2.0/scripts/score_cola.py --model sonnet --prompt direct --split in_domain_dev`

**POS out-of-domain** — run the existing models on `pos/en_ewt-ud-dev.conllu` or an out-of-domain source. This is the clearest head-to-head: SOTA degrades ~4–5% OOD; LLM should hold or degrade less.

### 2. NER — generality proof of concept

The argument: supervised NER (PubMedBERT, BioBERT) is trained on fixed schemas and fails when label types change. LLMs handle novel/unseen entity types without retraining.

**Recommended setup:**

| Domain | Dataset | Gold standard | Why |
|--------|---------|---------------|-----|
| News (standard) | CoNLL-2003 | 92–95% F1 (fine-tuned BERT) | establishes baseline gap |
| Biomedical | BC5CDR or NCBI-Disease | PubMedBERT ceiling | cross-domain generality |

**Experimental design:**
1. Zero-shot: give model entity types + definitions, return tagged spans
2. Few-shot (2–4 examples per type): test in-context learning sensitivity
3. Novel schema: define 1–2 entity types not in any training corpus (e.g. linguistic phenomena, historical entities) — this is where LLMs win and supervised models can't compete

**Eval metrics:** F1 with strict span match; also relaxed (type-only) match. Report per-entity-type breakdown.

**Prompting techniques to test (from `cora-notes/prompting_notes_0416_revised.pdf`):**
- Text-to-text with special tokens: `[ENTITY]...[/ENTITY]` inline markup
- Chain-of-thought: reason first, then produce entity list
- Code-based extraction: ask model to output a Python dict / dataclass

**Recommended datasets to download:**
- CoNLL-2003: available via HuggingFace `datasets` (`conll2003`)
- BC5CDR: `bigbio/bc5cdr` on HuggingFace
- NCBI-Disease: `ncbi_disease` on HuggingFace

### 3. Prompt engineering — qualitative analysis

Goal: don't just show accuracy numbers; show *which constructions* improve with better prompts and explain why.

**Grammaticality:**
- BLiMP gives per-construction-type breakdowns (subject-verb agreement, island constraints, binding, etc.)
- Document where MCC improves from direct → checklist → repair prompt
- Expected finding from literature: better on agreement/word order violations; worse on island constraints and center embedding

**Pronoun resolution:**
- P0 vs. P1 (two-shot) comparison already in hand for EN: 87% → 91%
- Igbo/Zulu near-chance even with few-shot — worth documenting as the multilingual failure mode
- Run P2–P4 for the remaining languages to complete the prompt × language matrix

**NER:**
- Position bias and overclassification are the known failure modes — document their frequency per prompt type

---

## Argument structure (how results tie together)

```
Lemmatization         → "solved" anchor: prompting = SOTA, no training needed
Grammaticality        → "no tool exists": LLMs fill a gap, prompt design matters
POS tagging           → "LLMs competitive OOD where SOTA degrades"
Pronoun resolution    → "multilingual": English strong, low-resource languages degrade gracefully
NER                   → "generality": novel schemas, LLMs win where supervised can't adapt
```

The through-line for the paper: each task is chosen to illustrate a different failure mode of existing supervised pipelines. LLMs via prompting address all of them from a single interface.

---

## Deprioritized

- **Presupposition** — sparse literature (~20 papers), risky positioning, only pursue if another task is dropped
- **Coreference** — requires training to be competitive; deprioritize
- **Lemmatization segmentation** — worth running for completeness but not a primary contribution

---

## Open decisions

- [ ] Confirm NER datasets (CoNLL-2003 + one biomedical source is the minimum)
- [ ] Decide strict vs. relaxed span match for NER and document rationale
- [ ] Decide whether to include gradient grammaticality judgments (Pearson/Spearman with BLiMP) or keep binary-only
- [ ] Confirm which models to run NER on (at minimum: sonnet, opus, one GPT variant for cross-family comparison)
