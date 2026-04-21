# Batch-Size Subset Summary

## Source Data

- **English master file**: `en_master.csv`
- **Full path**: `/Users/claireburkhardt/Documents/cs329-group/pronoun_resolution/mlm_african/data/en_master.csv`
- **Random seed**: 329
- **Generated**: 2026-04-16T02:09:29.162847Z

## Subset Sizes and Label Balance

| Subset | N | Label A | Label B | A fraction |
|--------|---|---------|---------|------------|
| batch_25 | 25 | 12 | 13 | 0.4800 |
| batch_100 | 100 | 50 | 50 | 0.5000 |
| batch_250 | 250 | 125 | 125 | 0.5000 |
| batch_500 | 500 | 250 | 250 | 0.5000 |

## Nesting Relationships

- `batch_25` ⊆ `batch_100`: verified
- `batch_100` ⊆ `batch_250`: verified
- `batch_250` ⊆ `batch_500`: verified

## Schema Decisions

- **item_id**: Preserved from `item_num` in the source file. Unique and stable.
- **gold_answer**: Normalised to uppercase `A` or `B` (from `correct_letter`).
- **option_a / option_b**: Mapped from `option1` / `option2`.

## Subset Construction

Items are drawn as label-balanced **prefixes** from a single deterministically
shuffled pool for each label (A and B).  The shuffle uses seed `329` via
`pandas.DataFrame.sample(random_state=329)`.

For each subset of size N:
- label-A items = first `floor(N/2)` rows of the shuffled A pool
- label-B items = first `ceil(N/2)` rows of the shuffled B pool

Because every smaller prefix is a strict subset of every larger prefix, the
nesting guarantee holds by construction.  Items are sorted by their original
`row_index` within each subset before writing.

## Inference-Only Files

Each `batch_<N>_inference.csv` contains **only** these columns:

```
item_id, sentence, option_a, option_b
```

Gold labels are intentionally withheld so the model-facing file cannot leak
the answer.  Gold labels are in `batch_<N>_full.csv`, used only for scoring
after the model run is complete.

## Assumptions

1. The canonical English master is `pronoun_resolution/mlm_african/data/en_master.csv`.
2. The file uses the schema: `item_num, sentence, option1, option2,
   correct_answer_num, correct_letter, correct_text`.
3. `item_num` is unique and serves as the stable item identifier.
4. All gold labels are exactly `A` or `B` (after upper-casing `correct_letter`).
