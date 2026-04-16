#!/usr/bin/env python3
"""
Build a representative CoLA sample with matched input/answer CSVs.

Compared with make_cola_eval.py, this sampler tries to preserve both:
1) label balance (acceptable vs unacceptable), and
2) source_code distribution within each label.

Examples:
    python scripts/make_cola_sample.py --split in_domain_dev
    python scripts/make_cola_sample.py --split out_of_domain_dev --sample-size 100 --seed 7
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import random
from collections import defaultdict
from typing import Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SIBLING_GRAMMATICAL = os.path.normpath(os.path.join(ROOT, "..", "grammatical"))
OUT_DIR = os.path.join(ROOT, "mini")

SPLIT_MAP = {
    "in_domain_train": os.path.join(SIBLING_GRAMMATICAL, "in_domain_train.tsv"),
    "in_domain_dev": os.path.join(SIBLING_GRAMMATICAL, "in_domain_dev.tsv"),
    "out_of_domain_dev": os.path.join(SIBLING_GRAMMATICAL, "out_of_domain_dev.tsv"),
}


def read_tsv(path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
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


def largest_remainder_quota(counts: Dict[str, int], target_total: int) -> Dict[str, int]:
    """Allocate integer quotas proportional to counts using largest remainder."""
    total = sum(counts.values())
    if total == 0 or target_total <= 0:
        return {k: 0 for k in counts}

    raw = {k: (v / total) * target_total for k, v in counts.items()}
    base = {k: min(counts[k], int(math.floor(raw[k]))) for k in counts}
    allocated = sum(base.values())

    # Hand out the remaining slots by largest remainder, respecting capacity.
    remainders = sorted(
        counts.keys(),
        key=lambda k: (raw[k] - math.floor(raw[k]), counts[k]),
        reverse=True,
    )
    i = 0
    while allocated < target_total and remainders:
        key = remainders[i % len(remainders)]
        if base[key] < counts[key]:
            base[key] += 1
            allocated += 1
        i += 1
        # Avoid infinite loops if every bucket is saturated.
        if i > len(remainders) * (target_total + 1):
            break

    return base


def sample_representative(rows: List[Dict[str, str]], sample_size: int, seed: int) -> List[Dict[str, str]]:
    if sample_size > len(rows):
        raise ValueError(f"sample_size={sample_size} exceeds available rows={len(rows)}")

    rng = random.Random(seed)

    # Group rows by label, then by source_code within label.
    by_label_source: Dict[str, Dict[str, List[Dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        by_label_source[row["label"]][row["source_code"]].append(row)

    # Shuffle within each bucket once for reproducibility.
    for label_buckets in by_label_source.values():
        for bucket in label_buckets.values():
            rng.shuffle(bucket)

    label_counts = {label: sum(len(bucket) for bucket in buckets.values()) for label, buckets in by_label_source.items()}
    label_quota = largest_remainder_quota(label_counts, sample_size)

    selected: List[Dict[str, str]] = []

    # First pass: allocate within each label proportionally by source_code.
    for label, buckets in sorted(by_label_source.items()):
        source_counts = {source: len(bucket) for source, bucket in buckets.items()}
        source_quota = largest_remainder_quota(source_counts, label_quota[label])
        for source, quota in source_quota.items():
            selected.extend(buckets[source][:quota])

    # Second pass: if rounding/capacity left us short, fill from leftovers preserving label first.
    if len(selected) < sample_size:
        selected_ids = {row["id"] for row in selected}

        # Prefer leftovers from labels that are below their quota.
        current_by_label = defaultdict(int)
        for row in selected:
            current_by_label[row["label"]] += 1

        for label in sorted(by_label_source.keys()):
            needed = label_quota[label] - current_by_label[label]
            if needed <= 0:
                continue
            leftovers = []
            for source in sorted(by_label_source[label].keys()):
                leftovers.extend([r for r in by_label_source[label][source] if r["id"] not in selected_ids])
            rng.shuffle(leftovers)
            take = leftovers[:needed]
            selected.extend(take)
            selected_ids.update(r["id"] for r in take)

    # Final backfill from any remaining rows if still short.
    if len(selected) < sample_size:
        selected_ids = {row["id"] for row in selected}
        leftovers = [row for row in rows if row["id"] not in selected_ids]
        rng.shuffle(leftovers)
        selected.extend(leftovers[: sample_size - len(selected)])

    rng.shuffle(selected)
    return selected[:sample_size]


def write_csv(path: str, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: List[Dict[str, str]]) -> str:
    label_counts = defaultdict(int)
    source_counts = defaultdict(int)
    for row in rows:
        label_counts[row["label"]] += 1
        source_counts[row["source_code"]] += 1

    top_sources = sorted(source_counts.items(), key=lambda x: (-x[1], x[0]))[:10]
    parts = [
        "Label counts: " + ", ".join(f"{label}={count}" for label, count in sorted(label_counts.items())),
        "Top sources: " + ", ".join(f"{src}={count}" for src, count in top_sources),
    ]
    return " | ".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", required=True, choices=sorted(SPLIT_MAP.keys()))
    parser.add_argument("--sample-size", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    source_path = SPLIT_MAP[args.split]
    if not os.path.exists(source_path):
        raise FileNotFoundError(
            f"Could not find {source_path}. This script expects the sibling folder '../grammatical/' to exist."
        )

    rows = read_tsv(source_path)
    sample_rows = sample_representative(rows, args.sample_size, args.seed)

    input_rows = [{"id": i, "sentence": row["sentence"]} for i, row in enumerate(sample_rows, start=1)]
    answer_rows = [
        {
            "id": i,
            "label": row["label"],
            "source_code": row["source_code"],
            "original_id": row["id"],
            "sentence": row["sentence"],
        }
        for i, row in enumerate(sample_rows, start=1)
    ]

    input_path = os.path.join(OUT_DIR, f"cola_{args.split}_sample{args.sample_size}_input.csv")
    answer_path = os.path.join(OUT_DIR, f"cola_{args.split}_sample{args.sample_size}_answers.csv")

    write_csv(input_path, input_rows, ["id", "sentence"])
    write_csv(answer_path, answer_rows, ["id", "label", "source_code", "original_id", "sentence"])

    print(f"Loaded {len(rows)} rows from {source_path}")
    print(f"Sampled {len(sample_rows)} rows with seed={args.seed}")
    print("Full split summary:")
    print("  " + summarize(rows))
    print("Sample summary:")
    print("  " + summarize(sample_rows))
    print(f"Wrote: {input_path}")
    print(f"Wrote: {answer_path}")


if __name__ == "__main__":
    main()
