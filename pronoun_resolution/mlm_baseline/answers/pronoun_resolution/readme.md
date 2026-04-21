# Pronoun-Resolution Answer Artifacts

This folder preserves the separate answer-aligned files that were stored in:

```text
srijon-2.0/answers/pronoun_resolution/
```

They are included in the unified `pronoun_resolution/mlm_baseline/` subtree so the imported baseline remains reproducible without having to look back into `srijon-2.0`.

## What is here

- `english_with_match.xlsx`
- `lm_wino_x_en-de_only_with_match.xlsx`
- `lm_wino_x_en-fr_only_with_match.xlsx`
- `lm_wino_x_en-ru_only_with_match.xlsx`
- `challenge_and_miss_answers/`
- `challenge_and_miss_answers.zip`

## How these relate to the normalized benchmark tree

The main benchmark CSVs used by the imported baseline live under:

```text
pronoun_resolution/mlm_baseline/pronoun_resolution/
```

Those normalized files are what the imported scripts operate on most directly.

The files in this directory are useful when you want the separate answer/match artifacts that were kept alongside the original `srijon-2.0` workflow.

## Relevant scripts

The companion scripts for this baseline live in:

```text
pronoun_resolution/mlm_baseline/scripts/
```

That folder includes:

- `normalize.py`
- `join_and_split.py`
- `generate_sample100.py`
- `generate_challenge_splits.py`
- `cli_scorer.py`
- `batch_scorer.py`

## Source benchmark note

Per the imported documentation:

- English is based on **WinoGrande**
- French, German, and Russian are based on **Wino-X**

For more detail, see:

- `../../docs/task_inventory.md`
- `../../docs/assumptions.md`
- `../../README.md`
