# Split Summary

## Source Data

- **English master file**: `en_master.csv`
- **Full path**: `pronoun_resolution/mlm_african/data/en_master.csv`
- **Random seed**: 329
- **Total items**: 826

## Split Sizes and Label Balance

| Split | N | A | B |
|-------|---|---|---|
| fewshot_bank | 8 | 4 | 4 |
| dev | 100 | 50 | 50 |
| challenge | 50 | 25 | 25 |
| holdout | 668 | 329 | 339 |

## Schema Decisions

- **item_id**: Preserved from `item_num` in the source file. This column is unique
  and stable, so no content-hash fallback was needed.
- **gold_answer**: Normalised to uppercase `A` or `B` (from `correct_letter`).
- **option_a / option_b**: Mapped from `option1` / `option2`.
- **difficulty_score**: Composite of sentence token length (weight 0.4),
  clause-boundary punctuation count (0.3), and mean token distance from the blank
  to each candidate mention (0.3 when recoverable, else redistributed 0.57/0.43).
  Higher score → harder item.

## Split Construction Notes

- **fewshot_bank**: Selected from the lowest-difficulty medium-length items,
  balanced by gold label. Disjoint from dev, challenge, and holdout.
- **dev**: Stratified on (gold_answer × coarse sentence-length bin: short/medium/long).
  Exact requested size achieved via top-up from largest strata.
- **challenge**: Top-difficulty items from the post-dev/post-fewshot pool,
  label-balanced as much as possible.
- **holdout**: Remainder after removing dev + challenge + fewshot_bank.
  These items should not be used during prompt development.

## Multilingual Propagation

- **Amharic (am)**: am_master.csv: covers items 1–744 (744 items); English has 82 additional items beyond this range. Alignment is safe for the shared range. Parallel split files written (items outside range omitted).
- **Igbo (ig)**: ig_master.csv: covers items 1–744 (744 items); English has 82 additional items beyond this range. Alignment is safe for the shared range. Parallel split files written (items outside range omitted).
- **Zulu (zu)**: zu_master.csv: covers items 1–744 (744 items); English has 82 additional items beyond this range. Alignment is safe for the shared range. Parallel split files written (items outside range omitted).
