# Batch-Size Experiment — Full Documentation

This document is the authoritative record for the English batch-size study
in `pronoun_resolution/en_testing_batch_size/`.  A reviewer should be able
to reproduce every step from this file alone.

---

## 1. Task Framing

### 1.1 What is being evaluated

This experiment evaluates **pronoun resolution framed as forced-choice
antecedent selection**, delivered in **batch form**.

Each item in the dataset contains:

- a sentence with a blank (`_`) where the pronoun has been replaced
- two candidate antecedents: `option_a` and `option_b`
- a gold answer (`A` or `B`) indicating which candidate fills the blank

The model receives a CSV file with many items and must return a corresponding
CSV of labels — one per row.

### 1.2 What this study is NOT

This is **not** 25/100/250/500 separate single-item queries.

Each condition is **one API call** with one attached CSV.  The experiment is
specifically about how the model handles a *batch* of items, not how it handles
items individually.

### 1.3 What changes between conditions

**Only the number of items** in the uploaded CSV changes.

The prompt text, the model, the temperature (default), and every other setting
remain fixed.  This isolates batch size as the sole independent variable.

---

## 2. Source Data and Normalization

### 2.1 Canonical English master file

```
pronoun_resolution/en_master.csv
```

- **826 items** total (as of this writing)
- **408 label-A items**, **418 label-B items**
- Source schema: `item_num, sentence, option1, option2, correct_answer_num,
  correct_letter, correct_text`

### 2.2 Normalization

The script `scripts/create_batch_size_subsets.py` normalizes the source to a
canonical schema:

| Canonical column     | Source column       | Notes                             |
|----------------------|---------------------|-----------------------------------|
| `item_id`            | `item_num`          | Unique integer string; preserved as-is |
| `sentence`           | `sentence`          | Whitespace-stripped               |
| `option_a`           | `option1`           | Whitespace-stripped               |
| `option_b`           | `option2`           | Whitespace-stripped               |
| `gold_answer`        | `correct_letter`    | Upper-cased to `A` or `B`         |
| `correct_answer_num` | `correct_answer_num`| Passthrough                       |
| `correct_text`       | `correct_text`      | Passthrough                       |
| `row_index`          | —                   | 0-based position in source file   |
| `source_file`        | —                   | Always `en_master.csv`            |

The full normalized master is saved to `data/english_master_normalized.csv`.

### 2.3 Assumptions

1. `item_num` is unique across all rows; no content-hash fallback is needed.
2. `correct_letter` contains only `A` or `B` (the script hard-fails otherwise).
3. `option1` corresponds to label `A`; `option2` to label `B`.
4. The file uses comma-separated UTF-8 encoding with a header row.

If any assumption fails, the script exits with a clear error message.

---

## 3. Nested Subset Design

### 3.1 Sizes

Four batch sizes are generated:

| Condition  | N items | Label A | Label B |
|------------|---------|---------|---------|
| batch_25   | 25      | 12      | 13      |
| batch_100  | 100     | 50      | 50      |
| batch_250  | 250     | 125     | 125     |
| batch_500  | 500     | 250     | 250     |

*Label counts are nominal; exact values are in `metadata/subset_summary.md`.*

### 3.2 Nesting guarantee

```
batch_25  ⊆  batch_100  ⊆  batch_250  ⊆  batch_500
```

Every item in batch_25 also appears in batch_100, batch_250, and batch_500.
This matters for comparability: any performance difference between conditions
cannot be due to different items.

### 3.3 How nesting is achieved

1. All label-A items are shuffled once with seed `329`.
2. All label-B items are shuffled once with seed `329`.
3. For the largest subset (batch_500): take the first 250 A items and first 250 B items.
4. For each smaller subset: take the first `floor(N/2)` A items and `ceil(N/2)` B
   items from the same shuffled pool — i.e., a strict prefix of the larger pool.
5. Each subset is sorted by original `row_index` before writing (restores natural order).
6. The script verifies nesting programmatically and exits loudly on any violation.

### 3.4 Random seed

**Seed: `329`** (the course number).  Passed via `--seed 329` (default).
All downstream runs use this same seed.

---

## 4. Inference-Only Files

For each batch size there are two files:

| File                     | Contains gold labels? | Purpose                      |
|--------------------------|-----------------------|------------------------------|
| `batch_<N>_full.csv`     | Yes                   | Scoring after the run        |
| `batch_<N>_inference.csv`| **No**                | Upload to the LLM            |

The inference files contain **only**:
```
item_id, sentence, option_a, option_b
```

Gold labels are withheld from the inference file so the model cannot see the
answer.  Only after the model has returned its predictions is the full file
used (in the scorer) to compute accuracy.

---

## 5. Prompt

### 5.1 Prompt file

```
prompts/base_zero_shot_batch_prompt.txt
```

### 5.2 Exact prompt text

