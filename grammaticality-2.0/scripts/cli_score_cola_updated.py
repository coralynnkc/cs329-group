#!/usr/bin/env python3
"""
CLI scorer for CoLA-style grammaticality runs.

Designed to mirror the behavior and ergonomics of the pronoun-resolution
cli_scorer_updated.py while using binary grammaticality labels.

Usage:
    python cli_score_cola_updated.py --gold mini/cola_in_domain_dev_answers.csv \
        --pred mini/predictions_sonnet_direct_in_domain_dev.csv

Optional:
    --output results/cola_sonnet_direct_in_domain_dev_summary.json

Accepted gold labels:
    0 / 1

Accepted prediction values:
    0 / 1
    acceptable / unacceptable
    grammatical / ungrammatical
    yes / no
    true / false
    REFUSE
"""

import argparse
import json
import math
from pathlib import Path

import pandas as pd

VALID_PREDICTIONS = {"0", "1", "REFUSE"}
SCORING_LABELS = ("0", "1")
NO_VALID_PRED = "__NO_VALID_PRED__"

GOLD_ID_CANDIDATES = ["item_id", "id", "row_id", "rowid"]
GOLD_LABEL_CANDIDATES = [
    "gold_label",
    "gold_answer",
    "label",
    "answer",
    "gold",
    "correct_answer",
    "correct_label",
    "target",
]
PRED_ID_CANDIDATES = ["item_id", "id", "row_id", "rowid"]
PRED_LABEL_CANDIDATES = [
    "predicted_label",
    "pred_answer",
    "prediction",
    "label",
    "pred",
    "output",
    "answer",
    "predicted",
]

