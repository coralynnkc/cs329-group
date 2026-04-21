"""
Score model POS tag predictions against the answer key.

Expects a prediction file named:  mini/en_predictions_<model>.csv
with columns: sample_id, sentence_id, predicted_tags
where predicted_tags is a space-separated sequence of UD POS tags.

Usage:
    # Score for a model
    python scripts/score_baseline_choose_output.py --model sonnet

    # Debug to inspect token-level mismatches
    python scripts/score_baseline_choose_output.py --model sonnet --debug

    # Score a single file directly, print all results including per-tag F1
    python scripts/score_baseline_choose_output.py \\
        --predictions mini/en_predictions_sonnet.csv \\
        --answers     mini/en_answers.csv

    # Score a single file and save all results to a specified output file
    python scripts/score_baseline_choose_output.py \\
        --predictions results/chatgpt_5.4_r1_scores.csv \\
        --answers     mini/en_answers_r1.csv \\
        --output      results/my_output.csv

Results are saved to:
    results/<model>_scores.csv   — per-sample breakdown
    results/summary.csv          — all models side by side

When --output is specified with --predictions:
    <output>             — summary + per-sample + per-tag F1 all in one file
"""

import os
import csv
import argparse
from collections import defaultdict


def macro_f1_from_counts(tag_counts):
    """
    Compute macro-averaged F1 from {tag: {"tp": int, "fp": int, "fn": int}}.
    Tags with no gold occurrences are excluded (undefined recall).
    """
    f1s = []
    for counts in tag_counts.values():
        tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
        if tp + fn == 0:
            continue  # tag never appears in gold — skip
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec  = tp / (tp + fn)
        f1   = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        f1s.append(f1)
    return sum(f1s) / len(f1s) if f1s else 0.0

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(HERE)
MINI_DIR = os.path.join(DATA_DIR, "mini")
RES_DIR  = os.path.join(DATA_DIR, "results")

SAMPLE_ID_VARIANTS = {"sample_id", "sample", "sampleid", "sample_num"}
SENT_ID_VARIANTS   = {"sentence_id", "sent_id", "sentid", "id"}


def load_csv(path):
    with open(path, encoding="utf-8") as f:
        sample = f.read(4096)
        f.seek(0)
        delimiter = "\t" if sample.count("\t") > sample.count(",") else ","
        reader = csv.DictReader(f, delimiter=delimiter)
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

    def new_sample():
        return {"correct": 0, "total": 0, "tag_counts": defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})}

    by_sample = defaultdict(new_sample)
    for row in answers:
        sid  = str(row.get("sample_id", "1")).strip()
        sent = str(row.get("sentence_id", "")).strip()
        gold_seq = row[ans_col].strip().split()
        pred_seq = preds.get((sid, sent), "").strip().split()

        by_sample[sid]["total"]   += len(gold_seq)
        by_sample[sid]["correct"] += sum(p == g for p, g in zip(pred_seq, gold_seq))

        tc = by_sample[sid]["tag_counts"]
        for p, g in zip(pred_seq, gold_seq):
            if p == g:
                tc[g]["tp"] += 1
            else:
                tc[g]["fn"] += 1
                tc[p]["fp"] += 1
        # gold tokens with no matching pred (length mismatch)
        for g in gold_seq[len(pred_seq):]:
            tc[g]["fn"] += 1

    if debug:
        for sid, data in sorted(by_sample.items()):
            acc = data["correct"] / data["total"] if data["total"] else 0
            f1  = macro_f1_from_counts(data["tag_counts"])
            print(f"  [debug] sample {sid}: {data['correct']}/{data['total']} tokens  acc={acc:.3f}  macro_f1={f1:.3f}")

    # Aggregate tag counts across all samples for per-tag F1
    all_tag_counts = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    for sample_data in by_sample.values():
        for tag, counts in sample_data["tag_counts"].items():
            for k in ("tp", "fp", "fn"):
                all_tag_counts[tag][k] += counts[k]

    tag_f1 = {}
    for tag, counts in all_tag_counts.items():
        tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
        if tp + fn == 0:
            continue
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec  = tp / (tp + fn)
        f1   = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        tag_f1[tag] = round(f1, 4)

    sample_accs = [v["correct"] / v["total"] for v in by_sample.values() if v["total"]]
    sample_f1s  = [macro_f1_from_counts(v["tag_counts"]) for v in by_sample.values() if v["total"]]
    if not sample_accs:
        return {"mean_acc": 0.0, "mean_f1": 0.0, "samples_acc": [], "samples_f1": [], "tag_f1": {}}
    mean_acc = sum(sample_accs) / len(sample_accs)
    mean_f1  = sum(sample_f1s)  / len(sample_f1s)
    return {
        "mean_acc": round(mean_acc, 4),
        "mean_f1":  round(mean_f1, 4),
        "min_acc":  round(min(sample_accs), 4),
        "max_acc":  round(max(sample_accs), 4),
        "samples_acc": [round(a, 4) for a in sample_accs],
        "samples_f1":  [round(f, 4) for f in sample_f1s],
        "tag_f1": tag_f1,
    }


