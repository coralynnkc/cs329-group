#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

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
    """
    Prefer ordinary CSV parsing. If that fails to expose plausible columns,
    fall back to the legacy permissive whitespace/comma parser used in batch testing.
    """
    try:
        pred = pd.read_csv(pred_path)
        pred = normalize_columns(pred)
        if find_column(pred, PRED_ID_CANDIDATES) and find_column(pred, PRED_ANSWER_CANDIDATES):
            return pred
    except Exception:
        pass

    pred = pd.read_csv(pred_path, sep=r"[\s,]+", engine="python")
    pred = normalize_columns(pred)
    return pred



def main():
    parser = argparse.ArgumentParser(description="Scorer for pronoun resolution runs.")
    parser.add_argument("--gold", required=True, help="Path to gold/full CSV")
    parser.add_argument("--pred", required=True, help="Path to generated predictions CSV")
    parser.add_argument("--output", default=None, help="Optional path to save summary JSON")
    args = parser.parse_args()

    gold_path = Path(args.gold)
    pred_path = Path(args.pred)

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
        "gold_file": str(gold_path),
        "pred_file": str(pred_path),
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

    print(json.dumps(summary, indent=2))

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
