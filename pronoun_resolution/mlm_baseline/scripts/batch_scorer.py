#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple
import re
import pandas as pd

VALID_ANSWERS = {"A", "B", "REFUSE"}
SCORING_LABELS = ("A", "B")
NO_VALID_PRED = "__NO_VALID_PRED__"

GOLD_ID_CANDIDATES = ["item_id", "id"]
GOLD_ANSWER_CANDIDATES = [
    "gold_answer",
    "answer",
    "correct_letter",
    "correct_answer",
    "label",
    "gold",
]
PRED_ID_CANDIDATES = ["item_id", "id"]
PRED_ANSWER_CANDIDATES = ["answer", "pred_answer", "label", "prediction", "pred"]

NUMERIC_TO_LABEL = {
    "1": "A",
    "1.0": "A",
    "2": "B",
    "2.0": "B",
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower().replace("\ufeff", "") for c in df.columns]
    return df


def find_column(df: pd.DataFrame, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


def normalize_answer_value(value):
    if pd.isna(value):
        return pd.NA
    text = str(value).strip().upper()
    if text in {"A", "B", "REFUSE"}:
        return text
    if text in NUMERIC_TO_LABEL:
        return NUMERIC_TO_LABEL[text]
    return text


def safe_div(num, denom):
    return num / denom if denom else 0.0


def compute_one_vs_rest_metrics(y_true: pd.Series, y_pred: pd.Series, label: str):
    tp = int(((y_true == label) & (y_pred == label)).sum())
    fp = int(((y_true != label) & (y_pred == label)).sum())
    fn = int(((y_true == label) & (y_pred != label)).sum())
    support = int((y_true == label).sum())

    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn)
    f1 = safe_div(2 * precision * recall, precision + recall)

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "support": support,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def read_prediction_file(pred_path: Path) -> pd.DataFrame:
    import io
    
    # Read raw text and strip surrounding quotes from each line
    raw = pred_path.read_bytes().decode("utf-8-sig").strip()  # utf-8-sig handles the BOM (﻿)
    lines = raw.splitlines()
    
    # Strip wrapping quotes from each line: "item_id,answer" -> item_id,answer
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        cleaned_lines.append(line)
    
    cleaned_csv = "\n".join(cleaned_lines)
    pred = pd.read_csv(io.StringIO(cleaned_csv))
    pred = normalize_columns(pred)
    return pred


def extract_language_code(filename: str) -> str:
    filename_lower = filename.lower()
    for lang in ["de", "fr", "en", "ru"]:
        if re.search(r'(?<![a-z])' + lang + r'(?![a-z])', filename_lower):
            return lang
    return None


def find_matching_files(answers_dir: Path, results_dir: Path) -> List[Tuple[Path, Path, str]]:
    """
    Find matching gold and prediction files by language code.
    Returns list of (gold_file, pred_file, language_code) tuples.
    """
    matches = []
    
    # Get all CSV files from both directories
    answer_files = list(answers_dir.glob("*.csv"))
    result_files = list(results_dir.glob("*.csv"))
    
    # Group files by language code
    answers_by_lang = {}
    for f in answer_files:
        lang = extract_language_code(f.name)
        if lang:
            if lang not in answers_by_lang:
                answers_by_lang[lang] = []
            answers_by_lang[lang].append(f)
    
    results_by_lang = {}
    for f in result_files:
        lang = extract_language_code(f.name)
        if lang:
            if lang not in results_by_lang:
                results_by_lang[lang] = []
            results_by_lang[lang].append(f)
    
    # Match files by language
    for lang in answers_by_lang:
        if lang in results_by_lang:
            # For each language, match each result file with each answer file
            for result_file in results_by_lang[lang]:
                # Prefer files with "full" in the name for gold answers
                gold_candidates = [f for f in answers_by_lang[lang] if "full" in f.name.lower()]
                if not gold_candidates:
                    gold_candidates = answers_by_lang[lang]
                
                if gold_candidates:
                    # Use the first matching gold file
                    matches.append((gold_candidates[0], result_file, lang))
    
    return matches


