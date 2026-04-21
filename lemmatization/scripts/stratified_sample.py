"""
stratified_sample.py
--------------------
Reads output.csv (columns: form, lemma) produced by extract_lemmas.py,
assigns each token to one or more hardness subgroups, then draws
stratified samples of 100, 200, and 300 rows with equal subgroup splits.

Subgroups
---------
  irregular   : form and lemma share fewer than 3 leading characters
                (e.g. went->go, was->be, better->good)
  changed     : form != lemma after lowercasing (any morphological change)
  ambiguous   : same surface form maps to 2+ different lemmas in the data
  rare        : lemma appears in the bottom 10% by frequency
  easy        : none of the above (form == lemma, unambiguous, common)

Sampling logic
--------------
  For a target size N, each subgroup gets floor(N / n_subgroups) rows.
  Remainder rows (N % n_subgroups) are filled from the largest subgroups.
  Rows that belong to multiple subgroups are assigned to their
  highest-priority subgroup (irregular > ambiguous > rare > changed > easy)
  so every row appears exactly once per sample.

Outputs
-------
  hard_examples.csv          all non-easy rows tagged by subgroup
  output_tagged.csv          full data with subgroup boolean columns + label
  sample_100_stratified.csv
  sample_200_stratified.csv
  sample_300_stratified.csv
"""

import os
import sys
import random
import pandas as pd
from collections import Counter

# ── config ────────────────────────────────────────────────────────────────────
SEED         = 42
SAMPLE_SIZES = [100, 200, 300]
INPUT_CSV    = "output.csv"        # change path if needed

# subgroup priority order (first match wins for the label column)
PRIORITY = ["irregular", "ambiguous", "rare", "changed", "easy"]


# ── helpers ───────────────────────────────────────────────────────────────────

def shared_prefix_len(a: str, b: str) -> int:
    count = 0
    for x, y in zip(a, b):
        if x == y:
            count += 1
        else:
            break
    return count


def tag_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Add boolean subgroup columns and a priority 'subgroup' label."""

    # 1. irregular: fewer than 3 leading chars in common
    df["irregular"] = df.apply(
        lambda r: shared_prefix_len(r["form"].lower(), r["lemma"].lower()) < 3,
        axis=1
    )

    # 2. changed: any difference after lowercasing
    df["changed"] = df["form"].str.lower() != df["lemma"].str.lower()

    # 3. ambiguous: same surface form -> 2+ distinct lemmas in the dataset
    form_lemma_counts = df.groupby("form")["lemma"].nunique()
    ambiguous_forms   = form_lemma_counts[form_lemma_counts > 1].index
    df["ambiguous"]   = df["form"].isin(ambiguous_forms)

    # 4. rare: lemma in the bottom 10% by frequency
    lemma_counts = Counter(df["lemma"])
    freq_threshold = sorted(lemma_counts.values())[
        max(0, int(len(lemma_counts) * 0.10) - 1)
    ]
    rare_lemmas  = {l for l, c in lemma_counts.items() if c <= freq_threshold}
    df["rare"]   = df["lemma"].isin(rare_lemmas)

    # 5. easy: none of the above
    df["easy"] = ~df[["irregular", "ambiguous", "rare", "changed"]].any(axis=1)

    # priority label
    def assign_label(row):
        for g in PRIORITY:
            if row[g]:
                return g
        return "easy"

    df["subgroup"] = df.apply(assign_label, axis=1)
    return df


def stratified_sample(df: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    """
    Draw exactly n rows with equal subgroup representation.
    Uses the priority 'subgroup' column so each row belongs to one group.
    """
    groups     = df.groupby("subgroup")
    n_groups   = len(groups)
    base_size  = n // n_groups
    remainder  = n % n_groups

    # sort groups largest-first to allocate remainder fairly
    group_sizes = groups.size().sort_values(ascending=False)
    frames = []

    for i, (name, size) in enumerate(group_sizes.items()):
        alloc = base_size + (1 if i < remainder else 0)
        group_df = df[df["subgroup"] == name]

        if len(group_df) < alloc:
            print(f"  WARNING: subgroup '{name}' has only {len(group_df)} rows "
                  f"but needs {alloc}. Taking all available.")
            frames.append(group_df)
        else:
            frames.append(group_df.sample(n=alloc, random_state=seed))

    result = pd.concat(frames).sample(frac=1, random_state=seed)  # shuffle
    return result.reset_index(drop=True)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"ERROR: '{INPUT_CSV}' not found. Run extract_lemmas.py first.")
        sys.exit(1)

    print(f"Loading {INPUT_CSV} ...")
    df = pd.read_csv(INPUT_CSV)

    if not {"form", "lemma"}.issubset(df.columns):
        print("ERROR: CSV must have 'form' and 'lemma' columns.")
        sys.exit(1)

    # drop rows where form or lemma is NaN/empty (malformed CSV lines)
    before = len(df)
    df = df.dropna(subset=["form", "lemma"])
    df["form"]  = df["form"].astype(str).str.strip()
    df["lemma"] = df["lemma"].astype(str).str.strip()
    df = df[(df["form"] != "") & (df["lemma"] != "")]
    dropped = before - len(df)
    if dropped:
        print(f"  Dropped {dropped} malformed rows (empty form or lemma)")

    print(f"Total rows: {len(df):,}\n")

    # tag every row
    df = tag_rows(df)

    # ── summary ───────────────────────────────────────────────────────────────
    print("Subgroup distribution (priority label):")
    counts = df["subgroup"].value_counts()
    for g in PRIORITY:
        n = counts.get(g, 0)
        print(f"  {g:12s}  {n:7,}  ({100*n/len(df):.1f}%)")

    print()

    # ── save tagged full data ─────────────────────────────────────────────────
    df.to_csv("output_tagged.csv", index=False)
    print("Saved output_tagged.csv")

    hard = df[df["subgroup"] != "easy"]
    hard.to_csv("hard_examples.csv", index=False)
    print(f"Saved hard_examples.csv  ({len(hard):,} rows)\n")

    # ── stratified samples ────────────────────────────────────────────────────
    for n in SAMPLE_SIZES:
        sample = stratified_sample(df, n, seed=SEED)
        out    = f"sample_{n}_stratified.csv"
        sample.to_csv(out, index=False)

        print(f"sample_{n}_stratified.csv  (total={len(sample)})")
        breakdown = sample["subgroup"].value_counts()
        for g in PRIORITY:
            print(f"    {g:12s}  {breakdown.get(g, 0):4d}")
        print()


if __name__ == "__main__":
    main()