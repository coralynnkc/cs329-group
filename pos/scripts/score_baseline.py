"""
Score model POS tag predictions against the answer key.

Expects a prediction file named:  mini/en_predictions_<model>.csv
with columns: sample_id, sentence_id, predicted_tags
where predicted_tags is a space-separated sequence of UD POS tags.

Usage:
    # Score for a model
    python scripts/score_baseline.py --model sonnet

    # Debug to inspect token-level mismatches
    python scripts/score_baseline.py --model sonnet --debug

    # Score a single file directly
    python scripts/score_baseline.py \\
        --predictions mini/en_predictions_sonnet.csv \\
        --answers     mini/en_answers.csv

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
SENT_ID_VARIANTS   = {"sentence_id", "sent_id", "sentid", "id"}


def load_csv(path):
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip().lstrip("\ufeff") for h in reader.fieldnames]
        return list(reader)


def normalise_keys(rows):
    if not rows:
        return rows
    remap = {}
    for k in rows[0].keys():
        kl = k.strip().lower()
        if kl in SAMPLE_ID_VARIANTS:
            remap[k] = "sample_id"
        elif kl in SENT_ID_VARIANTS:
            remap[k] = "sentence_id"
    if not remap:
        return rows
    return [{remap.get(k, k): v for k, v in row.items()} for row in rows]


def pred_col(rows):
    skip = SAMPLE_ID_VARIANTS | SENT_ID_VARIANTS
    for col in rows[0].keys():
        if col.strip().lower() not in skip:
            return col
    raise ValueError(f"Could not find prediction column in: {list(rows[0].keys())}")


def build_pred_dict(rows):
    rows = normalise_keys(rows)
    col = pred_col(rows)
    result = {}
    for r in rows:
        sid  = str(r.get("sample_id", "1")).strip()
        sent = str(r.get("sentence_id", "")).strip()
        result[(sid, sent)] = r.get(col, "").strip()
    return result


def token_accuracy(pred_tags, gold_tags):
    pred = pred_tags.strip().split()
    gold = gold_tags.strip().split()
    total = len(gold)
    if total == 0:
        return 0, 0
    correct = sum(p == g for p, g in zip(pred, gold))
    return correct, total


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

    preds   = build_pred_dict(raw_preds)
    answers = normalise_keys(raw_answers)
    ans_col = pred_col(answers)

    by_sample = defaultdict(lambda: {"correct": 0, "total": 0})
    for row in answers:
        sid  = str(row.get("sample_id", "1")).strip()
        sent = str(row.get("sentence_id", "")).strip()
        gold = row[ans_col].strip()
        pred = preds.get((sid, sent), "")

        c, t = token_accuracy(pred, gold)
        by_sample[sid]["correct"] += c
        by_sample[sid]["total"]   += t

    if debug:
        for sid, data in sorted(by_sample.items()):
            acc = data["correct"] / data["total"] if data["total"] else 0
            print(f"  [debug] sample {sid}: {data['correct']}/{data['total']} tokens = {acc:.3f}")

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
    pred_path   = os.path.join(MINI_DIR, f"en_predictions_{model}.csv")
    answer_path = os.path.join(MINI_DIR, "en_answers.csv")

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
    write_csv_file([{k: r.get(k, "") for k in all_keys} for r in existing], summary_path)

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
                       help="print token-level diagnostics")
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
