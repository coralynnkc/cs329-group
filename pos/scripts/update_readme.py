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

TABLE_START = "<!-- results:start -->"
TABLE_END   = "<!-- results:end -->"


def load_summary():
    if not os.path.exists(SUMMARY):
        print(f"No summary file found at {SUMMARY} — run score_baseline.py first.")
        return []
    with open(SUMMARY, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_per_sample(model):
    scores_path = os.path.join(RES_DIR, f"{model}_scores.csv")
    s = {"1": "", "2": "", "3": ""}
    if os.path.exists(scores_path):
        with open(scores_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                s[str(row.get("sample", ""))] = row.get("acc", "")
    return s["1"], s["2"], s["3"]


def build_table(rows):
    lines = [
        "<!-- results:start -->",
        "| Model | Sample 1 | Sample 2 | Sample 3 | Mean |",
        "| ------- | -------- | -------- | -------- | ------ |",
    ]
    for row in rows:
        model = row.get("model", "")
        mean  = row.get("mean", "")
        s1, s2, s3 = load_per_sample(model)
        lines.append(f"| {model} | {s1} | {s2} | {s3} | {mean} |")
    lines.append("<!-- results:end -->")
    return "\n".join(lines)


def update_readme(rows):
    with open(README, encoding="utf-8") as f:
        content = f.read()

    start_idx = content.find(TABLE_START)
    end_idx   = content.find(TABLE_END)

    if start_idx == -1 or end_idx == -1:
        print("Could not find results table markers in README.md.")
        return

    new_table = build_table(rows)
    content = content[:start_idx] + new_table + content[end_idx + len(TABLE_END):]

    with open(README, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"README.md updated with {len(rows)} model(s).")
    print(new_table)


rows = load_summary()
if rows:
    update_readme(rows)
