# Pronoun Resolution

This directory is the unified home for pronoun-resolution work in the main project.

It now brings together **three related sub-experiments**:

1. the main prompt-engineering workflow on the African-language benchmark line
2. the English-only batch-size study
3. the imported multilingual baseline from `srijon-2.0`

The key design choice in this cleanup is that these are **not flattened into one dataset folder**, because they are not just different splits of the same benchmark. They are different experiment families with different source datasets, language coverage, metadata, and scripts.

## Why there are multiple benchmark families

The pronoun-resolution work in this repo now spans **two different source dataset families**, which is useful because it gives a more robust multilingual comparison than relying on only one benchmark line.

### Benchmark family A: main prompt-testing dataset

This is the benchmark line documented in [explanation.md](explanation.md). It uses:

- `en`
- `am`
- `ig`
- `zu`

The English, Amharic, Igbo, and Zulu materials come from the low-resource African-language benchmark workflow described in that file, with filtering applied to keep cross-comparable pronoun-resolution items.

This benchmark family powers:

- the main prompt-engineering workflow in [`testing/`](testing/)
- the English-only batch-size study in [`en_testing_batch_size/`](en_testing_batch_size/)

### Benchmark family B: imported multilingual baseline from `srijon-2.0`

This is the second multilingual baseline copied into [`mlm_baseline/`](mlm_baseline/).

According to the imported `srijon-2.0` documentation, its pronoun-resolution data comes from:

- **WinoGrande** for English
- **Wino-X** for French, German, and Russian

Languages in this benchmark family:

- `en`
- `fr`
- `de`
- `ru`

Important clarification:

- the imported pronoun-resolution baseline uses **WinoGrande / Wino-X**
- **XNLI is not the pronoun-resolution source here**; XNLI is relevant to the presupposition pipeline, not this one

Because English appears in both benchmark families, this repo now contains **two different English pronoun-resolution benchmarks**, not one duplicated English dataset.

## Directory structure

### `testing/`

The main prompt-engineering workflow for the African-language benchmark line.

This contains:

- canonical split files for `en`, `am`, `ig`, `zu`
- prompts `P0` through `P4`
- results and challenge-and-miss outputs
- the newer scoring and split-generation scripts

Primary documentation:

- [testing/README.md](testing/README.md)
- [testing/prompts/README.md](testing/prompts/README.md)
- [testing/results/README.md](testing/results/README.md)

### `en_testing_batch_size/`

The English-only batch-size sensitivity study.

This is a separate sub-experiment built on the main benchmark family A English data. It compares how pronoun-resolution quality changes as batch size increases.

Primary documentation:

- [en_testing_batch_size/README.md](en_testing_batch_size/README.md)

### `mlm_baseline/`

The imported multilingual baseline copied from `srijon-2.0`.

This subtree keeps the older multilingual benchmark infrastructure close to its original layout so the imported scripts still make sense.

It contains:

- `pronoun_resolution/` -> the normalized multilingual benchmark tree
- `answers/pronoun_resolution/` -> imported answer/match artifacts from `srijon-2.0/answers/pronoun_resolution/`
- `scripts/` -> imported normalization / split / scoring scripts
- `docs/` -> imported task inventory, assumptions, split strategy, and label-normalization notes
- `prompts/` -> imported prompt template
- `SRIJON_2_0_README.md` -> preserved top-level source description

Primary documentation:

- [mlm_baseline/README.md](mlm_baseline/README.md)

## Replication map

### Main prompt-engineering workflow

Use:

- [testing/scripts/generate_splits.py](testing/scripts/generate_splits.py)
- [testing/scripts/generate_inference_full.py](testing/scripts/generate_inference_full.py)
- [testing/scripts/cli_scorer_updated.py](testing/scripts/cli_scorer_updated.py)

### English batch-size study

Use:

- [en_testing_batch_size/scripts/create_batch_size_subsets.py](en_testing_batch_size/scripts/create_batch_size_subsets.py)
- [en_testing_batch_size/scripts/score_batched_run.py](en_testing_batch_size/scripts/score_batched_run.py)
- [en_testing_batch_size/scripts/cli_scorer.py](en_testing_batch_size/scripts/cli_scorer.py)

### Imported MLM baseline

Use:

- [mlm_baseline/answers/pronoun_resolution/readme.md](mlm_baseline/answers/pronoun_resolution/readme.md)
- [mlm_baseline/docs/README.md](mlm_baseline/docs/README.md)
- [mlm_baseline/scripts/normalize.py](mlm_baseline/scripts/normalize.py)
- [mlm_baseline/scripts/join_and_split.py](mlm_baseline/scripts/join_and_split.py)
- [mlm_baseline/scripts/generate_sample100.py](mlm_baseline/scripts/generate_sample100.py)
- [mlm_baseline/scripts/generate_challenge_splits.py](mlm_baseline/scripts/generate_challenge_splits.py)
- [mlm_baseline/scripts/cli_scorer.py](mlm_baseline/scripts/cli_scorer.py)
- [mlm_baseline/scripts/batch_scorer.py](mlm_baseline/scripts/batch_scorer.py)
- [mlm_baseline/docs/task_inventory.md](mlm_baseline/docs/task_inventory.md)
- [mlm_baseline/docs/assumptions.md](mlm_baseline/docs/assumptions.md)
- [mlm_baseline/docs/split_strategy.md](mlm_baseline/docs/split_strategy.md)

The `mlm_baseline/docs/` files are worth keeping even though they are cross-task documents from the larger `srijon-2.0` cleanup. They contain the most explicit written record of source datasets, schema quirks, encoding fixes, and split assumptions for the imported pronoun-resolution baseline.

## Legacy root files

The flat CSVs at the root of this directory, such as:

- `en_master.csv`
- `am_master.csv`
- `ig_master.csv`
- `zu_master.csv`
- `*_questions_only.csv`
- `*_answers_only.csv`

have been kept in place because the current split-generation and batch-size scripts still reference them directly.

Related notes:

- [all_prompts.md](all_prompts.md)
- [explanation.md](explanation.md)

## Backup

The pre-cleanup version of this entire directory was copied to:

```text
old-work/pronoun_resolution/
```

That backup is intentionally untouched so nothing from the original main repo layout is lost.
