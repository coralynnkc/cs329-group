"""
generate_splits.py
==================
Reproducible split-generation pipeline for the African-language pronoun-
resolution benchmark in `pronoun_resolution/mlm_african/`.

Given the English master dataset (`mlm_african/data/en_master.csv`), this script:
  1. Normalizes the data to a canonical internal schema.
  2. Assigns stable item IDs (using the existing item_num when available,
     otherwise a deterministic SHA-256 hash of content).
  3. Computes a difficulty proxy score from surface features.
  4. Produces five disjoint output splits:
       fewshot_bank  – exemplars for few-shot prompts (never scored)
       dev           – primary evaluation set, stratified
       challenge     – harder stress-test subset
       holdout       – held-out items for final prompt selection
       english_master_normalized – full normalized file for reference
  5. Writes a split manifest and summary artefacts.
  6. Optionally propagates the split indices to aligned multilingual files.

Usage
-----
    python generate_splits.py [OPTIONS]

    --input             Path to English master CSV (auto-detected if omitted)
    --outdir            Output directory for English split CSVs
                        [default: mlm_african/en/source/]
    --metadata-dir      Output directory for metadata
                        [default: mlm_african/metadata/]
    --seed              Random seed for reproducibility   [default: 329]
    --dev-size          Number of items in dev split      [default: 100]
    --challenge-size    Number of items in challenge split [default: 50]
    --fewshot-bank-size Number of exemplars in few-shot bank [default: 8]
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]
PRONOUN_DIR = REPO_ROOT / "pronoun_resolution"
AFRICAN_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = AFRICAN_DIR / "data"
LEGACY_RAW_DIR = PRONOUN_DIR
EN_SOURCE_DIR = AFRICAN_DIR / "en" / "source"

# Schema mapping from en_master.csv column names → internal canonical names
EN_COLUMN_MAP = {
    "item_num": "item_id",
    "sentence": "sentence",
    "option1": "option_a",
    "option2": "option_b",
    "correct_letter": "gold_answer",
}

# Columns to keep from the source file but not rename
EN_PASSTHROUGH_COLS = ["correct_answer_num", "correct_text"]

# Multilingual file prefixes and their language codes
MULTILINGUAL_PREFIXES = {
    "am": "Amharic",
    "ig": "Igbo",
    "zu": "Zulu",
}

# ---------------------------------------------------------------------------
# Auto-detection
# ---------------------------------------------------------------------------

def find_english_master(raw_data_dir: Path) -> Path:
    """Return the path to the English master CSV, raising if not found."""
    candidate = raw_data_dir / "en_master.csv"
    if candidate.exists():
        return candidate

    legacy_candidate = LEGACY_RAW_DIR / "en_master.csv"
    if legacy_candidate.exists():
        print(
            f"[WARNING] Using legacy raw-data location: {legacy_candidate}. "
            "Move the file into pronoun_resolution/mlm_african/data/ to keep "
            "the repo layout consistent."
        )
        return legacy_candidate

    # Fallback: search for any file starting with 'en_' in the new data dir,
    # then in the legacy repo root.
    matches = list(raw_data_dir.glob("en_*.csv"))
    if not matches:
        matches = list(LEGACY_RAW_DIR.glob("en_*.csv"))
    if not matches:
        sys.exit(
            f"[ERROR] Could not find English master CSV in {raw_data_dir}. "
            "Pass --input explicitly."
        )
    return sorted(matches)[0]


# ---------------------------------------------------------------------------
# Loading & normalisation
# ---------------------------------------------------------------------------

def load_and_normalize(path: Path) -> pd.DataFrame:
    """
    Load the English master CSV and return a normalized DataFrame with the
    canonical internal schema plus passthrough columns.
    """
    df = pd.read_csv(path, dtype=str)

    # Validate that all required source columns are present
    missing = [c for c in EN_COLUMN_MAP if c not in df.columns]
    if missing:
        sys.exit(
            f"[ERROR] Expected columns not found in {path.name}: {missing}\n"
            f"  Available columns: {list(df.columns)}"
        )

    # Rename to canonical names
    df = df.rename(columns=EN_COLUMN_MAP)

    # Coerce and strip whitespace
    for col in ["item_id", "sentence", "option_a", "option_b", "gold_answer"]:
        df[col] = df[col].astype(str).str.strip()

    # Normalise gold_answer to uppercase A/B
    df["gold_answer"] = df["gold_answer"].str.upper()
    invalid_labels = df[~df["gold_answer"].isin(["A", "B"])]["gold_answer"].unique()
    if len(invalid_labels) > 0:
        sys.exit(
            f"[ERROR] Unexpected gold_answer values (expected A or B): {invalid_labels}"
        )

    # Add provenance columns
    df["source_file"] = path.name
    df["row_index"] = range(len(df))

    # If item_id is not unique (shouldn't happen), fall back to a content hash
    if df["item_id"].nunique() != len(df):
        print(
            "[WARNING] item_num is not unique — generating content-hash item_ids instead."
        )
        df["item_id"] = df.apply(_content_hash, axis=1)
    else:
        # Keep item_num as-is (already a stable integer string); also record hash for reference
        pass  # item_id already set from item_num

    # Reorder columns for clarity
    core_cols = [
        "item_id", "row_index", "source_file",
        "sentence", "option_a", "option_b", "gold_answer",
    ]
    extra_cols = [c for c in EN_PASSTHROUGH_COLS if c in df.columns]
    df = df[core_cols + extra_cols]

    return df


def _content_hash(row: pd.Series) -> str:
    """
    Deterministic SHA-256 hash of the four canonical content fields.
    Identical inputs always produce the same ID, independent of row order.
    """
    payload = "\t".join([
        row["sentence"].lower().strip(),
        row["option_a"].lower().strip(),
        row["option_b"].lower().strip(),
        row["gold_answer"].upper().strip(),
    ])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Difficulty proxy
# ---------------------------------------------------------------------------

def compute_difficulty(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute a simple, transparent difficulty proxy score for each item.

    Features (all derived from the English sentence text):

      feat_token_len       – whitespace-token count of the sentence
      feat_clause_markers  – count of commas, semicolons, em-dashes, parentheses
      feat_blank_distance  – mean token distance from '_' to each candidate mention
                             (if blank token and both candidates are findable,
                              otherwise NaN and excluded from score)

    The composite score is a normalised (0–1) sum of the three components.
    Higher score → harder item.

    The approach is documented here so prompt-engineering decisions can be traced
    back to these concrete features.
    """
    df = df.copy()

    sentences = df["sentence"].tolist()
    option_as = df["option_a"].tolist()
    option_bs = df["option_b"].tolist()

    tok_lens, clause_counts, blank_dists = [], [], []

    for sent, oa, ob in zip(sentences, option_as, option_bs):
        tokens = sent.split()
        tok_lens.append(len(tokens))

        # Count clause-boundary punctuation
        clause_count = sum(
            sent.count(ch)
            for ch in [",", ";", "—", "–", "(", ")"]
        )
        clause_counts.append(clause_count)

        # Token distance from blank to candidate tokens (lower-cased for matching)
        blank_idx = next(
            (i for i, t in enumerate(tokens) if "_" in t), None
        )
        dist = _candidate_blank_distance(tokens, blank_idx, oa, ob)
        blank_dists.append(dist)

    df["feat_token_len"] = tok_lens
    df["feat_clause_markers"] = clause_counts
    df["feat_blank_distance"] = blank_dists

    # Normalise each feature to [0, 1] min-max; NaN in blank_distance treated as 0
    def _minmax(series: pd.Series) -> pd.Series:
        lo, hi = series.min(), series.max()
        if hi == lo:
            return pd.Series(0.0, index=series.index)
        return (series - lo) / (hi - lo)

    norm_len = _minmax(df["feat_token_len"])
    norm_clause = _minmax(df["feat_clause_markers"])

    bd_series = df["feat_blank_distance"].copy()
    has_dist = bd_series.notna()
    norm_dist = pd.Series(0.0, index=df.index)
    if has_dist.any():
        norm_dist[has_dist] = _minmax(bd_series[has_dist])

    # Weight: length 0.4, clause 0.3, distance 0.3
    # If distance is unavailable for an item, redistribute weight to length + clause
    weights = pd.Series(0.0, index=df.index)
    for i in df.index:
        if has_dist[i]:
            weights[i] = 0.4 * norm_len[i] + 0.3 * norm_clause[i] + 0.3 * norm_dist[i]
        else:
            weights[i] = 0.57 * norm_len[i] + 0.43 * norm_clause[i]

    df["difficulty_score"] = weights.round(4)
    return df


