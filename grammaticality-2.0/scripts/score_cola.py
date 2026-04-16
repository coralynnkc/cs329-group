#!/usr/bin/env python3
"""
Score CoLA-style binary grammaticality predictions.

Expected prediction filename:
    mini/predictions_<model>_<prompt>_<split>.csv

Examples:
    python scripts/score_cola.py --model sonnet --prompt direct --split in_domain_dev
    python scripts/score_cola.py --predictions mini/predictions_sonnet_direct_in_domain_dev.csv \
        --answers mini/cola_in_domain_dev_answers.csv
"""

import argparse
import csv
import math
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MINI_DIR = os.path.join(ROOT, "mini")
RES_DIR = os.path.join(ROOT, "results")

ID_VARIANTS = {"id", "row_id", "rowid", "item_id"}
LABEL_VARIANTS = {
    "predicted_label",
    "prediction",
    "label",
    "pred",
    "output",
    "answer",
    "predicted",
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


def normalise_binary(value):
    v = str(value).strip().lower()
    if v in {"1", "acceptable", "grammatical", "yes", "true"}:
        return "1", "valid"
    if v in {"0", "unacceptable", "ungrammatical", "no", "false"}:
        return "0", "valid"
    if v in REFUSAL_MARKERS:
        return "", "refusal"
    return v, "invalid"


def detect_id_col(rows):
    if not rows:
        raise ValueError("Prediction file is empty.")
    for col in rows[0].keys():
        if col.strip().lower() in ID_VARIANTS:
            return col
    raise ValueError(f"Could not detect id column from {list(rows[0].keys())}")


def detect_label_col(rows):
    if not rows:
        raise ValueError("Prediction file is empty.")
    for col in rows[0].keys():
        if col.strip().lower() in LABEL_VARIANTS:
            return col
    for col in rows[0].keys():
        if col.strip().lower() not in ID_VARIANTS:
            return col
    raise ValueError(f"Could not detect prediction column from {list(rows[0].keys())}")


def build_prediction_map(rows):
    id_col = detect_id_col(rows)
    label_col = detect_label_col(rows)
    pred_map = {}
    duplicate_rows = 0

    for row in rows:
        row_id = str(row.get(id_col, "")).strip()
        if not row_id:
            continue
        norm, status = normalise_binary(row.get(label_col, ""))
        if row_id in pred_map:
            duplicate_rows += 1
        pred_map[row_id] = {"prediction": norm, "status": status}

    return pred_map, duplicate_rows


def safe_div(num, den):
    return num / den if den else 0.0


def matthews_corrcoef(tp, tn, fp, fn):
    denom = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    if denom <= 0:
        return 0.0
    return (tp * tn - fp * fn) / math.sqrt(denom)


def score(predictions_path, answers_path):
    pred_rows = load_csv(predictions_path)
    ans_rows = load_csv(answers_path)

    pred_map, duplicate_rows = build_prediction_map(pred_rows)

    counts = Counter()
    detailed_rows = []

    answer_ids = set()

    for row in ans_rows:
        row_id = str(row["id"]).strip()
        gold = str(row["label"]).strip()
        answer_ids.add(row_id)

        pred_entry = pred_map.get(row_id)
        pred = ""
        status = "missing"

        if pred_entry is not None:
            pred = pred_entry["prediction"]
            status = pred_entry["status"]

        if status == "missing":
            counts["missing_predictions"] += 1
        elif status == "refusal":
            counts["refusals"] += 1
        elif status == "invalid":
            counts["invalid_predictions"] += 1

        if status == "valid":
            counts["scored_predictions"] += 1
            if pred == gold:
                counts["correct"] += 1
            else:
                counts["incorrect"] += 1

            if gold == "1" and pred == "1":
                counts["tp"] += 1
            elif gold == "0" and pred == "0":
                counts["tn"] += 1
            elif gold == "0" and pred == "1":
                counts["fp"] += 1
            elif gold == "1" and pred == "0":
                counts["fn"] += 1

        detailed_rows.append(
            {
                "id": row_id,
                "gold": gold,
                "prediction": pred,
                "status": status,
                "source_code": row.get("source_code", ""),
                "sentence": row.get("sentence", ""),
            }
        )

    extra_prediction_ids = len(set(pred_map.keys()) - answer_ids)
    total = len(ans_rows)

    tp = counts["tp"]
    tn = counts["tn"]
    fp = counts["fp"]
    fn = counts["fn"]

    accuracy = safe_div(counts["correct"], total)
    precision_1 = safe_div(tp, tp + fp)
    recall_1 = safe_div(tp, tp + fn)
    f1_1 = safe_div(2 * precision_1 * recall_1, precision_1 + recall_1)
    mcc = matthews_corrcoef(tp, tn, fp, fn)
    coverage = safe_div(counts["scored_predictions"], total)

    metrics = {
        "n": total,
        "prediction_rows_raw": len(pred_rows),
        "prediction_rows_after_dedup": len(pred_map),
        "duplicate_prediction_rows": duplicate_rows,
        "extra_prediction_ids": extra_prediction_ids,
        "correct": counts["correct"],
        "incorrect": counts["incorrect"],
        "accuracy": round(accuracy, 4),
        "mcc": round(mcc, 4),
        "precision_1": round(precision_1, 4),
        "recall_1": round(recall_1, 4),
        "f1_1": round(f1_1, 4),
        "coverage": round(coverage, 4),
        "missing_predictions": counts["missing_predictions"],
        "missing_rate": round(safe_div(counts["missing_predictions"], total), 4),
        "refusals": counts["refusals"],
        "refusal_rate": round(safe_div(counts["refusals"], total), 4),
        "invalid_predictions": counts["invalid_predictions"],
        "invalid_rate": round(safe_div(counts["invalid_predictions"], total), 4),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }

    return metrics, detailed_rows


def write_csv(path, rows, fieldnames=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not rows and fieldnames is None:
        raise ValueError("Need rows or fieldnames to write a CSV.")
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
    fieldnames = [
        "model",
        "prompt",
        "split",
        "n",
        "accuracy",
        "mcc",
        "precision_1",
        "recall_1",
        "f1_1",
        "coverage",
        "refusal_rate",
        "invalid_rate",
        "tp",
        "tn",
        "fp",
        "fn",
    ]
    write_csv(summary_path, filtered, fieldnames=fieldnames)


def print_metrics(metrics):
    keys = [
        "n",
        "prediction_rows_raw",
        "prediction_rows_after_dedup",
        "duplicate_prediction_rows",
        "extra_prediction_ids",
        "correct",
        "incorrect",
        "accuracy",
        "mcc",
        "precision_1",
        "recall_1",
        "f1_1",
        "coverage",
        "missing_predictions",
        "missing_rate",
        "refusals",
        "refusal_rate",
        "invalid_predictions",
        "invalid_rate",
        "tp",
        "tn",
        "fp",
        "fn",
    ]
    for key in keys:
        print(f"{key}: {metrics[key]}")


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--model")
    group.add_argument("--predictions")
    parser.add_argument("--prompt", help="e.g. direct, checklist, repair, fewshot")
    parser.add_argument("--split", help="e.g. in_domain_dev or out_of_domain_dev")
    parser.add_argument("--answers", help="required with --predictions")
    args = parser.parse_args()

    if args.model:
        if not args.prompt or not args.split:
            parser.error("--prompt and --split are required with --model")
        predictions_path = os.path.join(
            MINI_DIR, f"predictions_{args.model}_{args.prompt}_{args.split}.csv"
        )
        answers_path = os.path.join(MINI_DIR, f"cola_{args.split}_answers.csv")
        model_name = args.model
        prompt_name = args.prompt
        split_name = args.split
    else:
        if not args.answers:
            parser.error("--answers is required with --predictions")
        predictions_path = args.predictions
        answers_path = args.answers
        model_name = "manual"
        prompt_name = args.prompt or "manual"
        split_name = args.split or "manual"

    if not os.path.exists(predictions_path):
        raise FileNotFoundError(f"Predictions not found: {predictions_path}")
    if not os.path.exists(answers_path):
        raise FileNotFoundError(f"Answers not found: {answers_path}")

    metrics, detailed_rows = score(predictions_path, answers_path)

    print(f"\nModel:  {model_name}")
    print(f"Prompt: {prompt_name}")
    print(f"Split:  {split_name}\n")
    print_metrics(metrics)

    detail_path = os.path.join(RES_DIR, f"cola_{model_name}_{prompt_name}_{split_name}_detail.csv")
    write_csv(detail_path, detailed_rows)

    summary_row = {
        "model": model_name,
        "prompt": prompt_name,
        "split": split_name,
        "n": metrics["n"],
        "accuracy": metrics["accuracy"],
        "mcc": metrics["mcc"],
        "precision_1": metrics["precision_1"],
        "recall_1": metrics["recall_1"],
        "f1_1": metrics["f1_1"],
        "coverage": metrics["coverage"],
        "refusal_rate": metrics["refusal_rate"],
        "invalid_rate": metrics["invalid_rate"],
        "tp": metrics["tp"],
        "tn": metrics["tn"],
        "fp": metrics["fp"],
        "fn": metrics["fn"],
    }

    upsert_summary(
        os.path.join(RES_DIR, "cola_summary.csv"),
        summary_row,
        key_fields=["model", "prompt", "split"],
    )

    print(f"\nDetailed rows saved to: {detail_path}")
    print(f"Summary updated: {os.path.join(RES_DIR, 'cola_summary.csv')}")


if __name__ == "__main__":
    main()
