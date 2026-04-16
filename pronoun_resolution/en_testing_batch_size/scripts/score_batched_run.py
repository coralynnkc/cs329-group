"""
score_batched_run.py
====================
Scorer for a single batched pronoun-resolution run.

Given a gold CSV (batch_<N>_full.csv) and a predictions CSV
(item_id, answer), this script:
  1. Validates the predictions format.
  2. Detects missing, duplicate, and invalid rows.
  3. Computes accuracy and a suite of quality / efficiency metrics.
  4. Computes per-row-position accuracy to detect degradation in long batches.
  5. Writes:
       results/<model_name>/<split_name>/scored_predictions.csv
       results/<model_name>/<split_name>/summary.json
       results/<model_name>/<split_name>/summary.md

Usage
-----
    python score_batched_run.py \\
        --gold-csv      data/batch_100_full.csv \\
        --predictions-csv  my_run/model_output_parsed.csv \\
        --model-name    claude-sonnet-4-6 \\
        --split-name    batch_100 \\
        [--raw-output-file   my_run/model_output_raw.txt] \\
        [--prompt-condition  base_zero_shot_batch] \\
        [--results-dir       pronoun_resolution/en_testing_batch_size/results] \\
        [--latency-seconds   12.4] \\
        [--input-tokens      8200] \\
        [--output-tokens     320] \\
        [--total-tokens      8520]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_ANSWERS = {"A", "B", "REFUSE"}
THIS_DIR = Path(__file__).resolve().parents[1]  # en_testing_batch_size/
DEFAULT_RESULTS_DIR = THIS_DIR / "results"

# Number of position buckets for row-position accuracy analysis
N_POSITION_BUCKETS = 4


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_gold(path: Path) -> pd.DataFrame:
    """
    Load a *_full.csv file and return it with columns validated.

    Required columns: item_id, gold_answer
    """
    try:
        df = pd.read_csv(path, dtype=str)
    except FileNotFoundError:
        sys.exit(f"[ERROR] Gold CSV not found: {path}")

    for col in ("item_id", "gold_answer"):
        if col not in df.columns:
            sys.exit(
                f"[ERROR] Gold CSV {path.name} is missing required column '{col}'.\n"
                f"  Available columns: {list(df.columns)}"
            )

    df["item_id"] = df["item_id"].str.strip()
    df["gold_answer"] = df["gold_answer"].str.strip().str.upper()

    invalid_gold = df[~df["gold_answer"].isin({"A", "B"})]["gold_answer"].unique()
    if len(invalid_gold) > 0:
        sys.exit(
            f"[ERROR] Gold CSV has unexpected gold_answer values: {invalid_gold}"
        )

    return df


def load_predictions(path: Path) -> pd.DataFrame:
    """
    Load the predictions CSV (item_id, answer) and normalise it.

    The file is expected to have been parsed from the raw model output.
    This function is deliberately lenient on column casing so that minor
    variations in the model output CSV are handled gracefully.
    """
    try:
        df = pd.read_csv(path, dtype=str)
    except FileNotFoundError:
        sys.exit(f"[ERROR] Predictions CSV not found: {path}")

    # Case-insensitive column matching
    df.columns = [c.strip().lower() for c in df.columns]

    if "item_id" not in df.columns:
        sys.exit(
            f"[ERROR] Predictions CSV {path.name} has no 'item_id' column.\n"
            f"  Available columns: {list(df.columns)}\n"
            "  Expected header: item_id,answer"
        )
    if "answer" not in df.columns:
        sys.exit(
            f"[ERROR] Predictions CSV {path.name} has no 'answer' column.\n"
            f"  Available columns: {list(df.columns)}\n"
            "  Expected header: item_id,answer"
        )

    df["item_id"] = df["item_id"].str.strip()
    df["answer"] = df["answer"].str.strip().str.upper()

    return df


# ---------------------------------------------------------------------------
# Core scoring
# ---------------------------------------------------------------------------

def score(
    gold: pd.DataFrame,
    predictions: pd.DataFrame,
) -> dict:
    """
    Compute the full metric suite.

    Parameters
    ----------
    gold        : DataFrame with columns item_id, gold_answer (+ optional extras)
    predictions : DataFrame with columns item_id, answer

    Returns
    -------
    dict with keys: metrics, joined_df
    """
    n_gold = len(gold)
    gold_ids = set(gold["item_id"])

    # ---- Duplicate detection in predictions --------------------------------
    dup_mask = predictions["item_id"].duplicated(keep=False)
    dup_ids = set(predictions.loc[dup_mask, "item_id"])
    duplicate_row_count = int(dup_mask.sum())

    # ---- Keep only first occurrence of each duplicate for joining ----------
    predictions_deduped = predictions.drop_duplicates("item_id", keep="first").copy()

    # ---- Missing / extra item_ids ------------------------------------------
    pred_ids = set(predictions_deduped["item_id"])
    missing_ids = gold_ids - pred_ids          # in gold, not in predictions
    extra_ids = pred_ids - gold_ids            # in predictions, not in gold
    n_missing = len(missing_ids)
    n_extra = len(extra_ids)

    # ---- Invalid answer labels ---------------------------------------------
    invalid_mask = ~predictions_deduped["answer"].isin(VALID_ANSWERS)
    n_invalid = int(invalid_mask.sum())
    invalid_labels = (
        predictions_deduped.loc[invalid_mask, "answer"].value_counts().to_dict()
    )

    # ---- Join --------------------------------------------------------------
    joined = gold.merge(
        predictions_deduped[["item_id", "answer"]],
        on="item_id",
        how="left",
    )
    # Rows where the prediction is missing will have answer = NaN
    joined["answer"] = joined["answer"].fillna("MISSING")

    # ---- Accuracy (REFUSE counts as wrong) ---------------------------------
    joined["is_correct"] = (
        (joined["answer"] == joined["gold_answer"]) &
        (joined["answer"].isin({"A", "B"}))
    )
    n_correct = int(joined["is_correct"].sum())
    accuracy = round(n_correct / n_gold, 6) if n_gold > 0 else None

    # ---- Parseability = proportion of rows with a valid answer label -------
    n_parseable = int(joined["answer"].isin(VALID_ANSWERS).sum())
    parseability_rate = round(n_parseable / n_gold, 6) if n_gold > 0 else None

    # ---- Refusal rate ------------------------------------------------------
    n_refuse = int((joined["answer"] == "REFUSE").sum())
    refusal_rate = round(n_refuse / n_gold, 6) if n_gold > 0 else None

    # ---- Missing row rate --------------------------------------------------
    missing_row_rate = round(n_missing / n_gold, 6) if n_gold > 0 else None

    # ---- Invalid answer rate -----------------------------------------------
    invalid_answer_rate = round(n_invalid / n_gold, 6) if n_gold > 0 else None

    metrics = {
        "n_gold_items": n_gold,
        "n_predictions_rows": len(predictions),
        "n_unique_prediction_ids": len(pred_ids),
        "n_correct": n_correct,
        "accuracy": accuracy,
        "parseability_rate": parseability_rate,
        "refusal_rate": refusal_rate,
        "missing_row_rate": missing_row_rate,
        "n_missing_ids": n_missing,
        "duplicate_row_count": duplicate_row_count,
        "n_duplicate_ids": len(dup_ids),
        "invalid_answer_rate": invalid_answer_rate,
        "n_invalid_answers": n_invalid,
        "invalid_answer_values": invalid_labels,
        "n_extra_ids_in_predictions": n_extra,
    }

    return {"metrics": metrics, "joined_df": joined}


# ---------------------------------------------------------------------------
# Row-position robustness
# ---------------------------------------------------------------------------

def position_accuracy(
    joined: pd.DataFrame,
    gold_order: pd.DataFrame,
    n_buckets: int = N_POSITION_BUCKETS,
) -> list[dict]:
    """
    Compute accuracy by row-position bucket.

    Assigns each gold row a 1-based position reflecting the order in the
    original batch (gold_order), then buckets into n_buckets equally-sized
    contiguous blocks.  Returns a list of dicts, one per bucket.

    This reveals whether model accuracy degrades for items that appear
    later in a long batch (a known concern for large context windows).
    """
    # Map item_id → row position in the original gold file
    position_map = {
        row["item_id"]: idx + 1
        for idx, row in gold_order.iterrows()
    }
    joined = joined.copy()
    joined["row_position"] = joined["item_id"].map(position_map)

    n = len(joined)
    bucket_size = max(1, n // n_buckets)

    buckets = []
    for b in range(n_buckets):
        lo = b * bucket_size + 1
        hi = (b + 1) * bucket_size if b < n_buckets - 1 else n
        mask = (joined["row_position"] >= lo) & (joined["row_position"] <= hi)
        sub = joined[mask]
        n_sub = len(sub)
        n_correct = int(sub["is_correct"].sum()) if n_sub > 0 else 0
        buckets.append({
            "bucket": b + 1,
            "row_positions": f"{lo}–{hi}",
            "n_items": n_sub,
            "n_correct": n_correct,
            "accuracy": round(n_correct / n_sub, 6) if n_sub > 0 else None,
        })

    return buckets


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def write_scored_predictions(joined: pd.DataFrame, out_dir: Path) -> Path:
    """Write scored_predictions.csv with is_correct column."""
    path = out_dir / "scored_predictions.csv"
    cols = ["item_id", "gold_answer", "answer", "is_correct"]
    # Include any extra gold columns if present (e.g. sentence)
    for c in ["sentence", "option_a", "option_b"]:
        if c in joined.columns:
            cols.append(c)
    cols_present = [c for c in cols if c in joined.columns]
    joined[cols_present].to_csv(path, index=False)
    return path


def write_summary_json(
    metrics: dict,
    position_buckets: list[dict],
    run_meta: dict,
    out_dir: Path,
) -> Path:
    """Write summary.json."""
    payload = {
        "run_metadata": run_meta,
        "metrics": metrics,
        "position_accuracy_by_bucket": position_buckets,
    }
    path = out_dir / "summary.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return path


def write_summary_md(
    metrics: dict,
    position_buckets: list[dict],
    run_meta: dict,
    out_dir: Path,
) -> Path:
    """Write summary.md — human-readable report."""
    m = metrics
    r = run_meta

    # Token efficiency block
    token_block = ""
    if r.get("total_tokens"):
        token_block = f"""\