def _candidate_blank_distance(tokens, blank_idx, oa, ob):
    """
    Return the mean token distance between the blank position and the nearest
    token matching each candidate. Returns None if blank or either candidate
    cannot be located robustly.
    """
    if blank_idx is None:
        return None

    def _find_nearest(tokens, target, blank_idx):
        target_tokens = target.lower().split()
        first_tok = target_tokens[0] if target_tokens else ""
        # Find all positions where this token appears before the blank
        positions = [
            i for i, t in enumerate(tokens)
            if t.lower().rstrip(".,;:!?)'\"") == first_tok and i != blank_idx
        ]
        if not positions:
            return None
        return min(abs(blank_idx - p) for p in positions)

    da = _find_nearest(tokens, oa, blank_idx)
    db = _find_nearest(tokens, ob, blank_idx)

    if da is None or db is None:
        return None

    return float((da + db) / 2)


# ---------------------------------------------------------------------------
# Stratification helpers
# ---------------------------------------------------------------------------

def length_bin(tok_len: int) -> str:
    """Assign a coarse sentence-length bin label."""
    if tok_len <= 15:
        return "short"
    elif tok_len <= 22:
        return "medium"
    else:
        return "long"


# ---------------------------------------------------------------------------
# Split logic
# ---------------------------------------------------------------------------

