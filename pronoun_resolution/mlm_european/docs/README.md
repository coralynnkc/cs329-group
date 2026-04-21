# Imported Documentation Guide

This folder preserves the important documentation that came with the `srijon-2.0` multilingual baseline.

These files are kept even though some of them also discuss presupposition and lemmatization work, because they record normalization decisions and source-dataset provenance that matter for understanding how the imported pronoun-resolution baseline was built.

## Most relevant files for pronoun resolution

- `task_inventory.md`
  Records the actual pronoun-resolution language coverage, source datasets, row counts, and normalized schemas.
  This is the best first reference for confirming that this baseline uses:
  - **WinoGrande** for English
  - **Wino-X** for French, German, and Russian

- `assumptions.md`
  Documents non-obvious normalization decisions, especially:
  - why English has no `option_a` / `option_b` columns in the imported source
  - why French and German required encoding repair
  - why gold labels are not embedded directly in the raw imported source files

- `label_normalization.md`
  Explains the scorer-side label conventions.
  For pronoun resolution, this clarifies how predictions and correctness are represented in normalized files.

- `split_strategy.md`
  Records the recommended split policy used for the imported restructuring and notes caveats around paired Winograd-style rows.

## Why the docs are cross-task

The original `srijon-2.0` documentation was written for the whole restructuring effort, not only pronoun resolution.

That means some sections mention:

- presuppositions
- lemmatization

Those sections are intentionally preserved rather than trimmed away, because they provide context for how the imported pipelines were normalized and organized.

## Suggested reading order

1. `task_inventory.md`
2. `assumptions.md`
3. `split_strategy.md`
4. `label_normalization.md`
