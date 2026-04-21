# African MLM Benchmark

This directory contains the main African-language pronoun-resolution experiment in the unified `pronoun_resolution/` workspace.

Languages in this benchmark family:

- `en`
- `am`
- `ig`
- `zu`

This subtree now keeps the experiment in one place:

- `data/` holds the raw master and helper CSVs for the benchmark family
- `{lang}/source/` holds the canonical split files used for evaluation
- `{lang}/inference/` holds model-facing CSVs regenerated from `source/`
- `{lang}/full/` holds scorer-facing CSVs regenerated from `source/`
- `results/` holds run outputs and challenge-and-miss files
- `prompts/` holds prompt templates
- `scripts/` holds split-generation and regeneration scripts
- `metadata/` holds split manifests and summary docs

## Raw data

The raw benchmark CSVs live in:

```text
mlm_african/data/
```

That folder includes:

- `en_master.csv`
- `am_master.csv`
- `ig_master.csv`
- `zu_master.csv`
- `*_questions_only.csv`
- `*_answers_only.csv`

These are the benchmark-family inputs. They belong here rather than at the root of `pronoun_resolution/`.

## Canonical experiment files

The authoritative evaluation files are the split CSVs in:

- `en/source/`
- `am/source/`
- `ig/source/`
- `zu/source/`

Do not edit `inference/` or `full/` directly. Regenerate those from `source/`.

## Regeneration

Generate or refresh the split files:

```bash
python pronoun_resolution/mlm_african/scripts/generate_splits.py
```

Generate or refresh `inference/` and `full/` from `source/`:

```bash
python pronoun_resolution/mlm_african/scripts/generate_inference_full.py
```

## Relationship to the other pronoun-resolution work

- `../en_testing_batch_size/` reuses the English benchmark from this African benchmark family
- `../mlm_european/` is the imported WinoGrande / Wino-X baseline from `srijon-2.0`

## Results Snapshot

The saved African-benchmark results currently live in:

- `results/README.md`
- `results/README_chat.md`
- `results/challenge_and_miss/`

Using the numbers already recorded there:

- Sonnet 4.6 prompt `P0` shows a clear language gradient on the dev split:
  English `0.870` accuracy / `0.869` macro-F1, Amharic `0.778` / `0.777`,
  Igbo `0.578` / `0.578`, and Zulu `0.556` / `0.558`.
- Chat 5.4 improves strongly on English across prompts in the saved dev runs,
  moving from `0.90` accuracy at `P0` to `0.94` at `P3`.
- The saved notes also record that Chat 5.3 was not a stable baseline here:
  it failed badly on some African-benchmark prompt conditions, including the
  English and Amharic `P0` runs described in `results/README_chat.md`.

## Current Conclusions

- Prompt engineering helps on the English side of this benchmark, especially for Chat 5.4.
- Language effects are larger than prompt effects in the saved runs: English and Amharic are materially stronger than Igbo and Zulu.
- The current benchmark writeup therefore supports two takeaways:
  prompt choice matters, but cross-language robustness is the bigger open problem in this African benchmark family.

## Backup

The original pre-cleanup pronoun-resolution tree was copied to:

```text
old-work/pronoun_resolution/
```
