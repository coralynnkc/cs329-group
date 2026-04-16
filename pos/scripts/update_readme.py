"""
Update the results tables in README.md from results/summary.csv and per-model tag F1 files.

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

# All 17 UD tags in a stable order
UD_TAGS = ["ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ",
           "NOUN", "NUM", "PART", "PRON", "PROPN", "PUNCT", "SCONJ",
           "SYM", "VERB", "X"]

RESULTS_START  = "<!-- results:start -->"
RESULTS_END    = "<!-- results:end -->"
TAG_F1_START   = "<!-- tag-f1:start -->"
TAG_F1_END     = "<!-- tag-f1:end -->"


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


def load_tag_f1(model):
    """Return {tag: f1} for a model, or {} if file missing."""
    path = os.path.join(RES_DIR, f"{model}_tag_f1.csv")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return {row["tag"]: row["f1"] for row in csv.DictReader(f)}


def build_summary_table(rows):
    lines = [
        RESULTS_START,
        "| Model | Sample 1 | Sample 2 | Sample 3 | Mean Acc | Macro-F1 |",
        "| ------- | -------- | -------- | -------- | -------- | -------- |",
    ]
    for row in rows:
        model    = row.get("model", "")
        mean_acc = row.get("mean_acc", "")
        mean_f1  = row.get("mean_f1", "")
        s1, s2, s3 = load_per_sample(model)
        lines.append(f"| {model} | {s1} | {s2} | {s3} | {mean_acc} | {mean_f1} |")
    lines.append(RESULTS_END)
    return "\n".join(lines)


def build_tag_f1_table(rows):
    models = [row["model"] for row in rows]
    tag_data = {m: load_tag_f1(m) for m in models}

    # Collect all tags seen across models, fall back to UD_TAGS order
    seen_tags = set()
    for d in tag_data.values():
        seen_tags.update(d.keys())
    tags = [t for t in UD_TAGS if t in seen_tags]
    # Append any unexpected tags at the end
    tags += sorted(seen_tags - set(UD_TAGS))

    header = "| Tag | " + " | ".join(models) + " |"
    sep    = "| --- | " + " | ".join(["---"] * len(models)) + " |"
    lines  = [TAG_F1_START, header, sep]
    for tag in tags:
        cells = [tag_data[m].get(tag, "") for m in models]
        lines.append("| " + tag + " | " + " | ".join(cells) + " |")
    lines.append(TAG_F1_END)
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

    summary_table = build_summary_table(rows)
    content = replace_block(content, RESULTS_START, RESULTS_END, summary_table)

    tag_table = build_tag_f1_table(rows)
    content = replace_block(content, TAG_F1_START, TAG_F1_END, tag_table)

    with open(README, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"README.md updated with {len(rows)} model(s).")
    print("\n--- summary table ---")
    print(summary_table)
    print("\n--- per-tag F1 table ---")
    print(tag_table)


rows = load_summary()
if rows:
    update_readme(rows)
