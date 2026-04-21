#!/usr/bin/env python3
"""
generate_inference_full.py
==========================
Regenerates inference/ and full/ CSV files from the canonical source/ files
for every language (en, am, ig, zu).

This script is SAFE TO RERUN — it overwrites existing inference/full files
without touching anything in source/.

Usage
-----
    # From the repo root or any directory:
    python pronoun_resolution/mlm_african/scripts/generate_inference_full.py

    # Or from inside mlm_african/scripts/:
    python generate_inference_full.py

What it does
------------
  For each language in {en, am, ig, zu}:
    For each scored split in {dev, challenge, holdout}:
      1. Read  mlm_african/{lang}/source/{lang}_{split}.csv
      2. Validate that all four inference columns are present:
             item_id  |  sentence  |  option_a  |  option_b
      3. Write mlm_african/{lang}/inference/{lang}_{split}_inference.csv
             (contains ONLY the four inference columns, same row order)
      4. Write mlm_african/{lang}/full/{lang}_{split}_full.csv
             (contains ALL columns from source, same row order)

  The fewshot_bank is NOT processed into inference/full — it is an exemplar
  source for prompt construction, not a scored evaluation split.

Output summary
--------------
  A manifest table is printed at the end showing every file written.
"""

import csv
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
AFRICAN_DIR = SCRIPT_DIR.parent

LANGS          = ["en", "am", "ig", "zu"]
SCORED_SPLITS  = ["dev", "challenge", "holdout"]
INFERENCE_COLS = ["item_id", "sentence", "option_a", "option_b"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    """Return (fieldnames, rows) from a CSV file."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    return fieldnames, rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    """Write rows to path using DictWriter."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def main() -> None:
    errors   = []
    manifest = []   # (lang, split, inference_path, full_path, n_rows)

    for lang in LANGS:
        source_dir   = AFRICAN_DIR / lang / "source"
        inf_dir      = AFRICAN_DIR / lang / "inference"
        full_dir     = AFRICAN_DIR / lang / "full"

        for split in SCORED_SPLITS:
            src = source_dir / f"{lang}_{split}.csv"

            if not src.exists():
                print(f"  [SKIP] {src.relative_to(AFRICAN_DIR)} — file not found")
                continue

            fieldnames, rows = read_csv(src)

            # ---- Validate required inference columns ----
            missing = [c for c in INFERENCE_COLS if c not in fieldnames]
            if missing:
                msg = (
                    f"  [ERROR] {src.name} is missing required inference columns: "
                    f"{missing} — skipped. "
                    f"Available columns: {fieldnames}"
                )
                print(msg)
                errors.append(msg)
                continue

            n = len(rows)

            # ---- Inference file (4 columns only) ----
            inf_rows = [{c: r[c] for c in INFERENCE_COLS} for r in rows]
            inf_path = inf_dir / f"{lang}_{split}_inference.csv"
            write_csv(inf_path, INFERENCE_COLS, inf_rows)

            # ---- Full file (all columns) ----
            full_path = full_dir / f"{lang}_{split}_full.csv"
            write_csv(full_path, fieldnames, rows)

            manifest.append((lang, split, inf_path, full_path, n))

    # ---- Print manifest ----
    print()
    print("=" * 70)
    print(" MANIFEST — files written")
    print("=" * 70)
    print(f"  {'LANGUAGE':<6} {'SPLIT':<12} {'ROWS':>5}  INFERENCE / FULL")
    print("-" * 70)
    for lang, split, inf_path, full_path, n in manifest:
        inf_rel  = inf_path.relative_to(AFRICAN_DIR)
        full_rel = full_path.relative_to(AFRICAN_DIR)
        print(f"  {lang:<6} {split:<12} {n:>5}  {inf_rel}")
        print(f"  {'':6} {'':12} {'':5}  {full_rel}")
    print("=" * 70)
    print(f"  Files written: {len(manifest) * 2}")

    if errors:
        print(f"\n  ERRORS ({len(errors)}):")
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print("\n  All files generated successfully.")


if __name__ == "__main__":
    main()
