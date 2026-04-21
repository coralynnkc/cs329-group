# Grammatical Judgments — CoLA

Source: [The Corpus of Linguistic Acceptability (CoLA)](http://nyu-mll.github.io/cola) — 9,594 English sentences from linguistics publications, annotated for grammatical acceptability.

## Baseline Results — Acceptability Accuracy

| Model | Sample 1 | Sample 2 | Sample 3 | Mean |
| ------- | -------- | -------- | -------- | ------ |
| chatgpt | 0.48 | 0.4733 | 0.5067 | 0.4867 |
| gemini | 0.7 | 0.55 | 0.4933 | 0.5811 |
| sonnet | 0.8233 | 0.86 | 0.8467 | 0.8433 |
| opus | 0.8567 | 0.89 | 0.8933 | 0.88 |

*Run `python scripts/update_readme.py` after scoring to populate this table.*

---

## Files

### Data

| File | Rows | Description |
| --- | --- | --- |
| `in_domain_train.tsv` | 8,551 | Training set (17 sources) |
| `in_domain_dev.tsv` | 527 | In-domain dev set |
| `out_of_domain_dev.tsv` | 515 | Out-of-domain dev set (6 sources) |

Each file is tab-separated with 4 columns:

```
source_code  label  notation  sentence
```

- `source_code` — publication code (e.g. `gj04`, `ks08`)
- `label` — `1` = acceptable, `0` = unacceptable
- `notation` — original author notation (blank or `*`)
- `sentence` — the English sentence

**Example rows:**
```
c-05    1        The book was written by John.
c-05    0    *   Books were sent to each other by the students.
swb04   1        She voted for herself.
```

**Label distribution (train):** 6,023 acceptable (70%), 2,528 unacceptable (30%)

---

## Tasks

| Task | Input | Target |
| --- | --- | --- |
| Grammatical acceptability | sentence | `0` or `1` |

The challenge is distinguishing subtle grammatical violations (e.g. binding violations, island constraints, agreement errors) from well-formed sentences. Many unacceptable sentences are semantically plausible but syntactically ill-formed.

---

## Baselining

### Workflow

1. Generate mini CSVs (one-time):

   ```bash
   python scripts/make_mini.py
   ```

   Creates `mini/input.csv` (sentences) and `mini/answers.csv` (labels) — 3 samples × 300 = 900 rows each.

2. **Send one message** using the prompt below — paste the CSV content directly. Save the response as:

   ```
   mini/predictions_<model>.csv
   ```

3. Score:
   ```bash
   python scripts/score_baseline.py --model sonnet
   ```
   Repeat steps 2–3 for each model (e.g. `--model haiku`, `--model gpt4o`).

4. Update this README:
   ```bash
   python scripts/update_readme.py
   ```

Scores are saved to:

- `results/<model>_scores.csv` — per-sample breakdown
- `results/summary.csv` — all models side by side

---

## Prompt

Paste the contents of `mini/input.csv` directly after this message:

```
For each row, judge whether the English sentence is grammatically acceptable.
Return 1 for acceptable (well-formed), 0 for unacceptable (ill-formed).
Return ONLY a CSV with columns: sample_id,id,predicted_label. No explanation. Do not skip rows.

Examples:
- "The book was written by John." → 1
- "Books were sent to each other by the students." → 0
- "She voted for herself." → 1
- "In price soared oil." → 0

Data:
[paste contents of mini/input.csv here]
```
