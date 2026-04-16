#!/usr/bin/env python3
"""
Refresh the README tables from results/cola_summary.csv and results/blimp_summary.csv.
"""

import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
README = os.path.join(ROOT, "README.md")
COLA_SUMMARY = os.path.join(ROOT, "results", "cola_summary.csv")
BLIMP_SUMMARY = os.path.join(ROOT, "results", "blimp_summary.csv")

COLA_START = "## CoLA Results Table"
COLA_END = "## BLiMP Results Table"
BLIMP_START = "## BLiMP Results Table"
BLIMP_END = "## Suggested next upgrade"


def load_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_cola_table(rows):
    lines = [
        "| Model | Prompt | Split | N | Accuracy | MCC | Precision(1) | Recall(1) | F1(1) | Coverage | Refusal rate | Invalid rate |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {model} | {prompt} | {split} | {n} | {accuracy} | {mcc} | {precision_1} | {recall_1} | {f1_1} | {coverage} | {refusal_rate} | {invalid_rate} |".format(
                **row
            )
        )
    return "\n".join(lines)


def build_blimp_table(rows):
    lines = [
        "| Model | Prompt | N | Accuracy | Coverage | Refusal rate | Invalid rate |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {model} | {prompt} | {n} | {accuracy} | {coverage} | {refusal_rate} | {invalid_rate} |".format(
                **row
            )
        )
    return "\n".join(lines)


def replace_block(content, start_marker, end_marker, replacement):
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        raise ValueError(f"Could not find block markers: {start_marker} ... {end_marker}")
    before = content[:start_idx]
    after = content[end_idx:]
    return before + replacement + "\n\n" + after


def main():
    with open(README, encoding="utf-8") as f:
        content = f.read()

    cola_rows = load_csv(COLA_SUMMARY)
    blimp_rows = load_csv(BLIMP_SUMMARY)

    cola_block = "## CoLA Results Table\n\n" + build_cola_table(cola_rows)
    blimp_block = "## BLiMP Results Table\n\n" + build_blimp_table(blimp_rows)

    content = replace_block(content, COLA_START, COLA_END, cola_block)
    content = replace_block(content, BLIMP_START, BLIMP_END, blimp_block)

    with open(README, "w", encoding="utf-8") as f:
        f.write(content)

    print("README.md updated.")


if __name__ == "__main__":
    main()