def score_single_pair(gold_path: Path, pred_path: Path) -> Dict:
    """Score a single gold/prediction file pair."""
    
    gold = pd.read_csv(gold_path)
    pred = read_prediction_file(pred_path)

    gold = normalize_columns(gold)

    gold_id_col = find_column(gold, GOLD_ID_CANDIDATES)
    gold_ans_col = find_column(gold, GOLD_ANSWER_CANDIDATES)
    pred_id_col = find_column(pred, PRED_ID_CANDIDATES)
    pred_ans_col = find_column(pred, PRED_ANSWER_CANDIDATES)

    if gold_id_col is None or gold_ans_col is None:
        raise ValueError(
            f"Gold file must contain an ID column like {GOLD_ID_CANDIDATES} "
            f"and an answer column like {GOLD_ANSWER_CANDIDATES}. Found columns: {list(gold.columns)}"
        )

    if pred_id_col is None or pred_ans_col is None:
        raise ValueError(
            f"Prediction file must contain an ID column like {PRED_ID_CANDIDATES} "
            f"and an answer column like {PRED_ANSWER_CANDIDATES}. Found columns: {list(pred.columns)}"
        )

    gold = gold[[gold_id_col, gold_ans_col]].copy()
    pred = pred[[pred_id_col, pred_ans_col]].copy()

    gold.columns = ["item_id", "gold_answer"]
    pred.columns = ["item_id", "pred_answer"]

    gold["item_id"] = gold["item_id"].astype(str).str.strip()
    pred["item_id"] = pred["item_id"].astype(str).str.strip()

    gold["gold_answer"] = gold["gold_answer"].map(normalize_answer_value)
    pred["pred_answer"] = pred["pred_answer"].map(normalize_answer_value)

    if gold["gold_answer"].isin(["A", "B"]).sum() != len(gold):
        bad_gold = sorted(set(gold["gold_answer"].dropna()) - set(SCORING_LABELS))
        raise ValueError(
            "Gold labels must resolve unambiguously to A/B for this scorer. "
            f"Unexpected gold labels: {bad_gold}"
        )

    gold_size = len(gold)
    pred_rows = len(pred)
    duplicate_pred_rows = int(pred["item_id"].duplicated().sum())

    pred_dedup = pred.drop_duplicates(subset=["item_id"], keep="first").copy()

    merged = gold.merge(pred_dedup, on="item_id", how="left")
    merged["is_missing"] = merged["pred_answer"].isna()
    merged["is_refuse"] = merged["pred_answer"] == "REFUSE"
    merged["is_invalid"] = (~merged["pred_answer"].isin(VALID_ANSWERS)) & (~merged["is_missing"])
    merged["is_correct"] = merged["gold_answer"] == merged["pred_answer"]

    merged["pred_for_metrics"] = merged["pred_answer"].where(
        merged["pred_answer"].isin(SCORING_LABELS),
        NO_VALID_PRED,
    )

    n_missing = int(merged["is_missing"].sum())
    n_refuse = int(merged["is_refuse"].sum())
    n_invalid = int(merged["is_invalid"].sum())
    n_correct = int(merged["is_correct"].sum())
    extra_prediction_ids = sorted(set(pred_dedup["item_id"]) - set(gold["item_id"]))
    n_extra_ids = len(extra_prediction_ids)

    accuracy = safe_div(n_correct, gold_size)
    missing_rate = safe_div(n_missing, gold_size)
    refusal_rate = safe_div(n_refuse, gold_size)
    invalid_rate = safe_div(n_invalid, gold_size)
    coverage = safe_div(gold_size - n_missing, gold_size)

    class_metrics = {
        label: compute_one_vs_rest_metrics(merged["gold_answer"], merged["pred_for_metrics"], label)
        for label in SCORING_LABELS
    }
    macro_f1 = safe_div(sum(class_metrics[label]["f1"] for label in SCORING_LABELS), len(SCORING_LABELS))

    summary = {
        "gold_file": str(gold_path.name),
        "pred_file": str(pred_path.name),
        "data_size": gold_size,
        "prediction_rows_raw": pred_rows,
        "prediction_rows_after_dedup": len(pred_dedup),
        "correct": n_correct,
        "accuracy": round(accuracy, 4),
        "missing_predictions": n_missing,
        "missing_rate": round(missing_rate, 4),
        "refusals": n_refuse,
        "refusal_rate": round(refusal_rate, 4),
        "invalid_predictions": n_invalid,
        "invalid_rate": round(invalid_rate, 4),
        "duplicate_prediction_rows": duplicate_pred_rows,
        "extra_prediction_ids": n_extra_ids,
        "coverage": round(coverage, 4),
        "precision_A": round(class_metrics["A"]["precision"], 4),
        "recall_A": round(class_metrics["A"]["recall"], 4),
        "f1_A": round(class_metrics["A"]["f1"], 4),
        "precision_B": round(class_metrics["B"]["precision"], 4),
        "recall_B": round(class_metrics["B"]["recall"], 4),
        "f1_B": round(class_metrics["B"]["f1"], 4),
        "macro_f1": round(macro_f1, 4),
        "class_metrics": {
            label: {
                "tp": class_metrics[label]["tp"],
                "fp": class_metrics[label]["fp"],
                "fn": class_metrics[label]["fn"],
                "support": class_metrics[label]["support"],
                "precision": round(class_metrics[label]["precision"], 4),
                "recall": round(class_metrics[label]["recall"], 4),
                "f1": round(class_metrics[label]["f1"], 4),
            }
            for label in SCORING_LABELS
        },
    }

    return summary


def main():
    parser = argparse.ArgumentParser(description="Batch scorer for pronoun resolution runs.")
    parser.add_argument("--answers", required=True, help="Path to answers directory")
    parser.add_argument("--results", required=True, help="Path to results directory")
    parser.add_argument("--output", default=None, help="Optional path to save summary JSON")
    args = parser.parse_args()

    answers_dir = Path(args.answers)
    results_dir = Path(args.results)
    
    if not answers_dir.exists():
        raise ValueError(f"Answers directory does not exist: {answers_dir}")
    if not results_dir.exists():
        raise ValueError(f"Results directory does not exist: {results_dir}")

    # Find matching files
    matches = find_matching_files(answers_dir, results_dir)
    
    if not matches:
        print("No matching files found!")
        return
    
    print(f"Found {len(matches)} file pairs to process:")
    for gold_file, pred_file, lang in matches:
        print(f"  [{lang}] {gold_file.name} <-> {pred_file.name}")
    print()
    
    # Process each pair
    all_results = {}
    
    for gold_file, pred_file, lang in matches:
        print(f"Processing: {pred_file.name}")
        try:
            result = score_single_pair(gold_file, pred_file)
            all_results[pred_file.name] = result
            print(f"  ✓ Accuracy: {result['accuracy']}, Macro F1: {result['macro_f1']}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            all_results[pred_file.name] = {"error": str(e)}
        print()
    
    # Output all results
    output_data = {
        "summary": {
            "total_files_processed": len(matches),
            "successful": sum(1 for v in all_results.values() if "error" not in v),
            "failed": sum(1 for v in all_results.values() if "error" in v),
        },
        "results": all_results
    }
    
    #print("=" * 80)
    #print("FINAL RESULTS")
    #print("=" * 80)
    #print(json.dumps(output_data, indent=2))
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