def make_splits(
    df: pd.DataFrame,
    seed: int,
    dev_size: int,
    challenge_size: int,
    fewshot_bank_size: int,
) -> dict[str, pd.DataFrame]:
    """
    Produce disjoint splits from the normalized+enriched DataFrame.

    Returns a dict with keys:
        fewshot_bank, dev, challenge, holdout
    """
    rng = np.random.default_rng(seed)

    total = len(df)
    required = fewshot_bank_size + dev_size + challenge_size
    if required > total:
        sys.exit(
            f"[ERROR] Requested sizes sum to {required}, but only {total} items available. "
            "Reduce --dev-size, --challenge-size, or --fewshot-bank-size."
        )

    # ---- Step 1: carve out few-shot bank ------------------------------------
    # Prefer medium-length, low-difficulty (clean) items, balanced by gold label
    df_sorted_easy = df.sort_values("difficulty_score", ascending=True)

    fewshot_rows = []
    target_per_label = fewshot_bank_size // 2
    for label in ["A", "B"]:
        pool = df_sorted_easy[df_sorted_easy["gold_answer"] == label]
        # Prefer medium-length items from the easy end
        pool_medium = pool[pool["feat_token_len"].apply(length_bin) == "medium"]
        if len(pool_medium) >= target_per_label:
            chosen = pool_medium.head(target_per_label)
        else:
            chosen = pool.head(target_per_label)
        fewshot_rows.append(chosen)

    # Handle odd fewshot_bank_size
    if fewshot_bank_size % 2 == 1:
        leftover_pool = df_sorted_easy[
            ~df_sorted_easy["item_id"].isin(
                pd.concat(fewshot_rows)["item_id"]
            )
        ]
        fewshot_rows.append(leftover_pool.head(1))

    fewshot_bank = pd.concat(fewshot_rows).drop_duplicates("item_id")
    remaining = df[~df["item_id"].isin(fewshot_bank["item_id"])].copy()

    # ---- Step 2: stratified dev set ----------------------------------------
    # Stratify on (gold_answer × length_bin)
    remaining["_len_bin"] = remaining["feat_token_len"].apply(length_bin)

    strata = remaining.groupby(["gold_answer", "_len_bin"], group_keys=False)
    n_strata = remaining[["gold_answer", "_len_bin"]].drop_duplicates().shape[0]
    base_per_stratum = dev_size // n_strata
    remainder_count = dev_size % n_strata

    dev_rows = []
    leftover_counts = {}

    for (label, lbin), group in strata:
        take = base_per_stratum
        g_shuffled = group.sample(frac=1, random_state=int(seed)).reset_index(drop=True)
        dev_rows.append(g_shuffled.iloc[:take])
        leftover_counts[(label, lbin)] = len(g_shuffled) - take

    # Top-up to exact dev_size by drawing extra rows from the largest strata
    dev_so_far = pd.concat(dev_rows)
    top_up_needed = dev_size - len(dev_so_far)

    if top_up_needed > 0:
        already_chosen = set(dev_so_far["item_id"])
        candidates = remaining[~remaining["item_id"].isin(already_chosen)]
        # Balance labels in top-up
        extra_rows = []
        for label in ["A", "B"]:
            n_take = top_up_needed // 2
            pool = candidates[candidates["gold_answer"] == label]
            pool = pool.sample(frac=1, random_state=int(seed)).reset_index(drop=True)
            extra_rows.append(pool.iloc[:n_take])
        if top_up_needed % 2 == 1:
            leftover_pool = candidates[~candidates["item_id"].isin(
                pd.concat(extra_rows)["item_id"]
            )]
            extra_rows.append(leftover_pool.iloc[:1])
        dev_so_far = pd.concat([dev_so_far] + extra_rows)

    dev = dev_so_far.head(dev_size).copy()

    remaining2 = remaining[~remaining["item_id"].isin(dev["item_id"])].copy()

    # ---- Step 3: challenge set (hardest items, label-balanced) --------------
    remaining2_sorted = remaining2.sort_values("difficulty_score", ascending=False)

    challenge_rows = []
    per_label = challenge_size // 2
    for label in ["A", "B"]:
        pool = remaining2_sorted[remaining2_sorted["gold_answer"] == label]
        challenge_rows.append(pool.iloc[:per_label])

    if challenge_size % 2 == 1:
        used_ids = pd.concat(challenge_rows)["item_id"]
        extra = remaining2_sorted[~remaining2_sorted["item_id"].isin(used_ids)].iloc[:1]
        challenge_rows.append(extra)

    challenge = pd.concat(challenge_rows).drop_duplicates("item_id")

    # ---- Step 4: holdout is whatever is left --------------------------------
    used_ids = set(fewshot_bank["item_id"]) | set(dev["item_id"]) | set(challenge["item_id"])
    holdout = df[~df["item_id"].isin(used_ids)].copy()

    # Clean up temporary column
    for split_df in [dev, challenge, holdout, remaining2]:
        if "_len_bin" in split_df.columns:
            split_df.drop(columns=["_len_bin"], inplace=True)
    if "_len_bin" in remaining.columns:
        remaining.drop(columns=["_len_bin"], inplace=True)

    return {
        "fewshot_bank": fewshot_bank,
        "dev": dev,
        "challenge": challenge,
        "holdout": holdout,
    }


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_splits(splits: dict[str, pd.DataFrame], total: int) -> None:
    """
    Hard-fail on any integrity violation; print a concise summary.
    """
    all_ids = []
    for name, sdf in splits.items():
        all_ids.extend(sdf["item_id"].tolist())

    # Disjointness
    from collections import Counter
    dup_ids = [iid for iid, cnt in Counter(all_ids).items() if cnt > 1]
    if dup_ids:
        sys.exit(
            f"[ERROR] Split overlap detected — {len(dup_ids)} item_ids appear in multiple splits: "
            f"{dup_ids[:5]}..."
        )

    # Coverage
    assigned = len(all_ids)
    if assigned != total:
        sys.exit(
            f"[ERROR] {assigned} items assigned across splits but input had {total}. "
            "Some items are missing."
        )

    print("\n=== Split Validation ===")
    for name, sdf in splits.items():
        label_counts = sdf["gold_answer"].value_counts().to_dict()
        print(
            f"  {name:<20} n={len(sdf):>4}   "
            f"A={label_counts.get('A', 0):>3}  B={label_counts.get('B', 0):>3}"
        )

    print(f"\n  Total items covered: {assigned} / {total}")
    print("  All splits disjoint: OK")


