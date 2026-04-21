#!/usr/bin/env python3
"""
generate_sample100.py
=====================
Generates a stratified 100-row sample for each task/language combination.

Samples are drawn from the master source file for each task/language and are
representative of the full data distribution. This set is intended for rapid,
cost-efficient prompt testing before committing to full-scale evaluation.

Sampling strategy
-----------------
  presuppositions (3 classes: E/N/C)
      Stratified by gold_label: ceil(100/3) from the largest class,
      floor(100/3) from the others. Exact total = 100.

  pronoun_resolution (2 classes: A/B)
      Stratified by gold_answer: 50 A + 50 B = 100.

  lemmatization (open-ended)
      Random 100 rows, skipping any row with empty gold_lemma.

Seed: 100 (distinct from the main 80/10/10 split seed = 42).

Output files (written alongside existing splits in source/inference/full/)
---------------------------------------------------------------------------
  {lang}_sample100.csv                (source — all columns including gold)
  {lang}_sample100_inference.csv      (model-facing — no gold)
  {lang}_sample100_full.csv           (scorer-ready — gold + empty model cols)

Usage
-----
    python srijon-2.0/scripts/generate_sample100.py
"""

import csv
import random
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE        = Path(__file__).resolve().parents[1]   # srijon-2.0/
SEED        = 100
SAMPLE_SIZE = 100


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_csv_file(path: Path) -> tuple[list[str], list[dict]]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    return fieldnames, rows


def write_csv_file(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def stratified_sample(
    rows: list[dict],
    strat_col: str,
    total: int,
    rng: random.Random,
) -> list[dict]:
    """
    Sample `total` rows from `rows`, stratified by `strat_col`.

    Allocation: floor(total / n_classes) per class, remainder distributed
    to the largest classes first. Row order is preserved within each stratum.
    If a class has fewer rows than its allocation, all rows of that class
    are included and the shortfall is filled from the largest remaining class.
    """
    # Group rows by class value, preserving original order
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row[strat_col]].append(row)

    classes = sorted(groups.keys())
    n = len(classes)
    base_alloc = total // n
    remainder  = total % n

    # Give the remainder to the classes with the most rows (most representative)
    sorted_by_size = sorted(classes, key=lambda c: len(groups[c]), reverse=True)
    alloc = {c: base_alloc for c in classes}
    for c in sorted_by_size[:remainder]:
        alloc[c] += 1

    sampled: list[dict] = []
    for cls in classes:
        pool = groups[cls]
        n_take = min(alloc[cls], len(pool))
        if n_take < alloc[cls]:
            print(
                f"    [WARN] class '{cls}' has only {len(pool)} rows "
                f"(wanted {alloc[cls]}) — taking all {n_take}"
            )
        # Sample within the stratum, then sort back to original order
        chosen_indices = sorted(rng.sample(range(len(pool)), n_take))
        sampled.extend(pool[i] for i in chosen_indices)

    # Return in original row order (by position in the input list)
    id_set = {id(r) for r in sampled}
    return [r for r in rows if id(r) in id_set]


def write_trio(
    lang_dir: Path,
    lang: str,
    src_fields: list[str],
    inf_fields: list[str],
    full_extra: list[str],
    sample_rows: list[dict],
) -> None:
    """Write source / inference / full CSV for the sample."""
    full_fields = src_fields + full_extra
    empty = {c: "" for c in full_extra}

    write_csv_file(
        lang_dir / "source"    / f"{lang}_sample100.csv",
        src_fields, sample_rows,
    )
    write_csv_file(
        lang_dir / "inference" / f"{lang}_sample100_inference.csv",
        inf_fields,
        [{c: r[c] for c in inf_fields} for r in sample_rows],
    )
    write_csv_file(
        lang_dir / "full"      / f"{lang}_sample100_full.csv",
        full_fields,
        [{**r, **empty} for r in sample_rows],
    )


# ---------------------------------------------------------------------------
# 1. Presuppositions
# ---------------------------------------------------------------------------

print("=== Presuppositions ===")

PS_LANGS     = ["en", "fr", "de", "hi", "ru", "vi"]
PS_INF_COLS  = ["item_id", "premise", "hypothesis"]
PS_FULL_XTRA = ["model_label", "correct"]

for lang in PS_LANGS:
    rng = random.Random(SEED)
    src_path = BASE / f"presuppositions/{lang}/source/{lang}_master.csv"
    src_fields, src_rows = read_csv_file(src_path)

    sample = stratified_sample(src_rows, "gold_label", SAMPLE_SIZE, rng)

    from collections import Counter
    dist = Counter(r["gold_label"] for r in sample)
    print(f"  {lang}: {len(sample)} rows sampled  dist={dict(dist)}")

    write_trio(
        BASE / f"presuppositions/{lang}", lang,
        src_fields, PS_INF_COLS, PS_FULL_XTRA, sample,
    )


# ---------------------------------------------------------------------------
# 2. Pronoun Resolution
# ---------------------------------------------------------------------------

print("\n=== Pronoun Resolution ===")

PR_LANGS     = ["en", "de", "fr", "ru"]
PR_INF_COLS  = ["item_id", "sentence", "option_a", "option_b"]
PR_FULL_XTRA = ["model_prediction", "correct"]

for lang in PR_LANGS:
    rng = random.Random(SEED)
    src_path = BASE / f"pronoun_resolution/{lang}/source/{lang}_master.csv"
    src_fields, src_rows = read_csv_file(src_path)

    sample = stratified_sample(src_rows, "gold_answer", SAMPLE_SIZE, rng)

    from collections import Counter
    dist = Counter(r["gold_answer"] for r in sample)
    print(f"  {lang}: {len(sample)} rows sampled  dist={dict(dist)}")

    write_trio(
        BASE / f"pronoun_resolution/{lang}", lang,
        src_fields, PR_INF_COLS, PR_FULL_XTRA, sample,
    )


# ---------------------------------------------------------------------------
# 3. Lemmatization
# ---------------------------------------------------------------------------

print("\n=== Lemmatization ===")

rng = random.Random(SEED)
src_path = BASE / "lemmatization/en/source/en_master.csv"
src_fields, src_rows = read_csv_file(src_path)

# Exclude rows with no gold lemma before sampling
eligible = [r for r in src_rows if r["gold_lemma"].strip()]
excluded = len(src_rows) - len(eligible)
if excluded:
    print(f"  [INFO] Excluding {excluded} rows with empty gold_lemma before sampling")

chosen_indices = sorted(rng.sample(range(len(eligible)), SAMPLE_SIZE))
sample = [eligible[i] for i in chosen_indices]

print(f"  en: {len(sample)} rows sampled  (from {len(eligible)} eligible)")

write_trio(
    BASE / "lemmatization/en", "en",
    src_fields, ["item_id", "word"], ["model_lemma", "correct"], sample,
)


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print(f"""
=== Done ===
Generated {SAMPLE_SIZE}-row stratified samples for all task/language combinations.
Seed: {SEED}

Files written per task/language:
  source/{{lang}}_sample100.csv            — all columns including gold label
  inference/{{lang}}_sample100_inference.csv  — model-facing, no gold
  full/{{lang}}_sample100_full.csv         — gold + empty model prediction columns

Sampling strategy:
  presuppositions  → stratified by gold_label (E/N/C)
  pronoun_resolution → stratified by gold_answer (A/B)
  lemmatization    → random (rows with empty gold_lemma excluded)
""")