| Total tokens          | {r['total_tokens']} |
| Avg tokens / item     | {r.get('avg_tokens_per_item', 'N/A')} |
| Correct / 1k tokens   | {r.get('correct_per_1000_tokens', 'N/A')} |
"""

    latency_block = ""
    if r.get("latency_seconds"):
        latency_block = f"""\
| Total latency (s)     | {r['latency_seconds']} |
| Avg latency / item (s)| {r.get('avg_latency_per_item', 'N/A')} |
"""

    # Position bucket table
    bucket_table = (
        "| Bucket | Row positions | N items | N correct | Accuracy |\n"
        "|--------|---------------|---------|-----------|----------|\n"
    )
    for b in position_buckets:
        acc = f"{b['accuracy']:.4f}" if b["accuracy"] is not None else "N/A"
        bucket_table += (
            f"| {b['bucket']} | {b['row_positions']} "
            f"| {b['n_items']} | {b['n_correct']} | {acc} |\n"
        )

    md = f"""# Batch Run Scoring Summary

## Run Metadata

| Key | Value |
|-----|-------|
| Model | {r.get('model_name', 'N/A')} |
| Split | {r.get('split_name', 'N/A')} |
| Prompt condition | {r.get('prompt_condition', 'N/A')} |
| Scored at | {r.get('scored_at', 'N/A')} |
| Gold CSV | {r.get('gold_csv', 'N/A')} |
| Predictions CSV | {r.get('predictions_csv', 'N/A')} |

