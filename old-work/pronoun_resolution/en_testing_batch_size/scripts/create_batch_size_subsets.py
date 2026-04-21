"""
create_batch_size_subsets.py
============================
Reproducible subset-generation pipeline for the English-only batch-size
testing experiment (pronoun_resolution/en_testing_batch_size/).

This script:
  1. Auto-detects (or accepts via --input) the canonical English master
     dataset: pronoun_resolution/en_master.csv
  2. Normalizes the data to the canonical internal schema:
       item_id, row_index, source_file, sentence,
       option_a, option_b, gold_answer,
       correct_answer_num, correct_text
  3. Creates NESTED English subsets of sizes 25, 100, 250, and 500 using a
     fixed seed (default 329):
       batch_25  ⊆  batch_100  ⊆  batch_250  ⊆  batch_500
     Label balance is preserved by stratifying on gold_answer (A / B).
  4. Saves:
       data/english_master_normalized.csv
       data/batch_<N>_full.csv        — includes gold labels
       data/batch_<N>_inference.csv   — inference-only (no gold labels)
       data/subset_manifest.csv
       metadata/subset_summary.json
       metadata/subset_summary.md

Usage
-----
    python create_batch_size_subsets.py [OPTIONS]

    --input   optional; path to English master CSV (auto-detected if omitted)
    --seed    random seed for reproducibility          [default: 329]
    --sizes   batch sizes to generate                  [default: 25 100 250 500]
    --outdir  output directory for data files          [default: …/data/]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]
PRONOUN_DIR = REPO_ROOT / "pronoun_resolution"
THIS_DIR = Path(__file__).resolve().parents[1]  # en_testing_batch_size/

# Canonical output locations (relative to THIS_DIR, overrideable via --outdir)
DEFAULT_OUTDIR = THIS_DIR / "data"
DEFAULT_META_DIR = THIS_DIR / "metadata"

# ---------------------------------------------------------------------------
# Schema mapping  en_master.csv → canonical names
# ---------------------------------------------------------------------------

EN_COLUMN_MAP = {
    "item_num": "item_id",
    "sentence": "sentence",
    "option1": "option_a",
    "option2": "option_b",
    "correct_letter": "gold_answer",
}
EN_PASSTHROUGH = ["correct_answer_num", "correct_text"]

# Columns present in the inference-only files (no gold labels)
INFERENCE_COLS = ["item_id", "sentence", "option_a", "option_b"]


# ---------------------------------------------------------------------------
# Auto-detection
# ---------------------------------------------------------------------------

def find_english_master(pronoun_dir: Path) -> Path:
    """Return the path to the English master CSV, exiting loudly if missing."""
    candidate = pronoun_dir / "en_master.csv"
    if candidate.exists():
        return candidate
    # Fallback: first en_*.csv found
    matches = sorted(pronoun_dir.glob("en_*.csv"))
    if not matches:
        sys.exit(
            f"[ERROR] No English master CSV found in {pronoun_dir}.\n"
            "  Expected: en_master.csv\n"
            "  Pass --input to specify the path explicitly."
        )
    print(
        f"[WARNING] en_master.csv not found; using fallback: {matches[0].name}"
    )
    return matches[0]


# ---------------------------------------------------------------------------
# Load & normalize
# ---------------------------------------------------------------------------

def load_and_normalize(path: Path) -> pd.DataFrame:
    """
    Load the English master CSV and return a DataFrame in the canonical schema.

    Canonical schema
    ----------------
    item_id           – stable integer string (from item_num)
    row_index         – 0-based position in the source file
    source_file       – basename of the source file
    sentence          – pronoun-resolution sentence with a blank ('_')
    option_a          – first candidate antecedent
    option_b          – second candidate antecedent
    gold_answer       – uppercase A or B
    correct_answer_num – original numeric label (passthrough)
    correct_text      – text of the correct option (passthrough)
    """
    df = pd.read_csv(path, dtype=str)

    # Verify required columns
    missing = [c for c in EN_COLUMN_MAP if c not in df.columns]
    if missing:
        sys.exit(
            f"[ERROR] Expected columns not found in {path.name}: {missing}\n"
            f"  Available columns: {list(df.columns)}\n"
            "  Check --input or verify the file schema."
        )

    # Rename to canonical names
    df = df.rename(columns=EN_COLUMN_MAP)

    # Strip whitespace from key fields
    for col in ["item_id", "sentence", "option_a", "option_b", "gold_answer"]:
        df[col] = df[col].astype(str).str.strip()

    # Normalize gold_answer to uppercase A / B
    df["gold_answer"] = df["gold_answer"].str.upper()
    bad = df[~df["gold_answer"].isin(["A", "B"])]["gold_answer"].unique()
    if len(bad) > 0:
        sys.exit(
            f"[ERROR] Unexpected gold_answer values (expected A or B): {bad}"
        )

    # Check item_id uniqueness; fall back to row index if needed
    if df["item_id"].nunique() != len(df):
        print(
            "[WARNING] item_id (from item_num) is not unique — "
            "generating row-index-based item_ids."
        )
        df["item_id"] = [str(i + 1) for i in range(len(df))]

    # Add provenance columns
    df["source_file"] = path.name
    df["row_index"] = range(len(df))

    # Canonical column order
    core = ["item_id", "row_index", "source_file", "sentence",
            "option_a", "option_b", "gold_answer"]
    extra = [c for c in EN_PASSTHROUGH if c in df.columns]
    return df[core + extra].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Nested subset generation
# ---------------------------------------------------------------------------

def make_nested_subsets(
    df: pd.DataFrame,
    sizes: list[int],
    seed: int,
) -> dict[int, pd.DataFrame]:
    """
    Build nested subsets of the given sizes, preserving gold-label balance.

    Strategy
    --------
    Sizes are sorted descending; the largest subset is sampled first, and
    each smaller subset is drawn as a prefix of the larger one's label pools,
    so strict nesting is guaranteed:

        batch_25 ⊆ batch_100 ⊆ batch_250 ⊆ batch_500 (for the default sizes)

    Within each label (A, B), items are shuffled with the fixed seed before
    any prefix is taken, so the order is deterministic and independent of the
    input file order.

    Label balance
    -------------
    For each size N, the split is floor(N/2) from label A and ceil(N/2) from
    label B (or perfectly even when N is divisible by 2).  If the requested
    number of items from either label exceeds what is available, the script
    exits loudly.
    """
    sizes_sorted = sorted(sizes, reverse=True)
    largest = sizes_sorted[0]

    # Separate by label and shuffle deterministically
    a_items = (
        df[df["gold_answer"] == "A"]
        .sample(frac=1, random_state=seed)
        .reset_index(drop=True)
    )
    b_items = (
        df[df["gold_answer"] == "B"]
        .sample(frac=1, random_state=seed)
        .reset_index(drop=True)
    )

    # How many A / B items we need for the largest subset
    n_a_needed = largest // 2
    n_b_needed = largest - n_a_needed  # handles odd sizes

    if len(a_items) < n_a_needed:
        sys.exit(
            f"[ERROR] Requested {n_a_needed} label-A items for batch_{largest} "
            f"but only {len(a_items)} available in the master dataset."
        )
    if len(b_items) < n_b_needed:
        sys.exit(
            f"[ERROR] Requested {n_b_needed} label-B items for batch_{largest} "
            f"but only {len(b_items)} available in the master dataset."
        )

    # Pool: fixed shuffled sequences from which all subsets are carved
    pool_a = a_items.iloc[:n_a_needed].copy()
    pool_b = b_items.iloc[:n_b_needed].copy()

    subsets: dict[int, pd.DataFrame] = {}
    for size in sizes_sorted:
        n_a = size // 2
        n_b = size - n_a
        sub_a = pool_a.iloc[:n_a]
        sub_b = pool_b.iloc[:n_b]
        combined = pd.concat([sub_a, sub_b])
        # Sort by original row_index to restore a sensible natural order
        combined = combined.sort_values("row_index").reset_index(drop=True)
        subsets[size] = combined

    return subsets


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_nesting(subsets: dict[int, pd.DataFrame]) -> None:
    """Assert that each smaller subset is a strict subset of every larger one."""
    sizes = sorted(subsets.keys())
    for i in range(len(sizes) - 1):
        small_ids = set(subsets[sizes[i]]["item_id"])
        large_ids = set(subsets[sizes[i + 1]]["item_id"])
        if not small_ids.issubset(large_ids):
            diff = small_ids - large_ids
            sys.exit(
                f"[ERROR] Nesting violation: batch_{sizes[i]} has {len(diff)} "
                f"item_ids NOT present in batch_{sizes[i+1]}: "
                f"{sorted(diff)[:5]} …"
            )
    print("  Nesting verified: batch_25 ⊆ … ⊆ batch_500  OK")


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

def write_subsets(
    subsets: dict[int, pd.DataFrame],
    outdir: Path,
) -> None:
    """Write full (gold-bearing) and inference-only CSVs for each subset."""
    for size, df in subsets.items():
        # Full file — includes gold labels and all metadata columns
        full_path = outdir / f"batch_{size}_full.csv"
        df.to_csv(full_path, index=False)
        print(f"  [data] batch_{size}_full.csv      → {full_path}")

        # Inference-only file — strips gold labels
        infer_path = outdir / f"batch_{size}_inference.csv"
        df[INFERENCE_COLS].to_csv(infer_path, index=False)
        print(f"  [data] batch_{size}_inference.csv → {infer_path}")


def write_manifest(
    subsets: dict[int, pd.DataFrame],
    outdir: Path,
) -> None:
    """Write subset_manifest.csv: one row per (item_id, batch_size) pair."""
    rows = []
    for size, df in subsets.items():
        for _, row in df.iterrows():
            rows.append({
                "item_id": row["item_id"],
                "batch_size": size,
                "gold_answer": row["gold_answer"],
                "row_index": row["row_index"],
            })
    manifest = pd.DataFrame(rows).sort_values(["batch_size", "row_index"])
    path = outdir / "subset_manifest.csv"
    manifest.to_csv(path, index=False)
    print(f"  [data] subset_manifest.csv        → {path}")


def write_metadata(
    subsets: dict[int, pd.DataFrame],
    meta_dir: Path,
    input_path: Path,
    seed: int,
    sizes: list[int],
) -> None:
    """Write subset_summary.json and subset_summary.md."""
    sizes_sorted = sorted(sizes)

    summary = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source_file": input_path.name,
        "source_path": str(input_path),
        "seed": seed,
        "sizes": sizes_sorted,
        "nesting": " ⊆ ".join(f"batch_{s}" for s in sizes_sorted),
        "subsets": {},
        "schema_notes": {
            "item_id": (
                "Preserved from item_num in en_master.csv. "
                "Unique integer string, stable across runs."
            ),
            "gold_answer": "Uppercase A or B (from correct_letter).",
            "option_a / option_b": "Mapped from option1 / option2.",
            "inference_cols": INFERENCE_COLS,
            "nesting_strategy": (
                "Items are drawn as label-balanced prefixes from a single "
                "deterministically shuffled pool, ensuring strict nesting."
            ),
            "label_balance": (
                "Each subset is split as floor(N/2) label-A items and "
                "ceil(N/2) label-B items."
            ),
        },
    }

    for size, df in subsets.items():
        lc = df["gold_answer"].value_counts().to_dict()
        summary["subsets"][f"batch_{size}"] = {
            "n": len(df),
            "label_A": lc.get("A", 0),
            "label_B": lc.get("B", 0),
            "label_balance_ratio": round(
                lc.get("A", 0) / len(df), 4
            ) if len(df) > 0 else None,
        }

    with open(meta_dir / "subset_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"  [meta] subset_summary.json        → {meta_dir / 'subset_summary.json'}")

    # ---- Markdown -------------------------------------------------------
    table_rows = ""
    for size in sizes_sorted:
        d = summary["subsets"][f"batch_{size}"]
        table_rows += (
            f"| batch_{size} | {d['n']} | {d['label_A']} | {d['label_B']} "
            f"| {d['label_balance_ratio']:.4f} |\n"
        )

    # Nesting assertions
    nest_lines = ""
    for i in range(len(sizes_sorted) - 1):
        nest_lines += (
            f"- `batch_{sizes_sorted[i]}` ⊆ `batch_{sizes_sorted[i+1]}`: "
            "verified\n"
        )

    md = f"""# Batch-Size Subset Summary

