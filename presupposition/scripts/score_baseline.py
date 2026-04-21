"""
Score model presupposition predictions against the answer key.

Expects a prediction file named:  mini/presupposition_predictions_<model>.csv
with columns: sample_id, row_id, predicted_label
where predicted_label is one of E, N, C (case-insensitive).

Evaluation uses:
  - Accuracy (primary, matching grammatical module convention)
  - Macro-F1 across the three classes (E / N / C)
  - Per-class precision, recall, F1

Usage:
    python presupposition/scripts/score_baseline.py --model sonnet
    python presupposition/scripts/score_baseline.py --model sonnet --debug

Results are saved to:
    presupposition/results/<model>_scores.csv   — per-sample breakdown
    presupposition/results/summary.csv          — all models side by side
"""

import os
import csv
import argparse
from collections import defaultdict

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(HERE)
MINI_DIR = os.path.join(DATA_DIR, "mini")
RES_DIR  = os.path.join(DATA_DIR, "results")

LABELS = ["E", "N", "C"]

SAMPLE_ID_VARIANTS = {"sample_id", "sample", "sampleid", "sample_num"}
ROW_ID_VARIANTS    = {"row_id", "id", "rowid", "row"}


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------

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
        elif kl in ROW_ID_VARIANTS:
            remap[k] = "row_id"
    return [{remap.get(k, k): v for k, v in row.items()} for row in rows]


def pred_col(rows):
    """Auto-detect the prediction column (anything that isn't sample_id or row_id)."""
    skip = SAMPLE_ID_VARIANTS | ROW_ID_VARIANTS | {"uid", "type", "premise", "hypothesis"}
    for col in rows[0].keys():
        if col.strip().lower() not in skip:
            return col
    raise ValueError(f"Could not find prediction column in: {list(rows[0].keys())}")


# ---------------------------------------------------------------------------
# Label normalisation
# ---------------------------------------------------------------------------