## Core Metrics

| Metric | Value |
|--------|-------|
| Gold items | {m['n_gold_items']} |
| Prediction rows | {m['n_predictions_rows']} |
| Unique prediction IDs | {m['n_unique_prediction_ids']} |
| **Accuracy** | **{m['accuracy']}** |
| Parseability rate | {m['parseability_rate']} |
| Refusal rate | {m['refusal_rate']} |
| Missing row rate | {m['missing_row_rate']} |
| Duplicate row count | {m['duplicate_row_count']} |
| Invalid answer rate | {m['invalid_answer_rate']} |
{latency_block}{token_block}
## Position-Accuracy Breakdown

Accuracy bucketed by item row-position in the batch.
Lower accuracy in later buckets indicates degradation as batch length increases.

{bucket_table}
## Data Quality Notes

- **Missing IDs**: {m['n_missing_ids']} item_id(s) absent from predictions
- **Duplicate IDs**: {m['n_duplicate_ids']} unique item_id(s) appeared more than once
  (first occurrence kept for scoring)
- **Extra IDs**: {m['n_extra_ids_in_predictions']} prediction item_id(s) not in gold
- **Invalid labels**: {m['n_invalid_answers']} answer(s) not in {{A, B, REFUSE}}
  {("— values: " + str(m['invalid_answer_values'])) if m['invalid_answer_values'] else ""}

## Scoring Notes

- REFUSE counts as **incorrect** for accuracy purposes.
- Missing predictions are treated as incorrect.
- Per-item latency and token averages are approximations derived from
  run-level totals divided by `n_gold_items`.