```
You are labeling a pronoun-resolution dataset in the attached CSV file.

The file contains these columns:
- item_id
- sentence
- option_a
- option_b

Task:
For each row, determine whether the blank in the sentence refers to option_a or option_b.

Output requirements:
- Return ONLY CSV
- Use exactly this header:
item_id,answer
- For each row, answer must be exactly one of:
A
B
REFUSE
- Preserve the input row order
- Include exactly one output row for every input row
- Do not omit any item_id
- Do not add explanations, notes, markdown, or code fences

Interpretation:
- A means the blank refers to option_a
- B means the blank refers to option_b
- REFUSE means you cannot determine the answer from the sentence

Now label every row in the attached file.
```

### 5.3 Why this prompt is fixed

The purpose of the study is to isolate the effect of batch size, not to
optimize the prompt.  Using the same prompt text for all four conditions
ensures any performance difference is attributable solely to batch size.

The prompt is zero-shot (no examples).  It is deliberately minimal to avoid
introducing confounds.

---

## 6. Experiment Stages

### Stage 1 — Generate subsets

```bash
cd pronoun_resolution/en_testing_batch_size
python scripts/create_batch_size_subsets.py
```

Verify:
- All four `batch_<N>_full.csv` files exist in `data/`
- All four `batch_<N>_inference.csv` files exist in `data/`
- `metadata/subset_summary.md` shows correct sizes and label balance
- Console output confirms nesting: `batch_25 ⊆ … ⊆ batch_500  OK`

### Stage 2 — Upload one inference CSV per batch-size condition

For each condition, start a fresh model session and:

1. Open `prompts/base_zero_shot_batch_prompt.txt`
2. Attach the corresponding inference CSV (e.g. `data/batch_100_inference.csv`)
3. Send the prompt + attachment in a single message

**Do not** modify the prompt.  **Do not** reuse context across conditions.

### Stage 3 — Save raw model output

Copy the model's full text response and save it verbatim:

```
my_runs/<model>_<split>_raw.txt
```

Example: `my_runs/claude-sonnet-4-6_batch_100_raw.txt`

### Stage 4 — Parse model output into item_id,answer CSV

The model should return a CSV block.  Strip any surrounding markdown fences,
preamble, or trailing text, and save the bare CSV:

```
my_runs/<model>_<split>_parsed.csv
```

Expected format:

```
item_id,answer
42,A
57,B
...
```

Valid answer values: `A`, `B`, `REFUSE`.  Any other value is treated as an
invalid answer (tracked in `invalid_answer_rate`).

If the model returns no parseable CSV at all, `parseability_rate` will be 0
and you should record this as a failed run.

### Stage 5 — Score

```bash
python scripts/score_batched_run.py \
    --gold-csv         data/batch_100_full.csv \
    --predictions-csv  my_runs/claude-sonnet-4-6_batch_100_parsed.csv \
    --model-name       claude-sonnet-4-6 \
    --split-name       batch_100 \
    --raw-output-file  my_runs/claude-sonnet-4-6_batch_100_raw.txt \
    --latency-seconds  <wall-clock seconds> \
    --total-tokens     <total tokens from API response>
```

Results are written to:
```
results/claude-sonnet-4-6/batch_100/
    scored_predictions.csv
    summary.json
    summary.md
```

Repeat for all four batch-size conditions.

---

## 7. Evaluation Metrics

### 7.1 Accuracy metrics

| Metric | Definition |
|--------|------------|
| `accuracy` | Proportion of gold items answered correctly (A or B matching gold). REFUSE counts as incorrect. |
| `parseability_rate` | Proportion of gold items where the model returned a valid answer (A, B, or REFUSE). |
| `refusal_rate` | Proportion of gold items where the model returned REFUSE. |
| `missing_row_rate` | Proportion of gold items completely absent from the model output. |
| `duplicate_row_count` | Number of rows in the model output that share an item_id with another row. First occurrence is used for scoring; rest are flagged. |
| `invalid_answer_rate` | Proportion of prediction rows with an answer value outside {A, B, REFUSE}. |

### 7.2 Efficiency metrics

All efficiency metrics are **run-level totals** divided by `n_gold_items`.
They are averages, not per-item actuals, because the batch is a single API call.

| Metric | Definition |
|--------|------------|
| `total_latency` | Wall-clock seconds for the entire API call. |
| `avg_latency_per_item` | `total_latency / n_gold_items` |
| `total_tokens` | Total tokens consumed by the run (input + output). |
| `avg_tokens_per_item` | `total_tokens / n_gold_items` |
| `correct_per_1000_tokens` | `(n_correct / total_tokens) × 1000` — efficiency of correct answers per token spend. |

### 7.3 Row-position accuracy

The scorer assigns each item a 1-based **row position** reflecting its order in
the uploaded CSV, then buckets all items into 4 equally-sized contiguous blocks
and reports accuracy per bucket.

