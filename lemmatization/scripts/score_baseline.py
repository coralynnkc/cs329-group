"""
Score model predictions against answer keys.

Expects prediction files named:  mini/<prefix>_predictions_<model>.csv
with columns: sample_id, id, predicted_lemma  (or predicted_derived_word)

Usage:
    # Score all files for a model (most common)
    python scripts/score_baseline.py --model sonnet

    # Debug a specific file to see why scores are wrong
    python scripts/score_baseline.py --model haiku --debug seg

    # Score a single file
    python scripts/score_baseline.py \\
        --predictions mini/eng_predictions_sonnet.csv \\
        --answers     mini/eng_answers.csv

Results are saved to:
    results/<model>_scores.csv   — per-sample breakdown
    results/summary.csv          — all models side by side
"""

import os
import csv
import argparse
from collections import defaultdict


def edit_distance(a, b):
    """Character-level Levenshtein distance."""
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[:]
        dp[0] = i
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[j] = prev[j - 1]
            else:
                dp[j] = 1 + min(prev[j - 1], prev[j], dp[j - 1])
    return dp[n]


def normalised_edit_distance(pred, gold):
    """Edit distance normalised by max length (0 = identical, 1 = fully different)."""
    denom = max(len(pred), len(gold))
    if denom == 0:
        return 0.0
    return edit_distance(pred, gold) / denom

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(HERE)
MINI_DIR = os.path.join(DATA_DIR, "mini")
RES_DIR  = os.path.join(DATA_DIR, "results")

PREFIXES = ["args", "seg"]

# accepted column name variants the model might return
SAMPLE_ID_VARIANTS = {"sample_id", "sample", "sampleid", "sample_num"}
ID_VARIANTS        = {"id", "row_id", "rowid", "row"}


def load_csv(path):
    with open(path, encoding="utf-8") as f:
        # strip BOM and whitespace from headers
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip().lstrip("\ufeff") for h in reader.fieldnames]
        return list(reader)


def normalise_keys(rows):
    """Return rows with sample_id/id columns normalised to those names."""
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


def build_pred_dict(rows):
    """Build {(sample_id, id): prediction} with flexible key matching."""
    rows = normalise_keys(rows)
    has_sample = "sample_id" in rows[0]
    result = {}
    for r in rows:
        pred_val = list(r.values())[-1].strip().lower()
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
    answers = normalise_keys(raw_answers)
    ans_col = pred_col(answers)

    by_sample = defaultdict(lambda: {"correct": 0, "total": 0, "ned_sum": 0.0, "misses": []})
    for row in answers:
        sid  = str(row.get("sample_id", "1")).strip()
        rid  = str(row.get("id", "")).strip()
        gold = row[ans_col].strip().lower()
        pred = preds.get((sid, rid), "").strip().lower()

        by_sample[sid]["total"] += 1
        by_sample[sid]["ned_sum"] += normalised_edit_distance(pred, gold)
        if pred == gold:
            by_sample[sid]["correct"] += 1
        else:
            by_sample[sid]["misses"].append((rid, gold, pred))

    if debug:
        # show how many pred keys matched
        answer_keys = {(str(r.get("sample_id","1")).strip(), str(r.get("id","")).strip())
                       for r in answers}
        matched = answer_keys & preds.keys()
        print(f"  [debug] answer keys (first 3): {list(answer_keys)[:3]}")
        print(f"  [debug] pred keys   (first 3): {list(preds.keys())[:3]}")
        print(f"  [debug] matched keys: {len(matched)} / {len(answer_keys)}")
        for sid, data in sorted(by_sample.items()):
            acc = data["correct"] / data["total"] if data["total"] else 0
            ned = data["ned_sum"] / data["total"] if data["total"] else 0
            print(f"  [debug] sample {sid}: {data['correct']}/{data['total']} acc={acc:.3f}  mean_ned={ned:.3f}")
            if data["misses"]:
                print(f"           first 3 misses: {data['misses'][:3]}")

    sample_accs = [v["correct"] / v["total"] for v in by_sample.values() if v["total"]]
    sample_neds = [v["ned_sum"] / v["total"] for v in by_sample.values() if v["total"]]
    if not sample_accs:
        return {"mean_acc": 0.0, "mean_ned": 0.0, "samples_acc": [], "samples_ned": []}
    mean_acc = sum(sample_accs) / len(sample_accs)
    mean_ned = sum(sample_neds) / len(sample_neds)
    return {
        "mean_acc": round(mean_acc, 4),
        "mean_ned": round(mean_ned, 4),
        "min_acc":  round(min(sample_accs), 4),
        "max_acc":  round(max(sample_accs), 4),
        "samples_acc": [round(a, 4) for a in sample_accs],
        "samples_ned": [round(d, 4) for d in sample_neds],
    }


