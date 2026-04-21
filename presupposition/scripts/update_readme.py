"""
Update the results table in README.md from results/summary.csv.

Run after scoring one or more models:
    python presupposition/scripts/update_readme.py
"""

import os
import csv

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(HERE)
RES_DIR  = os.path.join(DATA_DIR, "results")
README   = os.path.join(DATA_DIR, "README.md")
SUMMARY  = os.path.join(RES_DIR, "summary.csv")

RESULTS_START = "<!-- results:start -->"
RESULTS_END   = "<!-- results:end -->"


def load_summary():
    if not os.path.exists(SUMMARY):
        print(f"No summary file found at {SUMMARY} — run score_baseline.py first.")
        return []
    with open(SUMMARY, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_per_sample(model):
    scores_path = os.path.join(RES_DIR, f"{model}_scores.csv")
    acc = {"1": "", "2": "", "3": ""}
    f1  = {"1": "", "2": "", "3": ""}
    if os.path.exists(scores_path):
        with open(scores_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                s = str(row.get("sample", ""))
                if s in acc:
                    acc[s] = row.get("acc", "")
                    f1[s]  = row.get("macro_f1", "")
    return acc, f1


def build_summary_table(rows):
    lines = [
        RESULTS_START,
        "| Model | S1 Acc | S2 Acc | S3 Acc | Mean Acc | Mean Macro-F1 |",
        "| ----- | ------ | ------ | ------ | -------- | ------------- |",
    ]
    for row in rows:
        model    = row.get("model", "")
        mean_acc = row.get("mean_acc", "")
        mean_f1  = row.get("mean_f1", "")
        acc, _   = load_per_sample(model)
        lines.append(
            f"| {model} | {acc['1']} | {acc['2']} | {acc['3']} "
            f"| {mean_acc} | {mean_f1} |"
        )
    lines.append(RESULTS_END)
    return "\n".join(lines)


def replace_block(content, start_marker, end_marker, new_block):
    start_idx = content.find(start_marker)
    end_idx   = content.find(end_marker)
    if start_idx == -1 or end_idx == -1:
        print(f"Could not find markers in README.md — check {start_marker!r} / {end_marker!r}.")
        return content
    return content[:start_idx] + new_block + content[end_idx + len(end_marker):]


def update_readme(rows):
    with open(README, encoding="utf-8") as f:
        content = f.read()

    table = build_summary_table(rows)
    content = replace_block(content, RESULTS_START, RESULTS_END, table)

    with open(README, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"README.md updated with {len(rows)} model(s).")
    print("\n--- results table ---")
    print(table)


rows = load_summary()
if rows:
    update_readme(rows)
