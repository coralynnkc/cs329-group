#!/usr/bin/env python3

import argparse
import pandas as pd
import json
from pathlib import Path


VALID_ANSWERS = {"A", "B", "REFUSE"}


def normalize_columns(df):
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def find_column(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


def main():
    parser = argparse.ArgumentParser(description="Simple scorer for pronoun resolution runs.")
    parser.add_argument("--gold", required=True, help="Path to gold standard CSV")
    parser.add_argument("--pred", required=True, help="Path to generated predictions CSV")
    parser.add_argument("--output", default=None, help="Optional path to save summary JSON")
    args = parser.parse_args()

    gold_path = Path(args.gold)
    pred_path = Path(args.pred)

    gold = pd.read_csv(gold_path)
    pred = pd.read_csv(pred_path)

    gold = normalize_columns(gold)
    pred = normalize_columns(pred)

    gold_id_col = find_column(gold, ["item_id", "id"])
    gold_ans_col = find_column(gold, ["gold_answer", "answer", "label", "gold"])
    pred_id_col = find_column(pred, ["item_id", "id"])
    pred_ans_col = find_column(pred, ["answer", "label", "prediction", "pred"])

    if gold_id_col is None or gold_ans_col is None:
        raise ValueError("Gold file must contain columns like item_id and answer")

    if pred_id_col is None or pred_ans_col is None:
        raise ValueError("Prediction file must contain columns like item_id and answer")

    gold = gold[[gold_id_col, gold_ans_col]].copy()
    pred = pred[[pred_id_col, pred_ans_col]].copy()

    gold.columns = ["item_id", "gold_answer"]
    pred.columns = ["item_id", "pred_answer"]

    gold["item_id"] = gold["item_id"].astype(str).str.strip()
    pred["item_id"] = pred["item_id"].astype(str).str.strip()

    gold["gold_answer"] = gold["gold_answer"].astype(str).str.strip().str.upper()
    pred["pred_answer"] = pred["pred_answer"].astype(str).str.strip().str.upper()

    gold_size = len(gold)
    pred_rows = len(pred)

    duplicate_pred_rows = int(pred["item_id"].duplicated().sum())
    pred_dedup = pred.drop_duplicates(subset=["item_id"], keep="first").copy()

    merged = gold.merge(pred_dedup, on="item_id", how="left")

    merged["is_missing"] = merged["pred_answer"].isna()
    merged["is_refuse"] = merged["pred_answer"] == "REFUSE"
    merged["is_invalid"] = (~merged["pred_answer"].isin(VALID_ANSWERS)) & (~merged["is_missing"])
    merged["is_correct"] = merged["gold_answer"] == merged["pred_answer"]

    n_missing = int(merged["is_missing"].sum())
    n_refuse = int(merged["is_refuse"].sum())
    n_invalid = int(merged["is_invalid"].sum())
    n_correct = int(merged["is_correct"].sum())

    extra_prediction_ids = sorted(set(pred_dedup["item_id"]) - set(gold["item_id"]))
    n_extra_ids = len(extra_prediction_ids)

    accuracy = n_correct / gold_size if gold_size else 0.0
    missing_rate = n_missing / gold_size if gold_size else 0.0
    refusal_rate = n_refuse / gold_size if gold_size else 0.0
    invalid_rate = n_invalid / gold_size if gold_size else 0.0
    coverage = (gold_size - n_missing) / gold_size if gold_size else 0.0

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
    }

    print(json.dumps(summary, indent=2))

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()