# ---------------------------------------------------------------------------
# Multilingual propagation
# ---------------------------------------------------------------------------

def propagate_multilingual(
    splits: dict[str, pd.DataFrame],
    raw_data_dir: Path,
    african_dir: Path,
) -> dict[str, str]:
    """
    For each aligned multilingual master file, write parallel split CSVs.

    Returns a dict mapping language code → alignment status note.
    """
    notes = {}
    for lang_code, lang_name in MULTILINGUAL_PREFIXES.items():
        src = raw_data_dir / f"{lang_code}_master.csv"
        if not src.exists():
            src = LEGACY_RAW_DIR / f"{lang_code}_master.csv"
        if not src.exists():
            notes[lang_code] = f"Source file {src.name} not found — skipped."
            continue

        try:
            lang_df = pd.read_csv(src, dtype=str)
        except Exception as exc:
            notes[lang_code] = f"Could not read {src.name}: {exc} — skipped."
            continue

        if "item_num" not in lang_df.columns:
            notes[lang_code] = (
                f"{src.name} has no item_num column — "
                "alignment by row index would be unsafe. Skipped."
            )
            continue

        lang_df["item_id"] = lang_df["item_num"].astype(str).str.strip()

        # Confirm all item_ids in English splits exist in the lang file
        en_ids = set()
        for sdf in splits.values():
            en_ids.update(sdf["item_id"].tolist())
        missing_in_lang = en_ids - set(lang_df["item_id"])

        if missing_in_lang:
            # Check if the missing IDs are all > the language file's max item_num
            # (i.e., the lang file is a clean prefix-subset of English, not a gap)
            try:
                lang_max = max(int(x) for x in lang_df["item_id"])
                all_tail = all(int(x) > lang_max for x in missing_in_lang)
            except (ValueError, TypeError):
                all_tail = False

            if all_tail:
                notes[lang_code] = (
                    f"{src.name}: covers items 1–{lang_max} "
                    f"({len(lang_df)} items); English has {len(missing_in_lang)} "
                    "additional items beyond this range. Alignment is safe for the "
                    "shared range. Parallel split files written (items outside range omitted)."
                )
            else:
                notes[lang_code] = (
                    f"{src.name}: {len(missing_in_lang)} item_ids missing "
                    "— alignment may be incomplete. Split files written with available rows."
                )
        else:
            notes[lang_code] = (
                f"{src.name}: all item_ids matched via item_num. "
                "Parallel split files written."
            )

        for split_name, sdf in splits.items():
            split_ids = sdf["item_id"].tolist()
            lang_split = lang_df[lang_df["item_id"].isin(split_ids)].copy()
            out_path = african_dir / lang_code / "source" / f"{lang_code}_{split_name}.csv"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            lang_split.to_csv(out_path, index=False)

    return notes


