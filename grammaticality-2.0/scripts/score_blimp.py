#!/usr/bin/env python3
"""
Score BLiMP-style pairwise predictions.

Expected prediction filename:
    mini/predictions_<model>_<prompt>_blimp.csv

Examples:
    python scripts/score_blimp.py --model sonnet --prompt direct
    python scripts/score_blimp.py --predictions mini/predictions_sonnet_direct_blimp.csv \
        --answers mini/blimp_answers.csv
"""

import argparse
import csv
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MINI_DIR = os.path.join(ROOT, "mini")
RES_DIR = os.path.join(ROOT, "results")

ID_VARIANTS = {"pair_id", "id", "item_id", "row_id"}
OPTION_VARIANTS = {
    "predicted_option",
    "prediction",
    "label",
    "pred",
    "answer",
    "output",
    "choice",
}
REFUSAL_MARKERS = {
    "refuse",
    "refused",
    "cannot determine",
    "can't determine",
    "unable",
    "n/a",
    "na",
    "",
}


def load_csv(path):
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip().lstrip("\ufeff") for h in reader.fieldnames]
        return list(reader)


def detect_id_col(rows):
    for col in rows[0].keys():
        if col.strip().lower() in ID_VARIANTS:
            return col
    raise ValueError(f"Could not detect pair id column from {list(rows[0].keys())}")


def detect_option_col(rows):
    for col in rows[0].keys():
        if col.strip().lower() in OPTION_VARIANTS:
            return col
    for col in rows[0].keys():
        if col.strip().lower() not in ID_VARIANTS:
            return col
    raise ValueError(f"Could not detect prediction option column from {list(rows[0].keys())}")


def normalise_option(value):
    v = str(value).strip().upper()
    if v in {"A", "B"}:
        return v, "valid"
    if v.strip().lower() in REFUSAL_MARKERS:
        return "", "refusal"
    return v, "invalid"


def build_prediction_map(rows):
    id_col = detect_id_col(rows)
    option_col = detect_option_col(rows)
    pred_map = {}
    duplicate_rows = 0

    for row in rows:
        pair_id = str(row.get(id_col, "")).strip()
        if not pair_id:
            continue
        pred, status = normalise_option(row.get(option_col, ""))
        if pair_id in pred_map:
            duplicate_rows += 1
        pred_map[pair_id] = {"prediction": pred, "status": status}

    return pred_map, duplicate_rows


def safe_div(num, den):
    return num / den if den else 0.0


