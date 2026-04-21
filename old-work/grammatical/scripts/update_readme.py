"""
Update the results table in README.md from results/summary.csv.

Run after scoring one or more models:
    python scripts/update_readme.py
"""

import os
import csv

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(HERE)
RES_DIR  = os.path.join(DATA_DIR, "results")
README   = os.path.join(DATA_DIR, "README.md")

SUMMARY  = os.path.join(RES_DIR, "summary.csv")
TABLE_START = "| Model | Sample 1 | Sample 2 | Sample 3 | Mean |"
TABLE_END   = "*Run `python scripts/update_readme.py` after scoring to populate this table.*"


def load_summary():
    if not os.path.exists(SUMMARY):
        print(f"No summary file found at {SUMMARY} — run score_baseline.py first.")
        return []
    with open(SUMMARY, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_table(rows):
    lines = [
        "| Model | Sample 1 | Sample 2 | Sample 3 | Mean |",
        "| ------- | -------- | -------- | -------- | ------ |",
    ]
    for row in rows:
        model = row.get("model", "")
        mean  = row.get("mean", "")
        rng   = row.get("range", "")

        # load per-sample scores from <model>_scores.csv if available
        scores_path = os.path.join(RES_DIR, f"{model}_scores.csv")
        s1 = s2 = s3 = ""
        if os.path.exists(scores_path):
            with open(scores_path, encoding="utf-8") as f:
                for sr in csv.DictReader(f):
                    sample_num = sr.get("sample", "")
                    acc = sr.get("acc", "")
                    if sample_num == "1":
                        s1 = acc
                    elif sample_num == "2":
                        s2 = acc
                    elif sample_num == "3":
                        s3 = acc

        lines.append(f"| {model} | {s1} | {s2} | {s3} | {mean} |")
    return "\n".join(lines)


def update_readme(table_str):
    with open(README, encoding="utf-8") as f:
        content = f.read()

    start_idx = content.find(TABLE_START)
    end_idx   = content.find(TABLE_END)

    if start_idx == -1 or end_idx == -1:
        print("Could not find results table markers in README.md — check TABLE_START/TABLE_END.")
        return

    # find end of the table block (the line before TABLE_END)
    before = content[:start_idx]
    after  = content[end_idx:]

    new_content = before + table_str + "\n\n" + after
    with open(README, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"README.md updated with {len(rows)} model(s).")


rows = load_summary()
if rows:
    table_str = build_table(rows)
    update_readme(table_str)
    print(table_str)