def normalise_label(val):
    """Map common model outputs to E / N / C."""
    v = str(val).strip().upper()
    # Direct matches
    if v in {"E", "N", "C"}:
        return v
    # Word-form aliases
    if v in {"ENTAILMENT", "ENTAILS", "ENTAILED"}:
        return "E"
    if v in {"NEUTRAL", "NEITHER", "UNKNOWN"}:
        return "N"
    if v in {"CONTRADICTION", "CONTRADICTS", "CONTRADICTED", "CONTRADICTORY"}:
        return "C"
    return v  # pass through unknown values


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def prf(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall    = tp / (tp + fn) if (tp + fn) else 0.0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return precision, recall, f1


def compute_macro_f1(gold_list, pred_list):
    """Compute macro-averaged F1 over LABELS."""
    f1s = []
    for label in LABELS:
        tp = sum(1 for g, p in zip(gold_list, pred_list) if g == label and p == label)
        fp = sum(1 for g, p in zip(gold_list, pred_list) if g != label and p == label)
        fn = sum(1 for g, p in zip(gold_list, pred_list) if g == label and p != label)
        _, _, f1 = prf(tp, fp, fn)
        f1s.append(f1)
    return sum(f1s) / len(f1s)


def score_file(pred_path, answer_path, debug=False):
    raw_preds   = load_csv(pred_path)
    raw_answers = load_csv(answer_path)

    if debug:
        print(f"\n  [debug] pred columns  : {list(raw_preds[0].keys()) if raw_preds else 'EMPTY'}")
        print(f"  [debug] answer columns: {list(raw_answers[0].keys())}")
        print(f"  [debug] pred rows     : {len(raw_preds)}")
        print(f"  [debug] answer rows   : {len(raw_answers)}")

    preds   = normalise_keys(raw_preds)
    answers = normalise_keys(raw_answers)

    col = pred_col(preds)

    # Build lookup: (sample_id, row_id) -> predicted label
    pred_lookup = {}
    for r in preds:
        sid = str(r.get("sample_id", "1")).strip()
        rid = str(r.get("row_id", "")).strip()
        pred_lookup[(sid, rid)] = normalise_label(r.get(col, ""))

    # Per-sample accumulation
    by_sample = defaultdict(lambda: {"correct": 0, "total": 0, "gold": [], "pred": []})

    for row in answers:
        sid  = str(row.get("sample_id", "1")).strip()
        rid  = str(row.get("row_id", "")).strip()
        gold = normalise_label(row.get("gold_label", ""))
        pred = pred_lookup.get((sid, rid), "")

        by_sample[sid]["total"]   += 1
        by_sample[sid]["gold"].append(gold)
        by_sample[sid]["pred"].append(pred)
        if pred == gold:
            by_sample[sid]["correct"] += 1

        if debug:
            status = "OK" if pred == gold else "MISS"
            print(f"  [{status}] sample={sid} row={rid}  gold={gold}  pred={pred}")

    if debug:
        answer_keys = {(str(r.get("sample_id","1")).strip(), str(r.get("row_id","")).strip())
                       for r in answers}
        matched = answer_keys & pred_lookup.keys()
        print(f"  [debug] matched keys: {len(matched)} / {len(answer_keys)}")

    sample_results = []
    for sid in sorted(by_sample):
        d    = by_sample[sid]
        acc  = d["correct"] / d["total"] if d["total"] else 0.0
        mf1  = compute_macro_f1(d["gold"], d["pred"])
        sample_results.append({
            "sample_id": sid,
            "acc":       round(acc, 4),
            "macro_f1":  round(mf1, 4),
            "correct":   d["correct"],
            "total":     d["total"],
        })

    if not sample_results:
        return {"mean_acc": 0.0, "mean_f1": 0.0, "samples": []}

    mean_acc = sum(s["acc"]      for s in sample_results) / len(sample_results)
    mean_f1  = sum(s["macro_f1"] for s in sample_results) / len(sample_results)

    return {
        "mean_acc": round(mean_acc, 4),
        "mean_f1":  round(mean_f1, 4),
        "samples":  sample_results,
    }


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def write_csv_file(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def score_model(model, debug=False):
    pred_path   = os.path.join(MINI_DIR, f"presupposition_predictions_{model}.csv")
    answer_path = os.path.join(MINI_DIR, "presupposition_answers.csv")

    if not os.path.exists(pred_path):
        print(f"No predictions file found: {pred_path}")
        return
    if not os.path.exists(answer_path):
        print(f"No answers file found: {answer_path}")
        return

    r = score_file(pred_path, answer_path, debug=debug)

    print(f"\nModel: {model}")
    print(f"{'':>4}  {'s1_acc':>7}  {'s2_acc':>7}  {'s3_acc':>7}  {'mean_acc':>9}  {'mean_f1':>8}")
    print("-" * 58)
    cols = [f"{s['acc']:.3f}" for s in r["samples"]] + [""] * (3 - len(r["samples"]))
    print(f"      {'  '.join(cols)}  {r['mean_acc']:.3f}      {r['mean_f1']:.3f}")

    print(f"\n{'':>4}  {'s1_f1':>7}  {'s2_f1':>7}  {'s3_f1':>7}")
    f1_cols = [f"{s['macro_f1']:.3f}" for s in r["samples"]] + [""] * (3 - len(r["samples"]))
    print(f"      {'  '.join(f1_cols)}")

    detail_rows = [
        {
            "model":    model,
            "sample":   s["sample_id"],
            "acc":      s["acc"],
            "macro_f1": s["macro_f1"],
            "correct":  s["correct"],
            "total":    s["total"],
        }
        for s in r["samples"]
    ]
    if detail_rows:
        write_csv_file(detail_rows, os.path.join(RES_DIR, f"{model}_scores.csv"))

    summary_row  = {"model": model, "mean_acc": r["mean_acc"], "mean_f1": r["mean_f1"]}
    summary_path = os.path.join(RES_DIR, "summary.csv")
    existing = []
    if os.path.exists(summary_path):
        with open(summary_path, encoding="utf-8") as f:
            existing = list(csv.DictReader(f))
        existing = [row for row in existing if row.get("model") != model]
    existing.append(summary_row)

    all_keys = ["model", "mean_acc", "mean_f1"]
    write_csv_file([{k: row.get(k, "") for k in all_keys} for row in existing], summary_path)

    print(f"\nResults saved to  results/{model}_scores.csv")
    print(f"Summary updated:  results/summary.csv")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

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
                        help="print per-row diagnostics")
    args = parser.parse_args()

    if args.model:
        score_model(args.model, debug=args.debug)
    else:
        if not args.answers:
            parser.error("--answers is required with --predictions")
        r = score_file(args.predictions, args.answers, debug=args.debug)
        print(f"mean_acc={r['mean_acc']:.3f}  mean_f1={r['mean_f1']:.3f}")
        for s in r["samples"]:
            print(f"  sample {s['sample_id']}: acc={s['acc']:.3f}  macro_f1={s['macro_f1']:.3f}")


if __name__ == "__main__":
    main()
