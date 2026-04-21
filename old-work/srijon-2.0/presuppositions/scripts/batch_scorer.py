#!/usr/bin/env python3

import argparse
import io
import json
import re
from pathlib import Path
from typing import List, Tuple

import pandas as pd

LANGUAGES = ["de", "vi", "fr", "ru", "hi", "en"]
GOLD_LABELS = ["E", "N", "C"]
PROB_COLS = ["e_probability", "n_probability", "c_probability"]


# --------------------------------------------------------------------------- #
# File parsing
# --------------------------------------------------------------------------- #

def extract_language_code(filename: str) -> str:
    filename_lower = filename.lower()
    for lang in LANGUAGES:
        if re.search(r'(?<![a-z])' + lang + r'(?![a-z])', filename_lower):
            return lang
    return None


def parse_quoted_csv(path: Path) -> pd.DataFrame:
    """Handle the format where every row is wrapped in outer quotes: "col1,col2" """
    raw = path.read_bytes().decode("utf-8-sig").strip()
    lines = raw.splitlines()
    cleaned = []
    for line in lines:
        line = line.strip()
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        cleaned.append(line)
    df = pd.read_csv(io.StringIO("\n".join(cleaned)))
    df.columns = [c.strip().lower().replace("\ufeff", "") for c in df.columns]
    return df


def read_gold(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace("\ufeff", "") for c in df.columns]
    df["item_id"] = df["item_id"].astype(str).str.strip()
    # Normalise label to uppercase
    df["gold_label"] = df["gold_label"].astype(str).str.strip().str.upper()
    return df[["item_id", "gold_label"]]


def read_pred(path: Path) -> pd.DataFrame:
    # Try plain CSV first, fall back to the quoted format
    try:
        df = pd.read_csv(path)
        df.columns = [c.strip().lower().replace("\ufeff", "") for c in df.columns]
        if "item_id" in df.columns and "e_probability" in df.columns:
            df["item_id"] = df["item_id"].astype(str).str.strip()
            return df[["item_id"] + PROB_COLS]
    except Exception:
        pass

    df = parse_quoted_csv(path)
    df["item_id"] = df["item_id"].astype(str).str.strip()
    return df[["item_id"] + PROB_COLS]


# --------------------------------------------------------------------------- #
# Scoring
# --------------------------------------------------------------------------- #

def score_pair(gold_path: Path, pred_path: Path) -> dict:
    gold = read_gold(gold_path)
    pred = read_pred(pred_path)

    merged = gold.merge(pred, on="item_id", how="inner")
    n_matched = len(merged)
    n_gold = len(gold)

    if n_matched == 0:
        raise ValueError("No matching item_ids between gold and prediction file.")

    results = {}
    for label in GOLD_LABELS:
        subset = merged[merged["gold_label"] == label]
        n = len(subset)
        if n == 0:
            results[label] = {"count": 0, "avg_e": None, "avg_n": None, "avg_c": None}
        else:
            results[label] = {
                "count": n,
                "avg_e_probability": round(subset["e_probability"].mean(), 4),
                "avg_n_probability": round(subset["n_probability"].mean(), 4),
                "avg_c_probability": round(subset["c_probability"].mean(), 4),
            }

    return {
        "gold_file": gold_path.name,
        "pred_file": pred_path.name,
        "items_in_gold": n_gold,
        "items_matched": n_matched,
        "avg_probabilities_by_gold_label": results,
    }


# --------------------------------------------------------------------------- #
# File matching
# --------------------------------------------------------------------------- #

def find_matching_files(answers_dir: Path, results_dir: Path) -> List[Tuple[Path, Path, str]]:
    matches = []

    answers_by_lang = {}
    for f in answers_dir.glob("*.csv"):
        lang = extract_language_code(f.name)
        if lang:
            answers_by_lang.setdefault(lang, []).append(f)

    results_by_lang = {}
    for f in results_dir.glob("*.csv"):
        lang = extract_language_code(f.name)
        if lang:
            results_by_lang.setdefault(lang, []).append(f)

    for lang in answers_by_lang:
        if lang in results_by_lang:
            gold_candidates = [f for f in answers_by_lang[lang] if "full" in f.name.lower()]
            if not gold_candidates:
                gold_candidates = answers_by_lang[lang]
            for result_file in results_by_lang[lang]:
                matches.append((gold_candidates[0], result_file, lang))

    return matches


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(description="Probability scorer grouped by gold label.")
    parser.add_argument("--answers", required=True, help="Path to answers directory")
    parser.add_argument("--results", required=True, help="Path to results directory")
    parser.add_argument("--output", default=None, help="Optional path to save JSON output")
    args = parser.parse_args()

    answers_dir = Path(args.answers)
    results_dir = Path(args.results)

    if not answers_dir.exists():
        raise ValueError(f"Answers directory does not exist: {answers_dir}")
    if not results_dir.exists():
        raise ValueError(f"Results directory does not exist: {results_dir}")

    matches = find_matching_files(answers_dir, results_dir)

    if not matches:
        print("No matching files found!")
        return

    print(f"Found {len(matches)} file pairs to process:")
    for gold_file, pred_file, lang in matches:
        print(f"  [{lang}] {gold_file.name} <-> {pred_file.name}")
    print()

    all_results = {}
    for gold_file, pred_file, lang in matches:
        print(f"Processing: {pred_file.name}")
        try:
            result = score_pair(gold_file, pred_file)
            all_results[pred_file.name] = result
            for lbl, stats in result["avg_probabilities_by_gold_label"].items():
                if stats["count"] > 0:
                    print(f"  Gold={lbl} (n={stats['count']}): "
                          f"avg_E={stats['avg_e_probability']}, "
                          f"avg_N={stats['avg_n_probability']}, "
                          f"avg_C={stats['avg_c_probability']}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            all_results[pred_file.name] = {"error": str(e)}
        print()

    output_data = {
        "summary": {
            "total_files_processed": len(matches),
            "successful": sum(1 for v in all_results.values() if "error" not in v),
            "failed": sum(1 for v in all_results.values() if "error" in v),
        },
        "results": all_results,
    }

    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(json.dumps(output_data, indent=2))

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
