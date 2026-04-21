# Split Strategy

No train/dev/test split has been applied to any srijon-2.0 dataset. All files are
currently exported as `_master` (full dataset). This document specifies the recommended
split plan for future evaluation work.

---

## Current state

All output files follow the naming pattern:
- `{lang}_master.csv` (source)
- `{lang}_master_inference.csv` (inference)
- `{lang}_master_full.csv` (full / scorer)

These contain 100% of the available rows with no holdout.

---

## Recommended split plan

When splitting is needed for evaluation, use a **80 / 10 / 10** train/dev/test split.

### Parameters

| Parameter | Value |
|-----------|-------|
| Random seed | `42` |
| Train fraction | 0.80 |
| Dev fraction | 0.10 |
| Test fraction | 0.10 |
| Stratification | None (simple random split) |
| Row order | Preserved within each split |

Stratification is not applied because:
1. Gold labels are not present in source files to stratify by.
2. XNLI and WinoGrande are already balanced by design.

If gold labels are joined before splitting, consider stratifying by `gold_label` for
the presuppositions task.

### Naming convention after splitting

Replace `_master` with `_train`, `_dev`, `_test`:

```
{lang}_train.csv            {lang}_train_inference.csv      {lang}_train_full.csv
{lang}_dev.csv              {lang}_dev_inference.csv        {lang}_dev_full.csv
{lang}_test.csv             {lang}_test_inference.csv       {lang}_test_full.csv
```

### Reference split sizes (approximate)

#### Pronoun Resolution

| Language | Total | Train (~80%) | Dev (~10%) | Test (~10%) |
|----------|-------|-------------|-----------|------------|
| en | 10,234 | 8,187 | 1,023 | 1,024 |
| fr | 2,793 | 2,234 | 280 | 279 |
| de | 5,835 | 4,668 | 584 | 583 |
| ru | 1,487 | 1,190 | 148 | 149 |

#### Presuppositions

| Language | Total | Train (~80%) | Dev (~10%) | Test (~10%) |
|----------|-------|-------------|-----------|------------|
| en | 6,981 | 5,585 | 698 | 698 |
| fr | 5,010 | 4,008 | 501 | 501 |
| de | 5,010 | 4,008 | 501 | 501 |
| hi | 5,010 | 4,008 | 501 | 501 |
| ru | 5,010 | 4,008 | 501 | 501 |
| vi | 5,010 | 4,008 | 501 | 501 |

#### Lemmatization

| Language | Total | Train (~80%) | Dev (~10%) | Test (~10%) |
|----------|-------|-------------|-----------|------------|
| en | 115,523 | 92,418 | 11,552 | 11,553 |

---

## Splitting script skeleton

```python
import pandas as pd
from sklearn.model_selection import train_test_split

SEED = 42

def split_and_write(source_path: str, lang: str, task_dir: str) -> None:
    df = pd.read_csv(source_path)
    train, temp = train_test_split(df, test_size=0.20, random_state=SEED)
    dev, test   = train_test_split(temp, test_size=0.50, random_state=SEED)

    for split_name, split_df in [("train", train), ("dev", dev), ("test", test)]:
        split_df.to_csv(f"{task_dir}/{lang}/source/{lang}_{split_name}.csv", index=False)
        # write inference / full variants similarly
```

---

## Notes

- Keep `_master` files intact after splitting; splits are derived artifacts.
- The `item_id` column uniquely identifies each row — use it to map predictions back
  to source rows regardless of split boundaries.
- Wino-X (FR/DE/RU) and WinoGrande (EN) are drawn from paired sentence sets.
  If sentence-pair integrity matters, split at the pair level rather than the row level.
  Paired rows in the source file are typically adjacent (rows i and i+1 share entities
  but have opposite correct answers).