def write_csv_file(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def score_all(model, debug_prefix=None):
    detail_rows = []
    summary_row = {"model": model}

    print(f"\nModel: {model}")
    print(f"{'file':8s}  {'s1_acc':>7}  {'s2_acc':>7}  {'s3_acc':>7}  {'mean_acc':>8}  {'mean_ned':>8}")
    print("-" * 60)

    for prefix in PREFIXES:
        pred_path   = os.path.join(MINI_DIR, f"{prefix}_predictions_{model}.csv")
        answer_path = os.path.join(MINI_DIR, f"{prefix}_answers.csv")

        if not os.path.exists(pred_path):
            print(f"  {prefix:8s}  (no predictions file found — skipping)")
            continue
        if not os.path.exists(answer_path):
            print(f"  {prefix:8s}  (no answers file found — skipping)")
            continue

        debug = (debug_prefix == prefix)
        r = score_file(pred_path, answer_path, debug=debug)
        s = r["samples_acc"]
        cols = [f"{a:.3f}" for a in s] + [""] * (3 - len(s))
        print(f"  {prefix:8s}  {'  '.join(cols)}  {r['mean_acc']:.3f}     {r['mean_ned']:.3f}")

        for i, (acc, ned) in enumerate(zip(r["samples_acc"], r["samples_ned"]), start=1):
            detail_rows.append({"model": model, "file": prefix, "sample": i, "acc": acc, "mean_ned": ned})
        summary_row[f"{prefix}_mean_acc"] = r["mean_acc"]
        summary_row[f"{prefix}_mean_ned"] = r["mean_ned"]

    if detail_rows:
        write_csv_file(detail_rows, os.path.join(RES_DIR, f"{model}_scores.csv"))

    summary_path = os.path.join(RES_DIR, "summary.csv")
    existing = []
    if os.path.exists(summary_path):
        with open(summary_path, encoding="utf-8") as f:
            existing = list(csv.DictReader(f))
        existing = [r for r in existing if r["model"] != model]
    existing.append(summary_row)

    all_keys = ["model"] + [f"{p}_{s}" for p in PREFIXES for s in ("mean_acc", "mean_ned")]
    write_csv_file([{k: r.get(k, "") for k in all_keys} for r in existing], summary_path)

    print(f"\nResults saved to  results/{model}_scores.csv")
    print(f"Summary updated:  results/summary.csv")


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--model",
                       help="score all mini files for this model (e.g. sonnet, gpt4o)")
    group.add_argument("--predictions",
                       help="path to a single predictions CSV")
    parser.add_argument("--answers",
                       help="answer key CSV (required with --predictions)")
    parser.add_argument("--debug", metavar="PREFIX",
                       help="print detailed diagnostics for one file (e.g. --debug seg)")
    args = parser.parse_args()

    if args.model:
        score_all(args.model, debug_prefix=args.debug)
    else:
        if not args.answers:
            parser.error("--answers is required with --predictions")
        r = score_file(args.predictions, args.answers, debug=bool(args.debug))
        print(f"mean_acc={r['mean_acc']:.3f}  min_acc={r['min_acc']:.3f}  max_acc={r['max_acc']:.3f}  mean_ned={r['mean_ned']:.3f}")
        print(f"per-sample acc: {r['samples_acc']}")
        print(f"per-sample ned: {r['samples_ned']}")


if __name__ == "__main__":
    main()
