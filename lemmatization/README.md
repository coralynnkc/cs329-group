# Lemmatization Experiments

This directory now centers the English lemmatization evaluation we ran on **UD English EWT** (`en_ewt-ud`). The earlier UniMorph-oriented project README has been preserved as [old_unimorph_readme.md](old_unimorph_readme.md).

## Overview

We extracted token-level `(form, lemma)` pairs from the UD English EWT CoNLL-U files and evaluated five LLMs on balanced lemmatization subsets:

- Claude Sonnet 4.6 (`sonnet_4.6`)
- Claude Opus 4.6 (`opus_4.6`)
- GPT-5.4 (`gpt_5.4`)
- GPT-5.3 (`chat_5.3` in filenames)
- Gemini 3 (`gemeni_3` in filenames)

The core question is not just overall accuracy, but how performance changes as batch size grows and as examples become more difficult.

## Dataset And Sampling

### Source data

- Corpus: **UD English EWT**
- Raw files live in [data](data/), including `en_ewt-ud-*.conllu`
- Lemma extraction is handled by [scripts/extract_lemmas.py](scripts/extract_lemmas.py)

`extract_lemmas.py` reads CoNLL-U rows, skips comments, multiword-token ranges, empty nodes, and missing lemmas, and writes a flat CSV of `form,lemma` pairs.

### Evaluation subsets

The scored experiments use balanced stratified samples saved as:

- [data/sample_100_stratified_labeled.csv](data/sample_100_stratified_labeled.csv)
- [data/sample_200_stratified_labeled.csv](data/sample_200_stratified_labeled.csv)
- [data/sample_300_stratified_labeled.csv](data/sample_300_stratified_labeled.csv)
- [data/sample_500_stratified_labeled.csv](data/sample_500_stratified_labeled.csv)

Each evaluation set is evenly balanced across five subgroup labels:

- `ambiguous`: the same surface form maps to multiple lemmas in the corpus
- `changed`: the lemma differs from the surface form after lowercasing
- `easy`: none of the harder conditions apply
- `irregular`: form and lemma share fewer than 3 leading characters
- `rare`: lemma frequency is in the bottom 10%

In practice, this means each sample size is exactly 20% per subgroup:

| Sample size | Ambiguous | Changed | Easy | Irregular | Rare |
| --- | ---: | ---: | ---: | ---: | ---: |
| 100 | 20 | 20 | 20 | 20 | 20 |
| 200 | 40 | 40 | 40 | 40 | 40 |
| 300 | 60 | 60 | 60 | 60 | 60 |
| 500 | 100 | 100 | 100 | 100 | 100 |

The subgroup assignment and sampling logic live in [scripts/stratified_sample.py](scripts/stratified_sample.py). Rows that satisfy multiple difficulty conditions are assigned to a single label by priority:

`irregular > ambiguous > rare > changed > easy`

### Additional train/dev/test splits

For future fine-tuning work, [scripts/make_splits.py](scripts/make_splits.py) creates lemma-grouped `80/10/10` splits for the broader morphology resources under [splits](splits/). Those splits are separate from the balanced evaluation subsets used here.

## Evaluation Methodology

- Gold labels come from the `sample_*_stratified_labeled.csv` files.
- Model predictions are stored in `data/<model>_<n>_samples.csv`.
- Evaluation is performed by [scripts/evaluate_lemmas.py](scripts/evaluate_lemmas.py).
- Metrics reported:
  - `acc`: exact-match lemma accuracy
  - `mean_ned`: mean normalized edit distance
  - `macro_f1`: macro average over the five subgroup labels used in the balanced evaluation

Because the evaluation sets are subgroup-balanced, overall accuracy and subgroup trends are easy to compare across models and sample sizes.

## Benchmark Results

### Overall performance by batch size

