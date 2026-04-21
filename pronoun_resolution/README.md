# Pronoun Resolution

This directory is the unified home for pronoun-resolution work in the main project.

It currently contains three related sub-experiments:

1. `mlm_african/` — the main African-language prompt-engineering benchmark (`en / am / ig / zu`)
2. `en_testing_batch_size/` — the English-only batch-size study built from the African benchmark's English data
3. `mlm_european/` — the imported multilingual baseline from `srijon-2.0` (`en / fr / de / ru`)

These are kept as separate subtrees because they are not the same benchmark family.

## Benchmark family A: African prompt-testing benchmark

This benchmark family is documented in [explanation.md](explanation.md) and includes:

- `en`
- `am`
- `ig`
- `zu`

Use this subtree for the main prompt-engineering work:

- [mlm_african/README.md](mlm_african/README.md)
- [mlm_african/scripts/generate_splits.py](mlm_african/scripts/generate_splits.py)
- [mlm_african/scripts/generate_inference_full.py](mlm_african/scripts/generate_inference_full.py)
- [mlm_african/scripts/cli_scorer_updated.py](mlm_african/scripts/cli_scorer_updated.py)

Important layout note:

- raw benchmark CSVs now live in `mlm_african/data/`
- canonical evaluation splits live in `mlm_african/{lang}/source/`

## Benchmark family B: English batch-size study

This is the English-only batch-size sensitivity study derived from the African benchmark family.

Use:

- [en_testing_batch_size/README.md](en_testing_batch_size/README.md)
- [en_testing_batch_size/scripts/create_batch_size_subsets.py](en_testing_batch_size/scripts/create_batch_size_subsets.py)
- [en_testing_batch_size/scripts/score_batched_run.py](en_testing_batch_size/scripts/score_batched_run.py)
- [en_testing_batch_size/scripts/cli_scorer.py](en_testing_batch_size/scripts/cli_scorer.py)

Its canonical source English master is:

```text
pronoun_resolution/mlm_african/data/en_master.csv
```

## Benchmark family C: imported European baseline

This is the imported multilingual baseline from `srijon-2.0`.

According to the imported docs, it uses:

- **WinoGrande** for English
- **Wino-X** for French, German, and Russian

Use:

- [mlm_european/README.md](mlm_european/README.md)
- [mlm_european/docs/README.md](mlm_european/docs/README.md)
- [mlm_european/answers/pronoun_resolution/readme.md](mlm_european/answers/pronoun_resolution/readme.md)
- [mlm_european/scripts/normalize.py](mlm_european/scripts/normalize.py)
- [mlm_european/scripts/join_and_split.py](mlm_european/scripts/join_and_split.py)
- [mlm_european/scripts/generate_sample100.py](mlm_european/scripts/generate_sample100.py)
- [mlm_european/scripts/generate_challenge_splits.py](mlm_european/scripts/generate_challenge_splits.py)
- [mlm_european/scripts/cli_scorer.py](mlm_european/scripts/cli_scorer.py)
- [mlm_european/scripts/batch_scorer.py](mlm_european/scripts/batch_scorer.py)

## Root-level notes

The supporting project notes remain at the root:

- [all_prompts.md](all_prompts.md)
- [explanation.md](explanation.md)

The raw African benchmark CSVs no longer need to live at the root of `pronoun_resolution/`; they belong under `mlm_african/data/`.

## Backup

The pre-cleanup version of this directory was copied to:

```text
old-work/pronoun_resolution/
```
