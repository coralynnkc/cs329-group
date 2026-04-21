# srijon-2.0

A clean, evaluation-ready reorganization of the multilingual NLP benchmark data
originally in `/srijon/data/`. Nothing in `/srijon` was modified.

---

## What was imported

| Original file | Task | Language | Rows |
|---------------|------|----------|------|
| `Lemmas English.xlsx` | lemmatization | en | 115,523 |
| `Presuppositions English.xlsx` | presuppositions | en | 6,981 |
| `Presuppositions French.csv` | presuppositions | fr | 5,010 |
| `Presuppositions German.csv` | presuppositions | de | 5,010 |
| `Presuppositions Hindi.csv` | presuppositions | hi | 5,010 |
| `Presuppositions Russian.csv` | presuppositions | ru | 5,010 |
| `Presuppositions Vietnamese.csv` | presuppositions | vi | 5,010 |
| `Pronoun Resolution English.xlsx` | pronoun_resolution | en | 10,234 |
| `Pronoun Resolution French.xlsx` | pronoun_resolution | fr | 2,793 |
| `Pronoun Resolution German.xlsx` | pronoun_resolution | de | 5,835 |
| `Pronoun Resolution Russian.xlsx` | pronoun_resolution | ru | 1,487 |

**Total: 167,903 rows across 11 source files.**

---

## Directory layout

```
srijon-2.0/
├── pronoun_resolution/
│   ├── en/   fr/   de/   ru/
│   │   ├── source/      ← canonical CSV (item_id + all columns)
│   │   ├── inference/   ← model-facing CSV (item_id + minimal schema)
│   │   ├── full/        ← scorer CSV (source + empty prediction columns)
│   │   └── results/     ← placeholder for prediction outputs
├── presuppositions/
│   ├── en/   fr/   de/   hi/   ru/   vi/
│   │   └── (same source / inference / full / results layout)
├── lemmatization/
│   └── en/
│       └── (same layout)
├── prompts/
│   ├── pronoun_resolution/prompt_template.md
│   ├── presuppositions/prompt_template.md
│   └── lemmatization/prompt_template.md
├── scripts/
│   └── normalize.py      ← normalization pipeline (safe to re-run)
├── docs/
│   ├── assumptions.md    ← every non-obvious decision documented
│   ├── label_normalization.md
│   └── split_strategy.md
├── manifest.csv          ← per-file audit log
└── README.md             ← this file
```

---

## File naming convention

| Pattern | Meaning |
|---------|---------|
| `{lang}_master.csv` | Full dataset, canonical source |
| `{lang}_master_inference.csv` | Model-facing only (minimal columns) |
| `{lang}_master_full.csv` | Scorer-ready (source + empty prediction cols) |

All datasets are currently unsplit. See `docs/split_strategy.md` for the documented
plan (80/10/10 random, seed=42).

---

## Inference schemas (column layout per task)

### Pronoun Resolution — English
```
item_id | sentence
```
`sentence` contains `_` as a pronoun placeholder. No option columns (see `docs/assumptions.md` A2).

### Pronoun Resolution — French / German / Russian
```
item_id | sentence | option_a | option_b
```

### Presuppositions — all languages
```
item_id | premise | hypothesis
```

### Lemmatization — English
```
item_id | word
```

---

## What counts as canonical source data

Files in `source/` directories are the canonical inputs. They contain:
- `item_id` — stable deterministic identifier
- All original columns from the source file (encoding-repaired)
- No added labels, no filtering, no reordering

Files in `inference/` and `full/` are **generated artifacts** derived from source.

---

## How to regenerate inference / full files

```bash
# Run from repo root (cs329-group/)
python3 srijon-2.0/scripts/normalize.py
```

The script is idempotent and overwrites outputs deterministically. It requires
`pandas` and `openpyxl` (`pip install pandas openpyxl`).

---

## Typical LLM batch workflow

1. Pick a task and language, e.g. `presuppositions/fr/`.
2. Load `fr_master_inference.csv` — this is your model input file.
3. Use the prompt template from `prompts/presuppositions/prompt_template.md`.
4. For each row, format the prompt and collect the model's response.
5. Merge responses into a copy of `fr_master_full.csv` under `model_label`.
6. Join gold labels from XNLI (see `docs/label_normalization.md`).
7. Compute `correct = (model_label == gold_label)` and report accuracy.
8. Save scored output to `fr/results/fr_master_scored.csv`.

---

## Known limitations requiring manual action

| Issue | File(s) affected | Action needed |
|-------|-----------------|---------------|
| No gold labels | All `full/` files | Join from XNLI / WinoGrande / CONFER / UniMorph |
| No option_a/b | `pronoun_resolution/en/` | Re-join from WinoGrande source |
| No lemma gold | `lemmatization/en/` | Re-join from UniMorph corpus |
| No splits | All tasks | Run split script (see `docs/split_strategy.md`) |

---

## Related resources

- Original data and scripts: `/srijon/`
- Original evaluation notebooks: `/srijon/scripts/*.ipynb`
- Original task documentation: `/srijon/explanation.md`
- Manifest (file-level audit log): `srijon-2.0/manifest.csv`
- Task inventory (languages and schemas): `docs/task_inventory.md`