# ---------------------------------------------------------------------------
# Manifest & metadata
# ---------------------------------------------------------------------------

def write_manifest(
    splits: dict[str, pd.DataFrame],
    outdir: Path,
) -> None:
    """Write en_split_manifest.csv listing every item and its split assignment."""
    rows = []
    for split_name, sdf in splits.items():
        for _, row in sdf.iterrows():
            rows.append({
                "item_id": row["item_id"],
                "split": split_name,
                "gold_answer": row["gold_answer"],
                "difficulty_score": row.get("difficulty_score", ""),
            })
    manifest = pd.DataFrame(rows)
    manifest.to_csv(outdir / "en_split_manifest.csv", index=False)


def write_metadata(
    splits: dict[str, pd.DataFrame],
    metadata_dir: Path,
    input_path: Path,
    seed: int,
    multilingual_notes: dict[str, str],
) -> None:
    """Write split_summary.json and split_summary.md."""
    summary = {
        "english_master_file": input_path.name,
        "english_master_path": str(input_path),
        "seed": seed,
        "split_sizes": {name: len(sdf) for name, sdf in splits.items()},
        "label_distribution": {
            name: sdf["gold_answer"].value_counts().to_dict()
            for name, sdf in splits.items()
        },
        "difficulty_score_stats": {
            name: {
                "mean": round(float(sdf["difficulty_score"].mean()), 4),
                "min": round(float(sdf["difficulty_score"].min()), 4),
                "max": round(float(sdf["difficulty_score"].max()), 4),
            }
            for name, sdf in splits.items()
            if "difficulty_score" in sdf.columns
        },
        "multilingual_propagation": multilingual_notes,
        "schema_notes": {
            "item_id": "Preserved from source item_num (integer string). "
                       "Unique and stable across all language files.",
            "gold_answer": "Normalised to uppercase A or B.",
            "difficulty_score": (
                "Normalised weighted sum of: "
                "feat_token_len (0.4), feat_clause_markers (0.3), "
                "feat_blank_distance (0.3 when available, else redistributed to 0.57/0.43). "
                "Higher = harder."
            ),
            "dev_stratification": "Stratified on (gold_answer × coarse sentence-length bin).",
            "challenge_selection": "Top-difficulty items from post-dev pool, label-balanced.",
            "fewshot_selection": (
                "Lowest-difficulty medium-length items, label-balanced. "
                "Disjoint from all scored splits."
            ),
        },
    }

    with open(metadata_dir / "split_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # ---- Markdown summary --------------------------------------------------
    lang_section = ""
    if multilingual_notes:
        lang_section = "\n## Multilingual Propagation\n\n"
        for lang_code, note in multilingual_notes.items():
            lang_name = MULTILINGUAL_PREFIXES.get(lang_code, lang_code.upper())
            lang_section += f"- **{lang_name} ({lang_code})**: {note}\n"
    else:
        lang_section = (
            "\n## Multilingual Propagation\n\n"
            "No multilingual files were detected or propagation was not attempted.\n"
        )

    md = f"""# Split Summary

## Source Data

- **English master file**: `{input_path.name}`
- **Random seed**: {seed}
- **Total items**: {sum(len(sdf) for sdf in splits.values())}

## Split Sizes and Label Balance

| Split | N | A | B |
|-------|---|---|---|
"""
    for name, sdf in splits.items():
        lc = sdf["gold_answer"].value_counts().to_dict()
        md += f"| {name} | {len(sdf)} | {lc.get('A', 0)} | {lc.get('B', 0)} |\n"

    md += """
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
"""

    md += lang_section

    with open(metadata_dir / "split_summary.md", "w") as f:
        f.write(md)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    here = Path(__file__).resolve().parent
    african_dir = here.parent
    parser = argparse.ArgumentParser(
        description="Generate reproducible pronoun-resolution evaluation splits.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Path to English master CSV (auto-detected if omitted).",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=african_dir / "en" / "source",
        help="Output directory for English split CSV files.",
    )
    parser.add_argument(
        "--metadata-dir",
        type=Path,
        default=african_dir / "metadata",
        help="Output directory for metadata files.",
    )
    parser.add_argument("--seed", type=int, default=329)
    parser.add_argument("--dev-size", type=int, default=100)
    parser.add_argument("--challenge-size", type=int, default=50)
    parser.add_argument("--fewshot-bank-size", type=int, default=8)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Resolve input path
    raw_data_dir = RAW_DATA_DIR
    input_path = args.input if args.input else find_english_master(raw_data_dir)
    input_path = Path(input_path).resolve()
    print(f"[INFO] English master dataset : {input_path}")

    # Create output directories
    args.outdir.mkdir(parents=True, exist_ok=True)
    args.metadata_dir.mkdir(parents=True, exist_ok=True)

    # Load & normalise
    print("[INFO] Loading and normalising data …")
    df = load_and_normalize(input_path)
    print(f"       {len(df)} items loaded.")

    # Compute difficulty proxy
    print("[INFO] Computing difficulty proxy scores …")
    df = compute_difficulty(df)
    recoverable = df["feat_blank_distance"].notna().sum()
    print(
        f"       Blank-to-candidate distance recoverable for "
        f"{recoverable}/{len(df)} items."
    )

    # Write normalised master
    norm_path = args.outdir / "en_master_normalized.csv"
    df.to_csv(norm_path, index=False)
    print(f"[INFO] Normalised master written → {norm_path}")

    # Generate splits
    print("[INFO] Generating splits …")
    splits = make_splits(
        df,
        seed=args.seed,
        dev_size=args.dev_size,
        challenge_size=args.challenge_size,
        fewshot_bank_size=args.fewshot_bank_size,
    )

    # Validate
    validate_splits(splits, total=len(df))

    # Write split CSVs
    for split_name, sdf in splits.items():
        out = args.outdir / f"en_{split_name}.csv"
        sdf.to_csv(out, index=False)
        print(f"[INFO] Wrote {split_name:<20} → {out}")

    # Manifest
    write_manifest(splits, args.outdir)
    print(f"[INFO] Manifest written         → {args.outdir / 'en_split_manifest.csv'}")

    # Multilingual propagation
    print("[INFO] Attempting multilingual propagation …")
    multilingual_notes = propagate_multilingual(splits, raw_data_dir, AFRICAN_DIR)
    for lang_code, note in multilingual_notes.items():
        print(f"       [{lang_code.upper()}] {note}")

    # Metadata
    write_metadata(splits, args.metadata_dir, input_path, args.seed, multilingual_notes)
    print(f"[INFO] Metadata written         → {args.metadata_dir}")

    print("\n[DONE] Split generation complete.")


if __name__ == "__main__":
    main()