## Source Data

- **English master file**: `{input_path.name}`
- **Full path**: `{input_path}`
- **Random seed**: {seed}
- **Generated**: {summary['generated_at']}

## Subset Sizes and Label Balance

| Subset | N | Label A | Label B | A fraction |
|--------|---|---------|---------|------------|
{table_rows}
## Nesting Relationships

{nest_lines}
## Schema Decisions

- **item_id**: Preserved from `item_num` in the source file. Unique and stable.
- **gold_answer**: Normalised to uppercase `A` or `B` (from `correct_letter`).
- **option_a / option_b**: Mapped from `option1` / `option2`.

## Subset Construction

Items are drawn as label-balanced **prefixes** from a single deterministically
shuffled pool for each label (A and B).  The shuffle uses seed `{seed}` via
`pandas.DataFrame.sample(random_state={seed})`.

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

1. The canonical English master is `pronoun_resolution/en_master.csv`.
2. The file uses the schema: `item_num, sentence, option1, option2,
   correct_answer_num, correct_letter, correct_text`.
3. `item_num` is unique and serves as the stable item identifier.
4. All gold labels are exactly `A` or `B` (after upper-casing `correct_letter`).
"""

    with open(meta_dir / "subset_summary.md", "w", encoding="utf-8") as f:
        f.write(md)
    print(f"  [meta] subset_summary.md          → {meta_dir / 'subset_summary.md'}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate reproducible, nested English batch-size subsets "
            "for pronoun-resolution experiments."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Path to English master CSV (auto-detected if omitted).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=329,
        help="Random seed for reproducibility.",
    )
    parser.add_argument(
        "--sizes",
        type=int,
        nargs="+",
        default=[25, 100, 250, 500],
        help="Batch sizes to generate.",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=DEFAULT_OUTDIR,
        help="Output directory for data files.",
    )
    parser.add_argument(
        "--metadata-dir",
        type=Path,
        default=DEFAULT_META_DIR,
        help="Output directory for metadata files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Resolve input
    input_path = args.input or find_english_master(PRONOUN_DIR)
    input_path = Path(input_path).resolve()
    print(f"\n[INFO] English master dataset : {input_path}")
    print(f"[INFO] Seed                   : {args.seed}")
    print(f"[INFO] Batch sizes            : {sorted(args.sizes)}")

    # Create output directories
    args.outdir.mkdir(parents=True, exist_ok=True)
    args.metadata_dir.mkdir(parents=True, exist_ok=True)

    # Load and normalize
    print("\n[INFO] Loading and normalising …")
    df = load_and_normalize(input_path)
    print(f"       {len(df)} items loaded.")
    lc = df["gold_answer"].value_counts().to_dict()
    print(f"       Label distribution: A={lc.get('A', 0)}, B={lc.get('B', 0)}")

    # Write normalized master
    norm_path = args.outdir / "english_master_normalized.csv"
    df.to_csv(norm_path, index=False)
    print(f"       Normalized master written → {norm_path}")

    # Generate nested subsets
    print("\n[INFO] Generating nested subsets …")
    subsets = make_nested_subsets(df, args.sizes, args.seed)

    # Verify nesting
    print("\n[INFO] Verifying nesting …")
    verify_nesting(subsets)

    # Write files
    print("\n[INFO] Writing data files …")
    write_subsets(subsets, args.outdir)
    write_manifest(subsets, args.outdir)

    # Write metadata
    print("\n[INFO] Writing metadata …")
    write_metadata(subsets, args.metadata_dir, input_path, args.seed, args.sizes)

    # Summary
    print("\n=== Subset Summary ===")
    for size in sorted(subsets.keys()):
        sub = subsets[size]
        lc2 = sub["gold_answer"].value_counts().to_dict()
        print(
            f"  batch_{size:<5}  n={len(sub):>3}   "
            f"A={lc2.get('A', 0):>3}  B={lc2.get('B', 0):>3}"
        )

    print("\n[DONE] Subset generation complete.")


if __name__ == "__main__":
    main()
