# African Prompt-Testing Pipeline Notes

This note describes the active split-generation pipeline for the African pronoun-resolution benchmark.

## Canonical layout

```text
mlm_african/
  data/                raw benchmark-family CSVs
  en/source/           canonical English splits
  am/source/           canonical Amharic splits
  ig/source/           canonical Igbo splits
  zu/source/           canonical Zulu splits
  metadata/            split_summary.{json,md}
  scripts/             split-generation + regeneration scripts
```

## Main commands

Generate or refresh the canonical split files from the raw English master:

```bash
python pronoun_resolution/mlm_african/scripts/generate_splits.py
```

Regenerate `inference/` and `full/` files from the canonical `source/` splits:

```bash
python pronoun_resolution/mlm_african/scripts/generate_inference_full.py
```

## Key outputs

- `en/source/en_master_normalized.csv`
- `en/source/en_fewshot_bank.csv`
- `en/source/en_dev.csv`
- `en/source/en_challenge.csv`
- `en/source/en_holdout.csv`
- `en/source/en_split_manifest.csv`
- matching propagated split files in `am/source/`, `ig/source/`, and `zu/source/`
- `metadata/split_summary.json`
- `metadata/split_summary.md`