def write_csv(path, rows, fieldnames=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not rows and fieldnames is None:
        raise ValueError("Need rows or fieldnames to write CSV.")
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if rows:
            writer.writerows(rows)


def upsert_summary(summary_path, row, key_fields):
    existing = []
    if os.path.exists(summary_path):
        with open(summary_path, encoding="utf-8") as f:
            existing = list(csv.DictReader(f))

    filtered = []
    for existing_row in existing:
        same_key = all(existing_row.get(k, "") == row.get(k, "") for k in key_fields)
        if not same_key:
            filtered.append(existing_row)

    filtered.append(row)
    fieldnames = ["model", "prompt", "n", "accuracy", "coverage", "refusal_rate", "invalid_rate"]
    write_csv(summary_path, filtered, fieldnames=fieldnames)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--model")
    group.add_argument("--predictions")
    parser.add_argument("--prompt", help="e.g. direct, checklist, repair")
    parser.add_argument("--answers")
    args = parser.parse_args()

    if args.model:
        if not args.prompt:
            parser.error("--prompt is required with --model")
        predictions_path = os.path.join(MINI_DIR, f"predictions_{args.model}_{args.prompt}_blimp.csv")
        answers_path = os.path.join(MINI_DIR, "blimp_answers.csv")
        model_name = args.model
        prompt_name = args.prompt
    else:
        if not args.answers:
            parser.error("--answers is required with --predictions")
        predictions_path = args.predictions
        answers_path = args.answers
        model_name = "manual"
        prompt_name = args.prompt or "manual"

    if not os.path.exists(predictions_path):
        raise FileNotFoundError(f"Predictions not found: {predictions_path}")
    if not os.path.exists(answers_path):
        raise FileNotFoundError(f"Answers not found: {answers_path}")

    pred_rows = load_csv(predictions_path)
    answer_rows = load_csv(answers_path)
    pred_map, duplicate_rows = build_prediction_map(pred_rows)

    counts = Counter()
    by_dataset = defaultdict(lambda: Counter())
    detail_rows = []

    answer_ids = set()

    for row in answer_rows:
        pair_id = str(row["pair_id"]).strip()
        dataset = row.get("dataset", "")
        gold = str(row["correct_option"]).strip().upper()
        answer_ids.add(pair_id)

        pred_entry = pred_map.get(pair_id)
        pred = ""
        status = "missing"

        if pred_entry is not None:
            pred = pred_entry["prediction"]
            status = pred_entry["status"]

        by_dataset[dataset]["n"] += 1

        if status == "missing":
            counts["missing_predictions"] += 1
            by_dataset[dataset]["missing_predictions"] += 1
        elif status == "refusal":
            counts["refusals"] += 1
            by_dataset[dataset]["refusals"] += 1
        elif status == "invalid":
            counts["invalid_predictions"] += 1
            by_dataset[dataset]["invalid_predictions"] += 1

        if status == "valid":
            counts["scored_predictions"] += 1
            by_dataset[dataset]["scored_predictions"] += 1
            if pred == gold:
                counts["correct"] += 1
                by_dataset[dataset]["correct"] += 1
            else:
                counts["incorrect"] += 1
                by_dataset[dataset]["incorrect"] += 1

        detail_rows.append(
            {
                "pair_id": pair_id,
                "dataset": dataset,
                "gold": gold,
                "prediction": pred,
                "status": status,
                "sentence_A": row.get("sentence_A", ""),
                "sentence_B": row.get("sentence_B", ""),
            }
        )

    total = len(answer_rows)
    extra_prediction_ids = len(set(pred_map.keys()) - answer_ids)
    accuracy = safe_div(counts["correct"], total)
    coverage = safe_div(counts["scored_predictions"], total)

    print(f"\nModel:  {model_name}")
    print(f"Prompt: {prompt_name}\n")
    print(f"n: {total}")
    print(f"prediction_rows_raw: {len(pred_rows)}")
    print(f"prediction_rows_after_dedup: {len(pred_map)}")
    print(f"duplicate_prediction_rows: {duplicate_rows}")
    print(f"extra_prediction_ids: {extra_prediction_ids}")
    print(f"correct: {counts['correct']}")
    print(f"incorrect: {counts['incorrect']}")
    print(f"accuracy: {accuracy:.4f}")
    print(f"coverage: {coverage:.4f}")
    print(f"missing_predictions: {counts['missing_predictions']}")
    print(f"refusals: {counts['refusals']}")
    print(f"refusal_rate: {safe_div(counts['refusals'], total):.4f}")
    print(f"invalid_predictions: {counts['invalid_predictions']}")
    print(f"invalid_rate: {safe_div(counts['invalid_predictions'], total):.4f}")

    summary_row = {
        "model": model_name,
        "prompt": prompt_name,
        "n": total,
        "accuracy": round(accuracy, 4),
        "coverage": round(coverage, 4),
        "refusal_rate": round(safe_div(counts["refusals"], total), 4),
        "invalid_rate": round(safe_div(counts["invalid_predictions"], total), 4),
    }

    detail_path = os.path.join(RES_DIR, f"blimp_{model_name}_{prompt_name}_detail.csv")
    write_csv(detail_path, detail_rows)

    dataset_rows = []
    for dataset, c in sorted(by_dataset.items()):
        dataset_rows.append(
            {
                "dataset": dataset,
                "n": c["n"],
                "accuracy": round(safe_div(c["correct"], c["n"]), 4),
                "coverage": round(safe_div(c["scored_predictions"], c["n"]), 4),
                "refusal_rate": round(safe_div(c["refusals"], c["n"]), 4),
                "invalid_rate": round(safe_div(c["invalid_predictions"], c["n"]), 4),
            }
        )

    dataset_path = os.path.join(RES_DIR, f"blimp_{model_name}_{prompt_name}_by_dataset.csv")
    write_csv(
        dataset_path,
        dataset_rows,
        fieldnames=["dataset", "n", "accuracy", "coverage", "refusal_rate", "invalid_rate"],
    )

    upsert_summary(
        os.path.join(RES_DIR, "blimp_summary.csv"),
        summary_row,
        key_fields=["model", "prompt"],
    )

    print(f"\nDetailed rows saved to: {detail_path}")
    print(f"Dataset breakdown saved to: {dataset_path}")
    print(f"Summary updated: {os.path.join(RES_DIR, 'blimp_summary.csv')}")


if __name__ == "__main__":
    main()
