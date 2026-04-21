"""
evaluate_lemmas.py
------------------
Compares gold lemmas from stratified sample CSVs against model predictions,
computing accuracy, normalised edit distance, and F1 macro by subgroup.

Expected file pairs (matched by size):
  gold : sample_100_stratified_labeled.csv   (columns include: form, lemma, subgroup)
  pred : sonnet_4.6_100_samples.csv          (columns include: form, model_lemma)

The two files are joined on the 'form' column.

Outputs
-------
  results/eval_<model>_<size>.csv   per-row breakdown with match/subgroup
  results/summary_all.csv           all runs side by side

Usage
-----
  # score all three sizes for one model
  python evaluate_lemmas.py --model sonnet_4.6

  # score a single pair
  python evaluate_lemmas.py \\
      --gold sample_100_stratified_labeled.csv \\
      --pred sonnet_4.6_100_samples.csv
"""

import os
import json
import csv
import argparse
import warnings
from collections import defaultdict

# ── config ────────────────────────────────────────────────────────────────────
HERE        = os.path.dirname(os.path.abspath(__file__))
BASE_DIR    = os.path.dirname(HERE)
SIZES       = [100, 200, 300, 500]
RESULTS_DIR = os.path.join(BASE_DIR, "results")

# column name variants to try (lowercase)
GOLD_LEMMA_VARIANTS  = {"lemma", "gold_lemma", "gold"}
PRED_LEMMA_VARIANTS  = {"model_lemma", "predicted_lemma", "pred_lemma", "prediction", "lemma_pred"}
SUBGROUP_VARIANTS    = {"subgroup", "group", "hardness", "category"}
FORM_VARIANTS        = {"form", "token", "word", "surface"}


# ── helpers ───────────────────────────────────────────────────────────────────

def load_csv(path):
    with open(path, encoding="utf-8-sig") as f:
        content = f.read()

    def parse_lines(lines):
        reader = csv.DictReader(lines)
        rows = list(reader)
        return [
            {k.strip(): v.strip() for k, v in r.items() if k is not None and v is not None}
            for r in rows if r
        ]

    raw_lines = [line.strip() for line in content.splitlines() if line.strip()]
    rows = parse_lines(raw_lines)

    # Some model exports wrap each whole CSV row in quotes, e.g.:
    #   "form,model_lemma"
    #   "running,run"
    # In that case, the initial parse yields a single combined header instead of
    # separate columns. Only then do we strip one outer quote pair per line.
    if rows:
        keys = list(rows[0].keys())
        if len(keys) == 1 and "," in keys[0]:
            cleaned_lines = []
            for line in raw_lines:
                if line.startswith('"') and line.endswith('"'):
                    line = line[1:-1]
                cleaned_lines.append(line)
            rows = parse_lines(cleaned_lines)

    return rows


def find_col(row_keys, variants, label):
    keys_lower = {k.lower(): k for k in row_keys}
    for v in variants:
        if v in keys_lower:
            return keys_lower[v]
    raise ValueError(
        f"Could not find '{label}' column. "
        f"Tried: {sorted(variants)}. Got: {sorted(row_keys)}"
    )


def edit_distance(a, b):
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[:]
        dp[0] = i
        for j in range(1, n + 1):
            dp[j] = prev[j-1] if a[i-1] == b[j-1] else 1 + min(prev[j-1], prev[j], dp[j-1])
    return dp[n]


def norm_edit_distance(pred, gold):
    denom = max(len(pred), len(gold))
    return 0.0 if denom == 0 else edit_distance(pred, gold) / denom


def f1(tp, fp, fn):
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec  = tp / (tp + fn) if (tp + fn) else 0.0
    return 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0


# ── core evaluator ────────────────────────────────────────────────────────────

