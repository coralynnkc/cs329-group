"""
Update the results table in README.MD from results/summary.csv.

Run after scoring one or more models:
    python narnia/scripts/update_readme.py
"""

import os
import csv

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(HERE)
RES_DIR  = os.path.join(DATA_DIR, "results")
README   = os.path.join(DATA_DIR, "README.MD")
SUMMARY  = os.path.join(RES_DIR, "summary.csv")

RESULTS_START = "<!-- results:start -->"
RESULTS_END   = "<!-- results:end -->"


def load_summary():
    if not os.path.exists(SUMMARY):
        print(f"No summary file found at {SUMMARY} — run score_baseline.py first.")
        return []
    with open(SUMMARY, encoding="utf-8") as f:
        return list(csv.DictReader(f))



def build_summary_table(rows):
    lines = [
        RESULTS_START,
        "| Model | Precision | Recall | F1 |",
        "| ----- | --------- | ------ | -- |",
    ]
    for row in rows:
        model     = row.get("model", "")
        precision = row.get("precision", "")
        recall    = row.get("recall", "")
        f1        = row.get("f1", "")
        lines.append(f"| {model} | {precision} | {recall} | {f1} |")
    lines.append(RESULTS_END)
    return "\n".join(lines)


def replace_block(content, start_marker, end_marker, new_block):
    start_idx = content.find(start_marker)
    end_idx   = content.find(end_marker)
    if start_idx == -1 or end_idx == -1:
        print(f"Could not find markers {start_marker!r} / {end_marker!r} in README.MD.")
        return content
    return content[:start_idx] + new_block + content[end_idx + len(end_marker):]


def update_readme(rows):
    with open(README, encoding="utf-8") as f:
        content = f.read()

    summary_table = build_summary_table(rows)
    content = replace_block(content, RESULTS_START, RESULTS_END, summary_table)

    with open(README, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"README.MD updated with {len(rows)} model(s).")
    print("\n--- results table ---")
    print(summary_table)


rows = load_summary()
if rows:
    update_readme(rows)
