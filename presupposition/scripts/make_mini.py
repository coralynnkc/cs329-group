"""
Generate mini evaluation sets for manual LLM baselining.

Task: given a premise and hypothesis, classify the presupposition relationship as
E (Entailment), N (Neutral), or C (Contradiction).

Reads data/test.csv from the CoNFER dataset and creates 3 samples x 100 rows each,
stratified by label (E/N/C, ~33 per class per sample).

Output:
  mini/presupposition_input.csv    — premise + hypothesis for the model (no labels)
  mini/presupposition_answers.csv  — gold labels

Run:
    python presupposition/scripts/make_mini.py
"""

import os
import csv
import random
from collections import defaultdict

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(HERE)
OUT_DIR  = os.path.join(DATA_DIR, "mini")

SOURCE_FILE = os.path.join(DATA_DIR, "data", "test.csv")
SAMPLE_SIZE = 100
SEEDS       = [42, 123, 7]


def read_data(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def stratified_sample(rows, n, seed):
    """Sample n rows stratified by gold_label (E / N / C)."""
    by_label = defaultdict(list)
    for row in rows:
        by_label[row["gold_label"]].append(row)

    rng    = random.Random(seed)
    labels = sorted(by_label.keys())
    per_label = max(1, n // len(labels))

    sample = []
    for label in labels:
        bucket = list(by_label[label])
        rng.shuffle(bucket)
        sample.extend(bucket[:per_label])

    # top up to exactly n if needed
    sampled_uids = {r["uid"] for r in sample}
    remainder = [r for r in rows if r["uid"] not in sampled_uids]
    rng.shuffle(remainder)
    sample.extend(remainder[: n - len(sample)])

    rng.shuffle(sample)
    return sample[:n]


def write_csv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


print(f"Reading {SOURCE_FILE} ...")
data = read_data(SOURCE_FILE)
print(f"  {len(data)} rows loaded")

label_counts = defaultdict(int)
for r in data:
    label_counts[r["gold_label"]] += 1
print(f"  label distribution: {dict(label_counts)}")

input_rows  = []
answer_rows = []

for sample_num, seed in enumerate(SEEDS, start=1):
    sample = stratified_sample(data, SAMPLE_SIZE, seed)
    for row_id, row in enumerate(sample, start=1):
        input_rows.append({
            "sample_id":  sample_num,
            "row_id":     row_id,
            "uid":        row["uid"],
            "type":       row["type"],
            "premise":    row["premise"],
            "hypothesis": row["hypothesis"],
        })
        answer_rows.append({
            "sample_id":  sample_num,
            "row_id":     row_id,
            "uid":        row["uid"],
            "type":       row["type"],
            "gold_label": row["gold_label"],
        })

write_csv(input_rows,  os.path.join(OUT_DIR, "presupposition_input.csv"))
write_csv(answer_rows, os.path.join(OUT_DIR, "presupposition_answers.csv"))

n = len(input_rows)
print(f"  {n} rows written  ({len(SEEDS)} samples x {SAMPLE_SIZE})")
print(f"\nDone. Files in {OUT_DIR}/")
print("Upload presupposition_input.csv to a model, save output as")
print("presupposition_predictions_<model>.csv, then run score_baseline.py")