"""

    path = out_dir / "summary.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score a single batched pronoun-resolution run.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--gold-csv",
        type=Path,
        required=True,
        help="Path to batch_<N>_full.csv (gold labels).",
    )
    parser.add_argument(
        "--predictions-csv",
        type=Path,
        required=True,
        help="Path to parsed model output CSV with columns item_id,answer.",
    )
    parser.add_argument(
        "--raw-output-file",
        type=Path,
        default=None,
        help="Optional path to the raw model text output (not parsed).",
    )
    parser.add_argument(
        "--prompt-condition",
        type=str,
        default="base_zero_shot_batch",
        help="Prompt condition label for the run metadata.",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        required=True,
        help="Model name (e.g. claude-sonnet-4-6).",
    )
    parser.add_argument(
        "--split-name",
        type=str,
        required=True,
        help="Split name (e.g. batch_25, batch_100, batch_250, batch_500).",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help="Root results directory.",
    )
    # Optional run-level telemetry
    parser.add_argument("--latency-seconds", type=float, default=None)
    parser.add_argument("--input-tokens", type=int, default=None)
    parser.add_argument("--output-tokens", type=int, default=None)
    parser.add_argument("--total-tokens", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # ---- Load data ---------------------------------------------------------
    print(f"\n[INFO] Gold CSV         : {args.gold_csv}")
    print(f"[INFO] Predictions CSV  : {args.predictions_csv}")

    gold = load_gold(args.gold_csv)
    predictions = load_predictions(args.predictions_csv)

    print(f"       Gold items       : {len(gold)}")
    print(f"       Prediction rows  : {len(predictions)}")

    # ---- Score -------------------------------------------------------------
    print("\n[INFO] Scoring …")
    result = score(gold, predictions)
    metrics = result["metrics"]
    joined = result["joined_df"]

    # ---- Token / latency efficiency ----------------------------------------
    n_gold = metrics["n_gold_items"]
    total_tokens = args.total_tokens
    latency_seconds = args.latency_seconds

    if total_tokens is not None:
        metrics["total_tokens"] = total_tokens
        metrics["avg_tokens_per_item"] = round(total_tokens / n_gold, 2)
        n_correct = metrics["n_correct"]
        metrics["correct_per_1000_tokens"] = round(
            (n_correct / total_tokens) * 1000, 4
        ) if total_tokens > 0 else None
    if latency_seconds is not None:
        metrics["latency_seconds"] = latency_seconds
        metrics["avg_latency_per_item"] = round(latency_seconds / n_gold, 4)
    if args.input_tokens is not None:
        metrics["input_tokens"] = args.input_tokens
    if args.output_tokens is not None:
        metrics["output_tokens"] = args.output_tokens

    # ---- Position accuracy -------------------------------------------------
    print("[INFO] Computing row-position accuracy …")
    position_buckets = position_accuracy(joined, gold)

    # ---- Run metadata ------------------------------------------------------
    run_meta = {
        "model_name": args.model_name,
        "split_name": args.split_name,
        "prompt_condition": args.prompt_condition,
        "scored_at": datetime.utcnow().isoformat() + "Z",
        "gold_csv": str(args.gold_csv),
        "predictions_csv": str(args.predictions_csv),
    }
    if args.raw_output_file:
        run_meta["raw_output_file"] = str(args.raw_output_file)
    if latency_seconds is not None:
        run_meta["latency_seconds"] = latency_seconds
        run_meta["avg_latency_per_item"] = metrics.get("avg_latency_per_item")
    if total_tokens is not None:
        run_meta["total_tokens"] = total_tokens
        run_meta["avg_tokens_per_item"] = metrics.get("avg_tokens_per_item")
        run_meta["correct_per_1000_tokens"] = metrics.get("correct_per_1000_tokens")
    if args.input_tokens is not None:
        run_meta["input_tokens"] = args.input_tokens
    if args.output_tokens is not None:
        run_meta["output_tokens"] = args.output_tokens

    # ---- Write outputs -----------------------------------------------------
    out_dir = args.results_dir / args.model_name / args.split_name
    out_dir.mkdir(parents=True, exist_ok=True)

    p1 = write_scored_predictions(joined, out_dir)
    p2 = write_summary_json(metrics, position_buckets, run_meta, out_dir)
    p3 = write_summary_md(metrics, position_buckets, run_meta, out_dir)

    # ---- Console summary ---------------------------------------------------
    print("\n=== Scoring Results ===")
    print(f"  Gold items         : {metrics['n_gold_items']}")
    print(f"  Prediction rows    : {metrics['n_predictions_rows']}")
    print(f"  Accuracy           : {metrics['accuracy']}")
    print(f"  Parseability rate  : {metrics['parseability_rate']}")
    print(f"  Refusal rate       : {metrics['refusal_rate']}")
    print(f"  Missing row rate   : {metrics['missing_row_rate']}")
    print(f"  Duplicate row count: {metrics['duplicate_row_count']}")
    print(f"  Invalid answer rate: {metrics['invalid_answer_rate']}")
    if total_tokens is not None:
        print(f"  Correct/1k tokens  : {metrics.get('correct_per_1000_tokens')}")

    print("\n  Row-position accuracy:")
    for b in position_buckets:
        acc = f"{b['accuracy']:.4f}" if b["accuracy"] is not None else "N/A"
        print(f"    Bucket {b['bucket']} (rows {b['row_positions']}): {acc}")

    print(f"\n[INFO] scored_predictions.csv → {p1}")
    print(f"[INFO] summary.json           → {p2}")
    print(f"[INFO] summary.md             → {p3}")
    print("\n[DONE] Scoring complete.")


if __name__ == "__main__":
    main()