**Why this matters**: LLMs may exhibit degraded performance on items that appear
later in a long context window (the "lost-in-the-middle" effect).  If accuracy
in bucket 4 is materially lower than in bucket 1, it suggests the model
struggles with later items at that batch size.

For batch_25, each bucket is ~6 items; for batch_500, each bucket is ~125 items.
Position effects should be more visible at larger batch sizes.

---

## 8. Results Tables (fill in after runs)

### 8.1 Summary across batch sizes

| Batch size | Accuracy | Parseability | Refusal rate | Missing row rate | Duplicate row count | Invalid answer rate | Total latency (s) | Avg latency/item (s) | Total tokens | Avg tokens/item | Correct/1k tokens | Position effects notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 25  | — | — | — | — | — | — | — | — | — | — | — | — |
| 100 | — | — | — | — | — | — | — | — | — | — | — | — |
| 250 | — | — | — | — | — | — | — | — | — | — | — | — |
| 500 | — | — | — | — | — | — | — | — | — | — | — | — |

### 8.2 Row-position accuracy by batch size

Fill in after running the scorer for each condition.

#### batch_25

| Bucket | Row positions | N items | Accuracy |
|--------|---------------|---------|----------|
| 1 | — | — | — |
| 2 | — | — | — |
| 3 | — | — | — |
| 4 | — | — | — |

#### batch_100

| Bucket | Row positions | N items | Accuracy |
|--------|---------------|---------|----------|
| 1 | — | — | — |
| 2 | — | — | — |
| 3 | — | — | — |
| 4 | — | — | — |

#### batch_250

| Bucket | Row positions | N items | Accuracy |
|--------|---------------|---------|----------|
| 1 | — | — | — |
| 2 | — | — | — |
| 3 | — | — | — |
| 4 | — | — | — |

#### batch_500

| Bucket | Row positions | N items | Accuracy |
|--------|---------------|---------|----------|
| 1 | — | — | — |
| 2 | — | — | — |
| 3 | — | — | — |
| 4 | — | — | — |

---

## 9. How to Run — Example Commands

### Generate subsets (run once)

```bash
python pronoun_resolution/en_testing_batch_size/scripts/create_batch_size_subsets.py
```

With explicit options:

```bash
python pronoun_resolution/en_testing_batch_size/scripts/create_batch_size_subsets.py \
    --input  pronoun_resolution/en_master.csv \
    --seed   329 \
    --sizes  25 100 250 500
```

### Score a returned predictions CSV

```bash
python pronoun_resolution/en_testing_batch_size/scripts/score_batched_run.py \
    --gold-csv          pronoun_resolution/en_testing_batch_size/data/batch_100_full.csv \
    --predictions-csv   my_runs/claude-sonnet-4-6_batch_100_parsed.csv \
    --model-name        claude-sonnet-4-6 \
    --split-name        batch_100 \
    --latency-seconds   18.4 \
    --input-tokens      8200 \
    --output-tokens     320 \
    --total-tokens      8520
```

---

## 10. Reproducibility Checklist

Before reporting any results, confirm:

- [ ] `create_batch_size_subsets.py` was run with `--seed 329`
- [ ] `metadata/subset_summary.md` confirms sizes 25, 100, 250, 500
- [ ] Console output confirmed `batch_25 ⊆ … ⊆ batch_500  OK`
- [ ] Each model run used a fresh session (no shared context)
- [ ] The same prompt file (`base_zero_shot_batch_prompt.txt`) was used for all conditions
- [ ] Raw model output was saved before parsing
- [ ] The parsed CSV was checked to have header `item_id,answer`
- [ ] The scorer was run against the matching `batch_<N>_full.csv`
- [ ] `results/<model>/<split>/summary.json` exists for all four conditions
- [ ] Model name and temperature are recorded in the run metadata

---

## 11. File Reference

| File | Role |
|------|------|
| `data/english_master_normalized.csv` | Full 826-item normalized English dataset |
| `data/batch_<N>_full.csv` | Subset WITH gold labels (used only for scoring) |
| `data/batch_<N>_inference.csv` | Subset WITHOUT gold labels (upload to LLM) |
| `data/subset_manifest.csv` | All (item_id, batch_size) pairs |
| `metadata/subset_summary.json` | Machine-readable subset metadata |
| `metadata/subset_summary.md` | Human-readable subset metadata |
| `prompts/base_zero_shot_batch_prompt.txt` | The single fixed prompt for all conditions |
| `scripts/create_batch_size_subsets.py` | Generates all data and metadata files |
| `scripts/score_batched_run.py` | Scores one batched model run |
| `results/<model>/<split>/scored_predictions.csv` | Row-level scoring output |
| `results/<model>/<split>/summary.json` | Machine-readable run summary |
| `results/<model>/<split>/summary.md` | Human-readable run summary |
