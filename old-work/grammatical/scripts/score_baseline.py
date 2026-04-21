"""
Score model predictions against the grammatical acceptability answer key.

Expects prediction files named:  mini/predictions_<model>.csv
with columns: sample_id, id, predicted_label   (values: 0 or 1)

Usage:
    # Score all samples for a model (most common)
    python scripts/score_baseline.py --model sonnet

    # Debug to see mismatches
    python scripts/score_baseline.py --model sonnet --debug

    # Score a single predictions file directly
    python scripts/score_baseline.py \\
        --predictions mini/predictions_sonnet.csv \\
        --answers     mini/answers.csv

Results are saved to:
    results/<model>_scores.csv   — per-sample breakdown
    results/summary.csv          — all models side by side
"""

import os
import csv
import argparse
from collections import defaultdict

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(HERE)
MINI_DIR = os.path.join(DATA_DIR, "mini")
RES_DIR  = os.path.join(DATA_DIR, "results")

SAMPLE_ID_VARIANTS = {"sample_id", "sample", "sampleid", "sample_num"}
ID_VARIANTS        = {"id", "row_id", "rowid", "row"}


def load_csv(path):
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip().lstrip("\ufeff") for h in reader.fieldnames]
        return list(reader)


def normalise_keys(rows):
    if not rows:
        return rows
    orig_keys = list(rows[0].keys())
    remap = {}
    for k in orig_keys:
        kl = k.strip().lower()
        if kl in SAMPLE_ID_VARIANTS:
            remap[k] = "sample_id"
        elif kl in ID_VARIANTS:
            remap[k] = "id"
    if not remap:
        return rows
    return [{remap.get(k, k): v for k, v in row.items()} for row in rows]


def pred_col(rows):
    """Auto-detect the prediction column (anything that isn't sample_id or id)."""
    for col in rows[0].keys():
        if col.strip().lower() not in SAMPLE_ID_VARIANTS | ID_VARIANTS:
            return col
    raise ValueError(f"Could not find prediction column in: {list(rows[0].keys())}")


def normalise_label(val):
    """Map common model outputs to '0' or '1'."""
    v = str(val).strip().lower()
    if v in {"1", "acceptable", "grammatical", "yes", "true"}:
        return "1"
    if v in {"0", "unacceptable", "ungrammatical", "no", "false"}:
        return "0"
    return v  # pass through for exact-match fallback


def build_pred_dict(rows):
    rows = normalise_keys(rows)
    has_sample = "sample_id" in rows[0]
    result = {}
    for r in rows:
        col      = pred_col(rows)
        pred_val = normalise_label(r.get(col, ""))
        row_id   = str(r.get("id", "")).strip()
        sid      = str(r.get("sample_id", "1")).strip() if has_sample else "1"
        result[(sid, row_id)] = pred_val
    return result, has_sample


