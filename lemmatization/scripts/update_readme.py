"""
Update the results tables in README.md from results/summary.csv.

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

ARGS_START = "<!-- results-args:start -->"
ARGS_END   = "<!-- results-args:end -->"
SEG_START  = "<!-- results-seg:start -->"
SEG_END    = "<!-- results-seg:end -->"


def load_summary():
    if not os.path.exists(SUMMARY):
        print(f"No summary file found at {SUMMARY} — run score_baseline.py first.")
        return []
    with open(SUMMARY, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_per_sample(model, prefix):
    scores_path = os.path.join(RES_DIR, f"{model}_scores.csv")
    s = {"1": "", "2": "", "3": ""}
    if os.path.exists(scores_path):
        with open(scores_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("file", "") == prefix:
                    s[str(row.get("sample", ""))] = row.get("acc", "")
    return s["1"], s["2"], s["3"]


def build_table(rows, prefix, acc_key, ned_key, start_marker, end_marker):
    lines = [
        start_marker,
        "| Model | Sample 1 | Sample 2 | Sample 3 | Mean Acc | Mean NED |",
        "| ------- | -------- | -------- | -------- | -------- | -------- |",
    ]
    for row in rows:
        model    = row.get("model", "")
        mean_acc = row.get(acc_key, "")
        mean_ned = row.get(ned_key, "")
        s1, s2, s3 = load_per_sample(model, prefix)
        lines.append(f"| {model} | {s1} | {s2} | {s3} | {mean_acc} | {mean_ned} |")
    lines.append(end_marker)
    return "\n".join(lines)


def replace_block(content, start_marker, end_marker, new_block):
    start_idx = content.find(start_marker)
    end_idx   = content.find(end_marker)
    if start_idx == -1 or end_idx == -1:
        print(f"Could not find markers {start_marker!r} / {end_marker!r} in README.md.")
        return content
    return content[:start_idx] + new_block + content[end_idx + len(end_marker):]


def update_readme(rows):
    with open(README, encoding="utf-8") as f:
        content = f.read()

    args_table = build_table(rows, "args", "args_mean_acc", "args_mean_ned", ARGS_START, ARGS_END)
    content = replace_block(content, ARGS_START, ARGS_END, args_table)

    seg_table = build_table(rows, "seg", "seg_mean_acc", "seg_mean_ned", SEG_START, SEG_END)
    content = replace_block(content, SEG_START, SEG_END, seg_table)

    with open(README, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"README.md updated with {len(rows)} model(s).")
    print("\n--- args table ---")
    print(args_table)
    print("\n--- seg table ---")
    print(seg_table)


rows = load_summary()
if rows:
    update_readme(rows)
