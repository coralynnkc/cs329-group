# Presuppositions All

This directory is the new unified home for presupposition work in this repo.

It brings together two previously separate sources:

- `presupposition/` -> preserved here as `confer_baseline/`
- `srijon-2.0/presuppositions/` -> preserved here as `prompt_benchmarking/`

The goal is to make the presupposition work easier to navigate without breaking the scripts, folder assumptions, or existing experiment assets.

## Documentation Status

The original documentation from both sources has been kept, but lightly cleaned up so that:

- local commands point to the new folders instead of the old ones
- row counts and file names match the copied data
- each subtree states what kind of experiment it contains

Where older writeups are interpretive or provisional, that language has been preserved rather than silently rewritten.

## Structure

### `confer_baseline/`

This is the original compact CoNFER English workflow copied from the old top-level `presupposition/` folder.

Use this when you want the simpler baseline pipeline:

- dataset split files in `data/`
- mini-eval files in `mini/`
- scored outputs in `results/`
- runnable scripts in `scripts/`

Typical commands:

```bash
cd presuppositions-all/confer_baseline
python3 scripts/make_mini.py
python3 scripts/score_baseline.py --model sonnet
python3 scripts/update_readme.py
```

### `prompt_benchmarking/`

This is the richer presupposition experiment tree copied from `srijon-2.0/presuppositions/`.

It contains two distinct kinds of presupposition work:

- multilingual presupposition prompt benchmarking across `de`, `en`, `fr`, `hi`, `ru`, and `vi`
- English-only CONFER prompt benchmarking in `confer_en/`

Key subfolders:

- `confer_en/` -> CONFER English prompt-benchmark gold/input files
- `de/`, `en/`, `fr/`, `hi/`, `ru/`, `vi/` -> multilingual data splits
- `prompts/` -> prompt variants such as `p0`, `p1`, `p2`, `p4`, etc.
- `results/` -> model outputs and summary JSON files
- `scripts/` -> batch scorers for multilingual and CONFER benchmarking

Typical commands:

```bash
cd presuppositions-all/prompt_benchmarking
python3 scripts/batch_scorer_evaluation.py --presup-dir . --results results/chat_5.4_p0 --output results/chat_5.4_p0/results_summary.json
python3 scripts/batch_scorer_CONFER.py --gold confer_en/presupposition_answers.csv --results results/CONFER-chat-5.4 --output results/CONFER-chat-5.4/results_summary.json
```

## Backup / Migration

The original top-level `presupposition/` folder has been copied exactly to:

```text
old-work/presupposition/
```

That backup is intentionally untouched so you can always refer back to the original layout.

## What Is Not Included Here Yet

This folder is only the unified home for **presupposition** work.

Items still left in `srijon-2.0/` for later extraction include:

- pronoun resolution / Wino-style work
- any broader non-presupposition assets you want to sort later

## Working Principle

To minimize breakage, this refactor preserves each pipeline as a self-contained subtree instead of rewriting internal scripts to a new shared API. That means:

- old relative script assumptions inside each subtree still hold
- results and prompts stay near the pipeline that produced them
- the new root README gives one clean entry point without forcing a risky rewrite