def score_file(pred_path, answer_path, debug=False):
    raw_preds   = load_csv(pred_path)
    raw_answers = load_csv(answer_path)

    if debug:
        print(f"\n  [debug] prediction columns : {list(raw_preds[0].keys()) if raw_preds else 'EMPTY'}")
        print(f"  [debug] answer columns     : {list(raw_answers[0].keys())}")
        print(f"  [debug] pred rows          : {len(raw_preds)}")
        print(f"  [debug] answer rows        : {len(raw_answers)}")
        if raw_preds:
            print(f"  [debug] first pred row     : {dict(raw_preds[0])}")
        print(f"  [debug] first answer row   : {dict(raw_answers[0])}")

    preds, has_sample = build_pred_dict(raw_preds)
    answers  = normalise_keys(raw_answers)
    ans_col  = pred_col(answers)

    by_sample = defaultdict(lambda: {"correct": 0, "total": 0, "misses": []})
    for row in answers:
        sid  = str(row.get("sample_id", "1")).strip()
        rid  = str(row.get("id", "")).strip()
        gold = normalise_label(row[ans_col])
        pred = preds.get((sid, rid), "").strip()

        by_sample[sid]["total"] += 1
        if pred == gold:
            by_sample[sid]["correct"] += 1
        else:
            by_sample[sid]["misses"].append((rid, gold, pred))

    if debug:
        answer_keys = {(str(r.get("sample_id","1")).strip(), str(r.get("id","")).strip())
                       for r in answers}
        matched = answer_keys & preds.keys()
        print(f"  [debug] answer keys (first 3): {list(answer_keys)[:3]}")
        print(f"  [debug] pred keys   (first 3): {list(preds.keys())[:3]}")
        print(f"  [debug] matched keys: {len(matched)} / {len(answer_keys)}")
        for sid, data in sorted(by_sample.items()):
            acc = data["correct"] / data["total"] if data["total"] else 0
            print(f"  [debug] sample {sid}: {data['correct']}/{data['total']} = {acc:.3f}")
            if data["misses"]:
                print(f"           first 3 misses: {data['misses'][:3]}")

    sample_accs = [v["correct"] / v["total"] for v in by_sample.values() if v["total"]]
    if not sample_accs:
        return {"mean": 0.0, "min": 0.0, "max": 0.0, "samples": []}
    mean = sum(sample_accs) / len(sample_accs)
    return {"mean": round(mean, 4), "min": round(min(sample_accs), 4),
            "max": round(max(sample_accs), 4),
            "samples": [round(a, 4) for a in sample_accs]}


def write_csv_file(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def score_model(model, debug=False):
    pred_path   = os.path.join(MINI_DIR, f"predictions_{model}.csv")
    answer_path = os.path.join(MINI_DIR, "answers.csv")

    if not os.path.exists(pred_path):
        print(f"No predictions file found: {pred_path}")
        return
    if not os.path.exists(answer_path):
        print(f"No answers file found: {answer_path}")
        return

    r = score_file(pred_path, answer_path, debug=debug)
    s = r["samples"]
    rng = f"{r['min']:.3f}–{r['max']:.3f}"
    cols = [f"{a:.3f}" for a in s] + [""] * (3 - len(s))

    print(f"\nModel: {model}")
    print(f"{'s1':>6}  {'s2':>6}  {'s3':>6}  {'mean':>6}  {'range':>12}")
    print("-" * 45)
    print(f"{'  '.join(cols)}  {r['mean']:.3f}  {rng:>12}")

    detail_rows = [{"model": model, "sample": i+1, "acc": acc}
                   for i, acc in enumerate(r["samples"])]
    if detail_rows:
        write_csv_file(detail_rows, os.path.join(RES_DIR, f"{model}_scores.csv"))

    summary_row = {"model": model, "mean": r["mean"], "range": rng}
    summary_path = os.path.join(RES_DIR, "summary.csv")
    existing = []
    if os.path.exists(summary_path):
        with open(summary_path, encoding="utf-8") as f:
            existing = list(csv.DictReader(f))
        existing = [row for row in existing if row["model"] != model]
    existing.append(summary_row)

    all_keys = ["model", "mean", "range"]
    write_csv_file([{k: row.get(k, "") for k in all_keys} for row in existing], summary_path)

    print(f"\nResults saved to  results/{model}_scores.csv")
    print(f"Summary updated:  results/summary.csv")


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--model",
                       help="score mini predictions for this model (e.g. sonnet, gpt4o)")
    group.add_argument("--predictions",
                       help="path to a single predictions CSV")
    parser.add_argument("--answers",
                       help="answer key CSV (required with --predictions)")
    parser.add_argument("--debug", action="store_true",
                       help="print detailed diagnostics")
    args = parser.parse_args()

    if args.model:
        score_model(args.model, debug=args.debug)
    else:
        if not args.answers:
            parser.error("--answers is required with --predictions")
        r = score_file(args.predictions, args.answers, debug=args.debug)
        print(f"mean={r['mean']:.3f}  min={r['min']:.3f}  max={r['max']:.3f}")
        print(f"per-sample: {r['samples']}")


if __name__ == "__main__":
    main()
