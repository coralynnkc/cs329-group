# Presupposition — CoNFER

Source: **CoNFER** (Connotative Framework for Entailment Reasoning) — a dataset probing whether language models recognize presupposition triggers. Each example pairs a premise with a presupposed hypothesis and asks whether the premise entails, is neutral to, or contradicts the hypothesis.

Two families of presupposition triggers are covered:

| Trigger type | Description | Example |
| --- | --- | --- |
| `*_possessive` | Possessive NPs presuppose the existence of the possessor's referent | *"Emily's best friend..."* → Emily has a best friend |
| `*_again` | Change-of-state verbs (*again*, *stop*, *return*) presuppose a prior state | *"Alex stopped smoking"* → Alex used to smoke |

Each trigger family has 5 sub-types (type1–type5) corresponding to different linguistic environments (negation, belief contexts, questions, etc.).

---

## Baseline Results

<!-- results:start -->
| Model | S1 Acc | S2 Acc | S3 Acc | Mean Acc | F1-E | F1-N | F1-C | Macro-F1 |
| ----- | ------ | ------ | ------ | -------- | ---- | ---- | ---- | -------- |
| sonnet | 0.45 | 0.46 | 0.44 | 0.45 | 0.6171 | 0.0142 | 0.4897 | 0.3736 |
| opus | 0.58 | 0.58 | 0.55 | 0.57 | 0.6949 | 0.0979 | 0.7558 | 0.5162 |
| chatgpt | 0.7 | 0.69 | 0.71 | 0.7 | 0.8218 | 0.6779 | 0.5177 | 0.6725 |
| gemini | 0.59 | 0.58 | 0.61 | 0.5933 | 0.7807 | 0.5288 | 0.3252 | 0.5449 |
<!-- results:end -->

*Run `python presupposition/scripts/update_readme.py` after scoring to populate this table.*

---

## Files

### Data (`data/`)

| File | Rows | Description |
| --- | --- | --- |
| `data/train.csv` | 6,981 | Training split |
| `data/validation.csv` | 2,367 | Validation split |
| `data/test.csv` | 2,348 | Test split — used for mini eval |

Each file has five columns:

```
premise, hypothesis, gold_label, type, uid
```

- `premise` — the sentence containing the presupposition trigger
- `hypothesis` — the presupposed content
- `gold_label` — `E` (Entailment), `N` (Neutral), or `C` (Contradiction)
- `type` — presupposition trigger sub-type (e.g. `type3_again`, `type5_possessive`)
- `uid` — unique row identifier

**Label distribution (test):** E = 760 (32%), N = 861 (37%), C = 727 (31%)

---

## Task

| Input | Target |
| --- | --- |
| `premise` + `hypothesis` | `E`, `N`, or `C` |

The core challenge is recognising *projection*: presuppositions survive under negation, questions, and attitude verbs. A model that relies purely on surface entailment cues will confuse E/C with N in these contexts.

---

## Baselining

### Workflow

1. Generate mini CSVs (one-time):

   ```bash
   python presupposition/scripts/make_mini.py
   ```

   Creates `mini/presupposition_input.csv` and `mini/presupposition_answers.csv` — 3 samples × 100 rows each (stratified by label).

2. **Send one message** using the prompt below — paste the CSV content directly. Save the model's response as:

   ```
   mini/presupposition_predictions_<model>.csv
   ```

   Required columns: `sample_id`, `row_id`, `predicted_label`

3. Score:

   ```bash
   python presupposition/scripts/score_baseline.py --model sonnet
   ```

4. Update the README table:

   ```bash
   python presupposition/scripts/update_readme.py
   ```

---

### Prompt

```
You are evaluating presupposition in English.

Each row contains a PREMISE and a HYPOTHESIS. Decide whether the premise ENTAILS the hypothesis, is NEUTRAL to it, or CONTRADICTS it, specifically with respect to presupposition:

- E (Entailment)     — the premise triggers / preserves the presupposition in the hypothesis
- N (Neutral)        — the premise does not clearly trigger or cancel the presupposition
- C (Contradiction)  — the premise explicitly cancels or contradicts the presupposition

Important: presuppositions project through negation, questions, and belief contexts.
"John didn't stop smoking" still presupposes John used to smoke → label that E.

Return ONLY a CSV with columns: sample_id, row_id, predicted_label
Use exactly E, N, or C — no other values.

<paste presupposition_input.csv here>
```

---

## Metrics

- **Accuracy** — fraction of correct 3-way classifications
- **F1-E / F1-N / F1-C** — per-label F1 for each class
- **Macro-F1** — unweighted average of F1-E, F1-N, F1-C

All metrics are reported per sample and averaged across all 3 samples.

---

## Validation

```bash
# Check that make_mini produces 300 rows (3 x 100) stratified by label
python presupposition/scripts/make_mini.py

# Dry-run scoring with debug output
python presupposition/scripts/score_baseline.py --model sonnet --debug
```
