#!/usr/bin/env python3
"""
Build a BLiMP-style pairwise evaluation CSV from a directory of JSONL / CSV / TSV files.

Examples:
    python scripts/make_blimp_eval.py --source-dir data/blimp
    python scripts/make_blimp_eval.py --source-dir data/blimp --max-per-dataset 200 --seed 42
"""

import argparse
import csv
import glob
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "mini")

GOOD_KEYS = [
    "sentence_good",
    "good_sentence",
    "good",
    "acceptable",
    "grammatical",
    "sentence1_good",
]
BAD_KEYS = [
    "sentence_bad",
    "bad_sentence",
    "bad",
    "unacceptable",
    "ungrammatical",
    "sentence1_bad",
]
DATASET_KEYS = ["dataset", "subdataset", "phenomenon"]
PAIR_ID_KEYS = ["pair_id", "uid", "id", "item_id"]


def first_matching_key(row, candidates):
    lower_map = {k.lower(): k for k in row.keys()}
    for key in candidates:
        if key.lower() in lower_map:
            return lower_map[key.lower()]
    return None


def load_records(path):
    if path.endswith(".jsonl"):
        rows = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    delimiter = "," if path.endswith(".csv") else "\t"
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        reader.fieldnames = [h.strip().lstrip("\ufeff") for h in reader.fieldnames]
        return list(reader)


def normalise_pair_records(path):
    rows = load_records(path)
    dataset_name = os.path.splitext(os.path.basename(path))[0]
    records = []

    for idx, row in enumerate(rows, start=1):
        good_key = first_matching_key(row, GOOD_KEYS)
        bad_key = first_matching_key(row, BAD_KEYS)

        if not good_key or not bad_key:
            raise ValueError(
                f"Could not detect good/bad sentence columns in {path}. "
                f"Available columns: {list(row.keys())}"
            )

        dataset_key = first_matching_key(row, DATASET_KEYS)
        pair_id_key = first_matching_key(row, PAIR_ID_KEYS)

        records.append(
            {
                "dataset": str(row.get(dataset_key, dataset_name)).strip(),
                "original_pair_id": str(row.get(pair_id_key, idx)).strip(),
                "good_sentence": str(row[good_key]).strip(),
                "bad_sentence": str(row[bad_key]).strip(),
            }
        )

    return records


def write_csv(path, rows, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--max-per-dataset", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    patterns = ["*.jsonl", "*.csv", "*.tsv"]
    files = []
    for pattern in patterns:
        files.extend(sorted(glob.glob(os.path.join(args.source_dir, pattern))))

    if not files:
        raise FileNotFoundError(f"No jsonl/csv/tsv files found under {args.source_dir}")

    rng = random.Random(args.seed)
    input_rows = []
    answer_rows = []
    pair_id = 1

    for path in files:
        records = normalise_pair_records(path)
        if args.max_per_dataset and len(records) > args.max_per_dataset:
            rng.shuffle(records)
            records = records[: args.max_per_dataset]

        for record in records:
            good = record["good_sentence"]
            bad = record["bad_sentence"]

            if rng.random() < 0.5:
                sent_a, sent_b = good, bad
                correct = "A"
            else:
                sent_a, sent_b = bad, good
                correct = "B"

            input_rows.append(
                {
                    "pair_id": pair_id,
                    "dataset": record["dataset"],
                    "sentence_A": sent_a,
                    "sentence_B": sent_b,
                }
            )
            answer_rows.append(
                {
                    "pair_id": pair_id,
                    "dataset": record["dataset"],
                    "correct_option": correct,
                    "original_pair_id": record["original_pair_id"],
                    "sentence_A": sent_a,
                    "sentence_B": sent_b,
                }
            )
            pair_id += 1

    input_path = os.path.join(OUT_DIR, "blimp_input.csv")
    answer_path = os.path.join(OUT_DIR, "blimp_answers.csv")
    write_csv(input_path, input_rows, ["pair_id", "dataset", "sentence_A", "sentence_B"])
    write_csv(
        answer_path,
        answer_rows,
        ["pair_id", "dataset", "correct_option", "original_pair_id", "sentence_A", "sentence_B"],
    )

    print(f"Found {len(files)} BLiMP file(s)")
    print(f"Wrote {len(input_rows)} pairwise items to: {input_path}")
    print(f"Wrote answer key to: {answer_path}")


if __name__ == "__main__":
    main()