def write_csv_file(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def write_full_output(r, output_path):
    """Write summary, per-sample, and per-tag F1 all to one CSV."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    rows = []

    # Summary section
    rows.append({"section": "summary", "key": "mean_acc",  "value": r["mean_acc"]})
    rows.append({"section": "summary", "key": "min_acc",   "value": r["min_acc"]})
    rows.append({"section": "summary", "key": "max_acc",   "value": r["max_acc"]})
    rows.append({"section": "summary", "key": "mean_f1",   "value": r["mean_f1"]})

    # Per-sample section
    for i, (acc, f1) in enumerate(zip(r["samples_acc"], r["samples_f1"]), start=1):
        rows.append({"section": "per_sample", "key": f"sample_{i}_acc", "value": acc})
        rows.append({"section": "per_sample", "key": f"sample_{i}_f1",  "value": f1})

    # Per-tag F1 section
    for tag, f1 in sorted(r["tag_f1"].items()):
        rows.append({"section": "per_tag_f1", "key": tag, "value": f1})

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["section", "key", "value"])
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
    s = r["samples_acc"]
    cols = [f"{a:.3f}" for a in s] + [""] * (3 - len(s))

    print(f"\nModel: {model}")
    print(f"{'s1_acc':>7}  {'s2_acc':>7}  {'s3_acc':>7}  {'mean_acc':>8}  {'mean_f1':>8}")
    print("-" * 50)
    print(f"{'  '.join(cols)}  {r['mean_acc']:.3f}     {r['mean_f1']:.3f}")

    detail_rows = [{"model": model, "sample": i+1, "acc": acc, "macro_f1": f1}
                   for i, (acc, f1) in enumerate(zip(r["samples_acc"], r["samples_f1"]))]
    if detail_rows:
        write_csv_file(detail_rows, os.path.join(RES_DIR, f"{model}_scores.csv"))

    if r["tag_f1"]:
        tag_rows = [{"tag": tag, "f1": f1} for tag, f1 in sorted(r["tag_f1"].items())]
        write_csv_file(tag_rows, os.path.join(RES_DIR, f"{model}_tag_f1.csv"))

    summary_row = {"model": model, "mean_acc": r["mean_acc"], "mean_f1": r["mean_f1"]}
    summary_path = os.path.join(RES_DIR, "summary.csv")
    existing = []
    if os.path.exists(summary_path):
        with open(summary_path, encoding="utf-8") as f:
            existing = list(csv.DictReader(f))
        existing = [row for row in existing if row["model"] != model]
    existing.append(summary_row)

    all_keys = ["model", "mean_acc", "mean_f1"]
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
    parser.add_argument("--output",
                       help="path to save full results (summary + per-sample + per-tag F1) as CSV")
    parser.add_argument("--debug", action="store_true",
                       help="print token-level diagnostics")
    args = parser.parse_args()

    if args.model:
        score_model(args.model, debug=args.debug)
    else:
        if not args.answers:
            parser.error("--answers is required with --predictions")
        r = score_file(args.predictions, args.answers, debug=args.debug)
        print(f"mean_acc={r['mean_acc']:.3f}  min_acc={r['min_acc']:.3f}  max_acc={r['max_acc']:.3f}  mean_f1={r['mean_f1']:.3f}")
        print(f"per-sample acc: {r['samples_acc']}")
        print(f"per-sample f1:  {r['samples_f1']}")
        if r["tag_f1"]:
            print("\nper-tag F1:")
            for tag, f1 in sorted(r["tag_f1"].items()):
                print(f"  {tag:<6} {f1:.4f}")
        if args.output:
            write_full_output(r, args.output)
            print(f"\nFull results saved to {args.output}")


if __name__ == "__main__":
    main()
