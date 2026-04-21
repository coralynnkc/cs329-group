"""
Generate mini evaluation sets for manual LLM baselining.

Task: given a sentence, predict grammatical acceptability (0=unacceptable, 1=acceptable).

Creates one combined input CSV (3 x 300 = 900 rows, sample_id 1-3) sampled from
in_domain_train.tsv, stratified by label.

Upload the input CSV to a model, save its output as predictions, then score with
score_baseline.py.

Output:
  mini/input.csv     — sentences to classify
  mini/answers.csv   — ground-truth labels

Run:
    python scripts/make_mini.py
"""

import os
import csv
import random
from collections import defaultdict

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(HERE)
OUT_DIR  = os.path.join(DATA_DIR, "mini")

SAMPLE_SIZE = 300
SEEDS = [42, 123, 7]

SOURCE_FILE = os.path.join(DATA_DIR, "in_domain_train.tsv")


def read_tsv(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            rows.append(parts)
    return rows


def stratified_sample(rows, n, seed):
    """Sample n rows stratified by label (col 1: 0 or 1)."""
    by_label = defaultdict(list)
    for row in rows:
        label = row[1] if len(row) > 1 else "0"
        by_label[label].append(row)

    rng = random.Random(seed)
    labels = sorted(by_label.keys())
    per_label = max(1, n // len(labels))

    sample = []
    for label in labels:
        bucket = list(by_label[label])
        rng.shuffle(bucket)
        sample.extend(bucket[:per_label])

    # top up to exactly n if needed
    remainder = [r for r in rows if r not in sample]
    rng.shuffle(remainder)
    sample.extend(remainder[: n - len(sample)])

    rng.shuffle(sample)
    return sample[:n]


def write_csv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)


os.makedirs(OUT_DIR, exist_ok=True)

print(f"Reading {SOURCE_FILE} ...")
rows = read_tsv(SOURCE_FILE)
print(f"  {len(rows)} rows loaded")

label_counts = defaultdict(int)
for r in rows:
    label_counts[r[1]] += 1
print(f"  label distribution: {dict(label_counts)}")

input_rows  = [["sample_id", "id", "sentence"]]
answer_rows = [["sample_id", "id", "label"]]

for sample_num, seed in enumerate(SEEDS, start=1):
    sample = stratified_sample(rows, SAMPLE_SIZE, seed)
    for row_id, row in enumerate(sample, start=1):
        sentence = row[3] if len(row) > 3 else row[-1]
        label    = row[1]
        input_rows.append([sample_num, row_id, sentence])
        answer_rows.append([sample_num, row_id, label])

write_csv(input_rows,  os.path.join(OUT_DIR, "input.csv"))
write_csv(answer_rows, os.path.join(OUT_DIR, "answers.csv"))

print(f"\n{len(input_rows)-1} input rows  ({len(SEEDS)} samples x {SAMPLE_SIZE})")
print(f"Files written to {OUT_DIR}/")
print("Upload input.csv to a model, save output as predictions_<model>.csv, then run score_baseline.py")
