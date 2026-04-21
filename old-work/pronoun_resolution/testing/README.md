# Pronoun Resolution — Prompt Testing

This directory contains the canonical datasets, generated artifacts, and scripts
for multilingual pronoun-resolution prompt-engineering experiments.

---

## Directory Layout

```
testing/
  en/                        # English
    source/                  # canonical split files (authoritative)
    inference/               # LLM upload files (generated)
    full/                    # scoring files (generated)
    results/                 # model outputs + scorer outputs
  am/                        # Amharic (same sub-structure)
  ig/                        # Igbo    (same sub-structure)
  zu/                        # Zulu    (same sub-structure)
  prompts/                   # markdown prompt templates (P0–P4)
  scripts/                   # generation + split scripts
  splits/                    # LEGACY — original split outputs (do not edit)
```

---

## What belongs where

| Folder | Contents | Authoritative? |
|--------|----------|----------------|
| `{lang}/source/` | Canonical split CSVs with all columns (gold labels, difficulty, metadata). **Edit here, not in generated files.** | YES |
| `{lang}/inference/` | 4-column CSVs for LLM upload: `item_id`, `sentence`, `option_a`, `option_b` | No — generated artifact |
| `{lang}/full/` | All-column CSVs for scoring and auditing | No — generated artifact |
| `{lang}/results/` | Model predictions (from batch CSV out) and scorer outputs | Experiment outputs |
| `prompts/` | Prompt templates (P0–P4). Add your `.md` files here. | Manual |
| `scripts/` | Python scripts for split generation and artifact regeneration | Versioned code |

---

## Source files are canonical

The files in `{lang}/source/` are the **single source of truth** for each split.
Do not edit inference/ or full/ files directly — they are regenerated from source/.

If you need to fix a label or sentence, edit the source file and then rerun:

```bash
python testing/scripts/generate_inference_full.py
```

---

## Splits

Each language has these splits:

| Split | Purpose | Scored? |
|-------|---------|---------|
| `{lang}_fewshot_bank.csv` | Exemplars for prompt construction | Never scored |
| `{lang}_dev.csv` | Primary eval set — use during prompt development | Yes |
| `{lang}_challenge.csv` | Hard stress-test subset (highest difficulty) | Yes |
| `{lang}_holdout.csv` | Reserved — do not use until final prompt selection | Yes |

No `test` split exists yet. The holdout set serves as the final held-out
evaluation after a prompt condition has been selected.

---

## Column schema

All source files use this core schema:

| Column | Description |
|--------|-------------|
| `item_id` | Stable identifier (matches across languages by item number) |
| `sentence` | Sentence with `_` as the blank to fill |
| `option_a` | First candidate (letter A) |
| `option_b` | Second candidate (letter B) |
| `gold_answer` | Correct answer: `A` or `B` |
| `correct_answer_num` | Numeric form of correct answer (1 or 2) |
| `correct_text` | Text of the correct answer |

English files additionally include difficulty metadata:

| Column | Description |
|--------|-------------|
| `row_index` | 0-based row index in the original master file |
| `source_file` | Source CSV filename |
| `feat_token_len` | Token count of the sentence |
| `feat_clause_markers` | Count of clause-boundary punctuation |
| `feat_blank_distance` | Mean token distance from `_` to each candidate |
| `difficulty_score` | Composite difficulty proxy (0–1, higher = harder) |

---

## Batch workflow

For each prompt condition (P0–P4):

1. **Upload** `{lang}/inference/{lang}_{split}_inference.csv` to the model batch interface.
2. **Run** one prompt template from `prompts/`.
3. **Save** the model's predictions to `{lang}/results/`.
4. **Score** by joining predictions against `{lang}/full/{lang}_{split}_full.csv`
   on `item_id`.

---

## Prompt conditions

| ID | Name | Notes |
|----|------|-------|
| P0 | Base zero-shot | No examples, no task framing |
| P1 | Two-shot | Two fewshot examples from fewshot bank |
| P2 | Four-shot | Four fewshot examples from fewshot bank |
| P3 | Decomposed candidate tracking | Step-by-step reasoning |
| P4 | Expanded definition | Expanded task description |

Prompt templates live in `prompts/`. Add your `.md` files there manually.

---

## Regenerating inference and full files

```bash
# From anywhere in the repo:
python pronoun_resolution/testing/scripts/generate_inference_full.py

# Or from inside testing/:
python scripts/generate_inference_full.py
```

The script validates that all required columns exist and prints a manifest
of every file written. It is safe to rerun — overwrites existing files.

---

## Regenerating splits from scratch

The split generation script produces the source split CSVs from
the English master file and propagates indices to the multilingual files.

```bash
python pronoun_resolution/testing/scripts/generate_splits.py
python pronoun_resolution/testing/scripts/generate_inference_full.py
```

See the docstring in `scripts/generate_splits.py` for all options (seed,
dev size, challenge size, fewshot bank size).

---

## Legacy folder

`splits/` contains the original pre-restructure split outputs.
It is kept for reference but **should not be edited**.
Once you have verified the new layout is correct, it can be deleted.
