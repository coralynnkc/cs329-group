#!/usr/bin/env python3
"""
Build a CoLA evaluation CSV from the existing sibling grammatical/ folder.

Examples:
    python scripts/make_cola_eval.py --split in_domain_dev
    python scripts/make_cola_eval.py --split out_of_domain_dev
    python scripts/make_cola_eval.py --split in_domain_train --sample-size 300 --seed 42
"""

import argparse
import csv
import os
import random
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SIBLING_GRAMMATICAL = os.path.normpath(os.path.join(ROOT, "..", "grammatical"))
OUT_DIR = os.path.join(ROOT, "mini")

SPLIT_MAP = {
    "in_domain_train": os.path.join(SIBLING_GRAMMATICAL, "in_domain_train.tsv"),
    "in_domain_dev": os.path.join(SIBLING_GRAMMATICAL, "in_domain_dev.tsv"),
    "out_of_domain_dev": os.path.join(SIBLING_GRAMMATICAL, "out_of_domain_dev.tsv"),
}


def read_tsv(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 4:
                continue
            rows.append(
                {
                    "id": str(i),
                    "source_code": parts[0],
                    "label": parts[1],
                    "notation": parts[2],
                    "sentence": parts[3],
                }
            )
    return rows


def stratified_sample(rows, sample_size, seed):
    by_label = defaultdict(list)
    for row in rows:
        by_label[row["label"]].append(row)

    rng = random.Random(seed)
    labels = sorted(by_label.keys())
    if not labels:
        return []

    per_label = max(1, sample_size // len(labels))
    selected = []

    for label in labels:
        bucket = list(by_label[label])
        rng.shuffle(bucket)
        selected.extend(bucket[:per_label])

    if len(selected) < sample_size:
        selected_ids = {r["id"] for r in selected}
        remainder = [r for r in rows if r["id"] not in selected_ids]
        rng.shuffle(remainder)
        selected.extend(remainder[: sample_size - len(selected)])

    rng.shuffle(selected)
    return selected[:sample_size]


def write_csv(path, rows, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", required=True, choices=sorted(SPLIT_MAP.keys()))
    parser.add_argument("--sample-size", type=int, default=0, help="Optional stratified sample size.")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    source_path = SPLIT_MAP[args.split]
    if not os.path.exists(source_path):
        raise FileNotFoundError(
            f"Could not find {source_path}. This script expects the sibling folder '../grammatical/' to exist."
        )

    rows = read_tsv(source_path)
    original_n = len(rows)

    if args.sample_size:
        if args.sample_size > len(rows):
            raise ValueError(f"sample-size {args.sample_size} exceeds available rows {len(rows)}")
        rows = stratified_sample(rows, args.sample_size, args.seed)

    input_rows = [{"id": i, "sentence": row["sentence"]} for i, row in enumerate(rows, start=1)]
    answer_rows = [
        {
            "id": i,
            "label": row["label"],
            "source_code": row["source_code"],
            "original_id": row["id"],
            "sentence": row["sentence"],
        }
        for i, row in enumerate(rows, start=1)
    ]

    input_path = os.path.join(OUT_DIR, f"cola_{args.split}_input.csv")
    answer_path = os.path.join(OUT_DIR, f"cola_{args.split}_answers.csv")

    write_csv(input_path, input_rows, ["id", "sentence"])
    write_csv(answer_path, answer_rows, ["id", "label", "source_code", "original_id", "sentence"])

    print(f"Loaded {original_n} rows from {source_path}")
    if args.sample_size:
        print(f"Sampled {len(rows)} rows with seed={args.seed}")
    else:
        print(f"Using full split: {len(rows)} rows")
    print(f"Wrote: {input_path}")
    print(f"Wrote: {answer_path}")


if __name__ == "__main__":
    main()