| Model | n=100 | n=200 | n=300 | n=500 | Mean acc | Mean F1 | Mean NED |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sonnet 4.6 | 0.9300 | 0.9400 | 0.9233 | 0.9320 | 0.9313 | 0.9313 | 0.0442 |
| Opus 4.6 | 0.9500 | 0.9650 | 0.8567 | 0.8600 | 0.9079 | 0.9079 | 0.0669 |
| GPT-5.4 | 0.9300 | 0.9400 | 0.9200 | 0.9300 | 0.9300 | 0.9300 | 0.0418 |
| GPT-5.3 | 0.8500 | 0.7950 | 0.5400 | 0.4720 | 0.6643 | 0.6643 | 0.3138 |
| Gemini 3 | 0.9100 | 0.9650 | 0.8633 | 0.9720 | 0.9276 | 0.9276 | 0.0491 |

Notes:

- All five models now have scored runs for `n=100`, `200`, `300`, and `500`.
- GPT-5.4 metrics come from [results/eval_gpt_5.4_summary_all.csv](results/eval_gpt_5.4_summary_all.csv).
- The cross-model aggregate file is [results/summary_all.csv](results/summary_all.csv).

### Performance by task category

The table below averages subgroup accuracy across the scored batch sizes available for each model.

| Model | Ambiguous | Changed | Easy | Irregular | Rare | Mean F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sonnet 4.6 | 0.9363 | 0.9817 | 0.9654 | 0.8275 | 0.9458 | 0.9313 |
| Opus 4.6 | 0.9375 | 0.9792 | 0.9629 | 0.7592 | 0.9008 | 0.9079 |
| GPT-5.4 | 0.9363 | 0.9446 | 0.9654 | 0.8325 | 0.9712 | 0.9300 |
| GPT-5.3 | 0.7667 | 0.6887 | 0.7529 | 0.5000 | 0.6129 | 0.6643 |
| Gemini 3 | 0.9450 | 0.9817 | 0.9846 | 0.8117 | 0.9150 | 0.9276 |

### What stands out

- `easy` and `changed` are the most stable categories across stronger models.
- `irregular` is the hardest subgroup for every model.
- GPT-5.3 falls off sharply as the batch size increases, especially at `n=300` and `n=500`.
- GPT-5.4 is the most stable overall among the fully scored four-size runs.
- Gemini 3 is competitive at `n=200` and especially strong at `n=500`, but its `n=300` run is much weaker than its other settings.
- Opus 4.6 starts very strong at smaller batch sizes, then drops substantially at `n=300` and `n=500`, largely due to the `irregular` category.

## Per-Model Notes

### Sonnet 4.6

- Strong and consistent across all four batch sizes.
- Best categories: `changed`, `easy`, and `rare`
- Weakest category: `irregular`

### Opus 4.6

- Best small-batch performer together with Gemini at `n=200`
- Accuracy drops at larger batches, with the largest degradation on `irregular`

### GPT-5.4

- Most even profile across all four batch sizes
- No dramatic collapse on larger batches
- Best average `rare` accuracy among the five models in this README

### GPT-5.3

- Usable on the smallest sample, but degrades rapidly as context grows
- Particularly weak on `irregular` and `rare` at larger batch sizes

### Gemini 3

- High ceiling, especially at `n=200` and `n=500`
- More variance between runs than GPT-5.4
- `n=300` is notably weaker than its other three evaluations

## Preliminary Conclusions

- For this task, **model quality matters more than prompt wording alone**. The stronger frontier models stay near or above the low-0.90s on exact-match accuracy for most runs.
- **Irregular lemmatization remains the main failure mode**. Even the strongest models drop here first.
- **Batch size sensitivity is real**. GPT-5.3, Opus 4.6, and Gemini 3 all show at least one larger-batch evaluation with a clear drop in quality.
- **GPT-5.4 currently looks like the safest default choice** if we care about consistency across sample sizes.
- **Gemini 3 is worth keeping in the comparison set** because its best runs are excellent, but it appears more volatile.
- **Sonnet 4.6 remains competitive** and now looks slightly more stable than Opus once all four batch sizes are included.

## Key Files

- Gold evaluation sets: [data](data/)
- Scoring script: [scripts/evaluate_lemmas.py](scripts/evaluate_lemmas.py)
- Shared summary: [results/summary_all.csv](results/summary_all.csv)
- GPT-5.4 summary: [results/eval_gpt_5.4_summary_all.csv](results/eval_gpt_5.4_summary_all.csv)
- Archived README: [old_unimorph_readme.md](old_unimorph_readme.md)