NORMALIZE_MAP = {
    # positive / acceptable
    "1": "1",
    "1.0": "1",
    "acceptable": "1",
    "grammatical": "1",
    "yes": "1",
    "true": "1",
    # negative / unacceptable
    "0": "0",
    "0.0": "0",
    "unacceptable": "0",
    "ungrammatical": "0",
    "no": "0",
    "false": "0",
    # refusals
    "refuse": "REFUSE",
    "refused": "REFUSE",
    "cannot determine": "REFUSE",
    "can't determine": "REFUSE",
    "unable": "REFUSE",
    "n/a": "REFUSE",
    "na": "REFUSE",
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


def normalize_label_value(value):
    if pd.isna(value):
        return pd.NA
    text = str(value).strip().lower()
    if text == "":
        return "REFUSE"
    return NORMALIZE_MAP.get(text, str(value).strip().upper())


def safe_div(num, denom):
    return num / denom if denom else 0.0


def matthews_corrcoef(tp, tn, fp, fn):
    denom = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    if denom <= 0:
        return 0.0
    return (tp * tn - fp * fn) / math.sqrt(denom)


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
    """
    Prefer standard CSV parsing. If that does not expose plausible columns,
    fall back to permissive whitespace/comma parsing for batch outputs.
    """
    try:
        pred = pd.read_csv(pred_path)
        pred = normalize_columns(pred)
        if find_column(pred, PRED_ID_CANDIDATES) and find_column(pred, PRED_LABEL_CANDIDATES):
            return pred
    except Exception:
        pass

    pred = pd.read_csv(pred_path, sep=r"[\s,]+", engine="python")
    pred = normalize_columns(pred)
    return pred


def main():
    parser = argparse.ArgumentParser(description="Scorer for grammaticality runs.")
    parser.add_argument("--gold", required=True, help="Path to gold/answers CSV")
    parser.add_argument("--pred", required=True, help="Path to predictions CSV")
    parser.add_argument("--output", default=None, help="Optional path to save summary JSON")
    args = parser.parse_args()

    gold_path = Path(args.gold)
    pred_path = Path(args.pred)

    gold = pd.read_csv(gold_path)
    pred = read_prediction_file(pred_path)

    gold = normalize_columns(gold)
    pred = normalize_columns(pred)

    gold_id_col = find_column(gold, GOLD_ID_CANDIDATES)
    gold_label_col = find_column(gold, GOLD_LABEL_CANDIDATES)
    pred_id_col = find_column(pred, PRED_ID_CANDIDATES)
    pred_label_col = find_column(pred, PRED_LABEL_CANDIDATES)

    if gold_id_col is None or gold_label_col is None:
        raise ValueError(
            f"Gold file must contain an ID column like {GOLD_ID_CANDIDATES} "
            f"and a label column like {GOLD_LABEL_CANDIDATES}. Found columns: {list(gold.columns)}"
        )

    if pred_id_col is None or pred_label_col is None:
        raise ValueError(
            f"Prediction file must contain an ID column like {PRED_ID_CANDIDATES} "
            f"and a label column like {PRED_LABEL_CANDIDATES}. Found columns: {list(pred.columns)}"
        )

    gold = gold[[gold_id_col, gold_label_col]].copy()
    pred = pred[[pred_id_col, pred_label_col]].copy()

    gold.columns = ["item_id", "gold_label"]
    pred.columns = ["item_id", "pred_label"]

    gold["item_id"] = gold["item_id"].astype(str).str.strip()
    pred["item_id"] = pred["item_id"].astype(str).str.strip()

    gold["gold_label"] = gold["gold_label"].map(normalize_label_value)
    pred["pred_label"] = pred["pred_label"].map(normalize_label_value)

    if gold["gold_label"].isin(SCORING_LABELS).sum() != len(gold):
        bad_gold = sorted(set(gold["gold_label"].dropna()) - set(SCORING_LABELS))
        raise ValueError(
            "Gold labels must resolve unambiguously to 0/1 for this scorer. "
            f"Unexpected gold labels: {bad_gold}"
        )

    gold_size = len(gold)
    pred_rows = len(pred)
    duplicate_pred_rows = int(pred["item_id"].duplicated().sum())
    pred_dedup = pred.drop_duplicates(subset=["item_id"], keep="first").copy()

    merged = gold.merge(pred_dedup, on="item_id", how="left")
    merged["is_missing"] = merged["pred_label"].isna()
    merged["is_refuse"] = merged["pred_label"] == "REFUSE"
    merged["is_invalid"] = (~merged["pred_label"].isin(VALID_PREDICTIONS)) & (~merged["is_missing"])
    merged["is_correct"] = merged["gold_label"] == merged["pred_label"]
    merged["pred_for_metrics"] = merged["pred_label"].where(
        merged["pred_label"].isin(SCORING_LABELS),
        NO_VALID_PRED,
    )

    n_missing = int(merged["is_missing"].sum())
    n_refuse = int(merged["is_refuse"].sum())
    n_invalid = int(merged["is_invalid"].sum())
    n_correct = int(merged["is_correct"].sum())
    extra_prediction_ids = sorted(set(pred_dedup["item_id"]) - set(gold["item_id"]))
    n_extra_ids = len(extra_prediction_ids)

    # Confusion matrix for label 1 as positive class; invalid/refuse/missing count as wrong.
    tp = int(((merged["gold_label"] == "1") & (merged["pred_for_metrics"] == "1")).sum())
    tn = int(((merged["gold_label"] == "0") & (merged["pred_for_metrics"] == "0")).sum())
    fp = int(((merged["gold_label"] == "0") & (merged["pred_for_metrics"] == "1")).sum())
    fn = int(((merged["gold_label"] == "1") & (merged["pred_for_metrics"] != "1")).sum())

    accuracy = safe_div(n_correct, gold_size)
    missing_rate = safe_div(n_missing, gold_size)
    refusal_rate = safe_div(n_refuse, gold_size)
    invalid_rate = safe_div(n_invalid, gold_size)
    coverage = safe_div(gold_size - n_missing, gold_size)
    valid_prediction_rate = safe_div(int(merged["pred_for_metrics"].isin(SCORING_LABELS).sum()), gold_size)
    mcc = matthews_corrcoef(tp, tn, fp, fn)

    class_metrics = {
        label: compute_one_vs_rest_metrics(merged["gold_label"], merged["pred_for_metrics"], label)
        for label in SCORING_LABELS
    }
    macro_f1 = safe_div(sum(class_metrics[label]["f1"] for label in SCORING_LABELS), len(SCORING_LABELS))

    summary = {
        "gold_file": str(gold_path),
        "pred_file": str(pred_path),
        "data_size": gold_size,
        "prediction_rows_raw": pred_rows,
        "prediction_rows_after_dedup": len(pred_dedup),
        "correct": n_correct,
        "accuracy": round(accuracy, 4),
        "mcc": round(mcc, 4),
        "missing_predictions": n_missing,
        "missing_rate": round(missing_rate, 4),
        "refusals": n_refuse,
        "refusal_rate": round(refusal_rate, 4),
        "invalid_predictions": n_invalid,
        "invalid_rate": round(invalid_rate, 4),
        "duplicate_prediction_rows": duplicate_pred_rows,
        "extra_prediction_ids": n_extra_ids,
        "coverage": round(coverage, 4),
        "valid_prediction_rate": round(valid_prediction_rate, 4),
        "precision_0": round(class_metrics["0"]["precision"], 4),
        "recall_0": round(class_metrics["0"]["recall"], 4),
        "f1_0": round(class_metrics["0"]["f1"], 4),
        "precision_1": round(class_metrics["1"]["precision"], 4),
        "recall_1": round(class_metrics["1"]["recall"], 4),
        "f1_1": round(class_metrics["1"]["f1"], 4),
        "macro_f1": round(macro_f1, 4),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
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

    print(json.dumps(summary, indent=2))

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