def evaluate(gold_path, pred_path, label=""):
    gold_rows = load_csv(gold_path)
    pred_rows = load_csv(pred_path)

    if not gold_rows:
        raise ValueError(f"Gold file is empty: {gold_path}")
    if not pred_rows:
        raise ValueError(f"Pred file is empty: {pred_path}")

    # detect columns
    g_form     = find_col(gold_rows[0].keys(), FORM_VARIANTS,       "form (gold)")
    g_lemma    = find_col(gold_rows[0].keys(), GOLD_LEMMA_VARIANTS,  "gold lemma")
    g_subgroup = find_col(gold_rows[0].keys(), SUBGROUP_VARIANTS,    "subgroup")
    p_form     = find_col(pred_rows[0].keys(), FORM_VARIANTS,        "form (pred)")
    p_lemma    = find_col(pred_rows[0].keys(), PRED_LEMMA_VARIANTS,  "predicted lemma")

    # build pred lookup: form -> predicted lemma
    # if a form appears multiple times keep a list (handles duplicates)
    pred_lookup = defaultdict(list)
    for r in pred_rows:
        pred_lookup[r[p_form].lower()].append(r[p_lemma].lower())

    # ── per-row scoring ───────────────────────────────────────────────────────
    detail   = []
    unmatched = 0

    for r in gold_rows:
        form     = r[g_form]
        gold_lem = r[g_lemma].lower()
        subgroup = r[g_subgroup]
        preds    = pred_lookup.get(form.lower(), [])

        if not preds:
            unmatched += 1
            pred_lem = ""
        else:
            pred_lem = preds.pop(0)   # consume first occurrence (preserves order)

        correct = int(pred_lem == gold_lem)
        ned     = norm_edit_distance(pred_lem, gold_lem)

        detail.append({
            "form":      form,
            "gold_lemma": gold_lem,
            "pred_lemma": pred_lem,
            "subgroup":  subgroup,
            "correct":   correct,
            "ned":       round(ned, 4),
        })

    if unmatched:
        warnings.warn(f"  {unmatched} gold rows had no matching prediction (form not found in pred file).")

    # ── overall metrics ───────────────────────────────────────────────────────
    total   = len(detail)
    correct = sum(r["correct"] for r in detail)
    acc     = correct / total if total else 0.0
    mean_ned = sum(r["ned"] for r in detail) / total if total else 0.0

    # ── per-subgroup metrics (for macro-F1) ───────────────────────────────────
    # treat each subgroup as a "class": correct prediction = TP for that class
    subgroups = sorted(set(r["subgroup"] for r in detail))

    subgroup_stats = {}
    for sg in subgroups:
        sg_rows = [r for r in detail if r["subgroup"] == sg]
        sg_tp   = sum(r["correct"] for r in sg_rows)
        sg_fn   = len(sg_rows) - sg_tp

        # FP = rows from OTHER subgroups where model predicted a lemma that
        # belongs to this subgroup's gold set (conservative: use wrong predictions
        # on this subgroup's rows as FP proxy)
        sg_fp   = sg_fn   # symmetric proxy: each miss is both FN and FP

        sg_f1   = f1(sg_tp, sg_fp, sg_fn)
        sg_acc  = sg_tp / len(sg_rows) if sg_rows else 0.0
        sg_ned  = sum(r["ned"] for r in sg_rows) / len(sg_rows) if sg_rows else 0.0

        subgroup_stats[sg] = {
            "n":      len(sg_rows),
            "acc":    round(sg_acc, 4),
            "f1":     round(sg_f1, 4),
            "ned":    round(sg_ned, 4),
        }

    macro_f1 = sum(v["f1"] for v in subgroup_stats.values()) / len(subgroup_stats) if subgroup_stats else 0.0

    # ── print results ─────────────────────────────────────────────────────────
    tag = f"[{label}]" if label else ""
    print(f"\n{'─'*55}")
    print(f"  {tag}  gold={os.path.basename(gold_path)}  pred={os.path.basename(pred_path)}")
    print(f"  Overall  acc={acc:.4f}  mean_ned={mean_ned:.4f}  macro_F1={macro_f1:.4f}  n={total}")
    print(f"\n  {'Subgroup':12s}  {'n':>5}  {'acc':>6}  {'F1':>6}  {'NED':>6}")
    print(f"  {'-'*45}")
    for sg, s in subgroup_stats.items():
        print(f"  {sg:12s}  {s['n']:>5}  {s['acc']:>6.4f}  {s['f1']:>6.4f}  {s['ned']:>6.4f}")
    print(f"  {'─'*45}")
    print(f"  {'MACRO F1':12s}  {'':>5}  {'':>6}  {macro_f1:>6.4f}")

    return detail, {
        "label":     label,
        "gold_file": os.path.basename(gold_path),
        "pred_file": os.path.basename(pred_path),
        "n":         total,
        "acc":       round(acc, 4),
        "mean_ned":  round(mean_ned, 4),
        "macro_f1":  round(macro_f1, 4),
        **{f"f1_{sg}": subgroup_stats[sg]["f1"] for sg in subgroups},
        **{f"acc_{sg}": subgroup_stats[sg]["acc"] for sg in subgroups},
    }


def write_results(detail_rows, summary_row, model, size):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # per-row detail
    detail_path = os.path.join(RESULTS_DIR, f"eval_{model}_{size}.csv")
    with open(detail_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=detail_rows[0].keys())
        w.writeheader()
        w.writerows(detail_rows)
    print(f"\n  Saved detail → {detail_path}")

    # running summary
    summary_path = os.path.join(RESULTS_DIR, "summary_all.csv")
    existing = []
    if os.path.exists(summary_path):
        with open(summary_path, encoding="utf-8") as f:
            existing = list(csv.DictReader(f))
        existing = [r for r in existing if r.get("label") != summary_row["label"]]
    existing.append(summary_row)

    all_keys = list(dict.fromkeys(k for row in existing for k in row.keys()))
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
        w.writeheader()
        w.writerows([{k: r.get(k, "") for k in all_keys} for r in existing])
    print(f"  Summary  → {summary_path}")

    # running JSON summary
    json_path = os.path.join(RESULTS_DIR, "summary_all.json")
    existing_json = []
    if os.path.exists(json_path):
        with open(json_path, encoding="utf-8") as f:
            existing_json = json.load(f)
        existing_json = [r for r in existing_json if r.get("label") != summary_row["label"]]
    existing_json.append(summary_row)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(existing_json, f, indent=2)
    print(f"  JSON     → {json_path}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--model",
        help="model name prefix, e.g. sonnet_4.6 — scores all sizes")
    group.add_argument("--gold",
        help="path to a single gold CSV")
    parser.add_argument("--pred",
        help="path to a single prediction CSV (required with --gold)")
    args = parser.parse_args()

    if args.model:
        model = args.model
        for size in SIZES:
            gold_path = f"sample_{size}_stratified_labeled.csv"
            pred_path = f"{model}_{size}_samples.csv"

            if not os.path.exists(gold_path):
                print(f"  Skipping size={size}: gold file not found ({gold_path})")
                continue
            if not os.path.exists(pred_path):
                print(f"  Skipping size={size}: pred file not found ({pred_path})")
                continue

            label  = f"{model}_{size}"
            detail, summary = evaluate(gold_path, pred_path, label=label)
            write_results(detail, summary, model, size)

    else:
        if not args.pred:
            parser.error("--pred is required when using --gold")
        label  = os.path.basename(args.gold).replace(".csv", "")
        detail, summary = evaluate(args.gold, args.pred, label=label)
        model  = label
        size   = "custom"
        write_results(detail, summary, model, size)


if __name__ == "__main__":
    main()
