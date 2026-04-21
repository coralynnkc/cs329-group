#!/usr/bin/env python3
"""
generate_challenge_splits.py
============================
Generates challenge and train_holdout splits for pronoun resolution (en, de, fr, ru)
from the existing train split, excluding rows already in *_sample100.

For each language:
  1. Load {lang}_train.csv (the 80% train split).
  2. Exclude any rows whose item_id appears in {lang}_sample100.csv.
  3. Compute a difficulty proxy score (same methodology as generate_splits.py):
       feat_token_len       – whitespace-token count of the sentence
       feat_clause_markers  – count of , ; — – ( )
       feat_blank_distance  – mean token distance from '_' to each candidate mention
     Composite (normalised 0-1):  0.4 * token_len + 0.3 * clause_markers + 0.3 * blank_distance
     (distance weight redistributed 0.57/0.43 when unavailable)
  4. Select the top CHALLENGE_SIZE hardest items, label-balanced (A/B).
  5. Remaining rows → {lang}_train_holdout.

Outputs (written alongside existing splits):
  source/   {lang}_challenge.csv          {lang}_train_holdout.csv
  inference/{lang}_challenge_inference.csv {lang}_train_holdout_inference.csv
  full/     {lang}_challenge_full.csv      {lang}_train_holdout_full.csv

Usage
-----
    python srijon-2.0/scripts/generate_challenge_splits.py [--challenge-size N]
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE = Path(__file__).resolve().parents[1]   # srijon-2.0/
LANGUAGES = ["en", "de", "fr", "ru"]
CHALLENGE_SIZE = 50

SRC_FIELDS  = ["item_id", "sentence", "option_a", "option_b", "gold_answer"]
INF_FIELDS  = ["item_id", "sentence", "option_a", "option_b"]
FULL_EXTRA  = ["model_prediction", "correct"]
FULL_FIELDS = SRC_FIELDS + FULL_EXTRA


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------

def read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_trio(lang_dir: Path, lang: str, split_name: str, rows: list[dict]) -> None:
    """Write source / inference / full CSVs for a split."""
    write_csv(
        lang_dir / "source" / f"{lang}_{split_name}.csv",
        SRC_FIELDS, rows,
    )
    write_csv(
        lang_dir / "inference" / f"{lang}_{split_name}_inference.csv",
        INF_FIELDS,
        [{c: r[c] for c in INF_FIELDS} for r in rows],
    )
    write_csv(
        lang_dir / "full" / f"{lang}_{split_name}_full.csv",
        FULL_FIELDS,
        [{**r, "model_prediction": "", "correct": ""} for r in rows],
    )


# ---------------------------------------------------------------------------
# Difficulty proxy  (mirrors generate_splits.py)
# ---------------------------------------------------------------------------

def _find_nearest_distance(tokens: list[str], blank_idx: int, candidate: str) -> Optional[float]:
    """Token distance from blank position to nearest occurrence of candidate's first token."""
    first_tok = candidate.lower().split()[0] if candidate.strip() else ""
    positions = [
        i for i, t in enumerate(tokens)
        if t.lower().rstrip(".,;:!?)'\"") == first_tok and i != blank_idx
    ]
    if not positions:
        return None
    return float(min(abs(blank_idx - p) for p in positions))


def _blank_distance(sentence: str, option_a: str, option_b: str) -> Optional[float]:
    tokens = sentence.split()
    blank_idx = next((i for i, t in enumerate(tokens) if "_" in t), None)
    if blank_idx is None:
        return None
    da = _find_nearest_distance(tokens, blank_idx, option_a)
    db = _find_nearest_distance(tokens, blank_idx, option_b)
    if da is None or db is None:
        return None
    return (da + db) / 2.0


def _minmax_norm(values: list[float]) -> list[float]:
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.0] * len(values)
    return [(v - lo) / (hi - lo) for v in values]


def compute_difficulty(rows: list[dict]) -> list[float]:
    """Return a parallel list of difficulty scores (0–1, higher = harder)."""
    tok_lens, clause_counts, blank_dists = [], [], []

    for r in rows:
        sent = r["sentence"]
        tokens = sent.split()
        tok_lens.append(len(tokens))
        clause_counts.append(sum(sent.count(ch) for ch in [",", ";", "—", "–", "(", ")"]))
        blank_dists.append(_blank_distance(sent, r["option_a"], r["option_b"]))

    norm_len    = _minmax_norm(tok_lens)
    norm_clause = _minmax_norm(clause_counts)

    # Normalise only the non-None blank distances
    has_dist = [d is not None for d in blank_dists]
    dist_vals = [d for d in blank_dists if d is not None]
    norm_dist_vals = _minmax_norm(dist_vals) if dist_vals else []
    dist_iter = iter(norm_dist_vals)
    norm_dist = [next(dist_iter) if has_dist[i] else None for i in range(len(rows))]

    scores = []
    for i in range(len(rows)):
        if norm_dist[i] is not None:
            s = 0.4 * norm_len[i] + 0.3 * norm_clause[i] + 0.3 * norm_dist[i]
        else:
            s = 0.57 * norm_len[i] + 0.43 * norm_clause[i]
        scores.append(round(s, 4))

    return scores


# ---------------------------------------------------------------------------
# Challenge selection
# ---------------------------------------------------------------------------

def select_challenge(rows: list[dict], scores: list[float], challenge_size: int) -> tuple[list[dict], list[dict]]:
    """
    Pick top challenge_size hardest items, label-balanced (A/B).
    Returns (challenge_rows, remaining_rows).
    """
    # Attach scores and sort descending
    indexed = sorted(
        zip(scores, range(len(rows))),
        key=lambda x: x[0],
        reverse=True,
    )

    per_label = challenge_size // 2
    chosen_indices = set()

    for label in ["A", "B"]:
        count = 0
        for _, idx in indexed:
            if idx in chosen_indices:
                continue
            if rows[idx]["gold_answer"] == label:
                chosen_indices.add(idx)
                count += 1
                if count >= per_label:
                    break

    # Handle odd challenge_size: grab one more from the top of the remaining pool
    if challenge_size % 2 == 1:
        for _, idx in indexed:
            if idx not in chosen_indices:
                chosen_indices.add(idx)
                break

    challenge  = [rows[i] for i in sorted(chosen_indices)]
    remaining  = [rows[i] for i in range(len(rows)) if i not in chosen_indices]
    return challenge, remaining


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate challenge + train_holdout splits for srijon-2.0 pronoun resolution.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--challenge-size", type=int, default=CHALLENGE_SIZE,
        help="Number of items in the challenge split per language.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    for lang in LANGUAGES:
        lang_dir  = BASE / "pronoun_resolution" / lang
        train_path   = lang_dir / "source" / f"{lang}_train.csv"
        sample_path  = lang_dir / "source" / f"{lang}_sample100.csv"

        if not train_path.exists():
            print(f"[SKIP] {lang}: {train_path} not found.")
            continue
        if not sample_path.exists():
            print(f"[WARN] {lang}: {sample_path} not found — no rows will be excluded.")
            sample_ids = set()
        else:
            sample_rows = read_csv(sample_path)
            sample_ids  = {r["item_id"] for r in sample_rows}

        train_rows = read_csv(train_path)
        pool = [r for r in train_rows if r["item_id"] not in sample_ids]
        excluded = len(train_rows) - len(pool)

        if len(pool) < args.challenge_size:
            sys.exit(
                f"[ERROR] {lang}: only {len(pool)} rows available after excluding sample100 "
                f"({excluded} excluded), but challenge_size={args.challenge_size}."
            )

        # Difficulty scoring
        scores = compute_difficulty(pool)

        # Split
        challenge, holdout = select_challenge(pool, scores, args.challenge_size)

        # Validate label balance in challenge
        a_count = sum(1 for r in challenge if r["gold_answer"] == "A")
        b_count = sum(1 for r in challenge if r["gold_answer"] == "B")

        # Write outputs
        write_trio(lang_dir, lang, "challenge",      challenge)
        write_trio(lang_dir, lang, "train_holdout",  holdout)

        print(
            f"  {lang}: train={len(train_rows)}  excluded(sample100)={excluded}  "
            f"pool={len(pool)}  "
            f"challenge={len(challenge)} (A={a_count} B={b_count})  "
            f"train_holdout={len(holdout)}"
        )

    print("\n[DONE] Challenge and train_holdout splits written.")


if __name__ == "__main__":
    print("=== Pronoun Resolution — Challenge Split Generation ===\n")
    main()
