"""
Convert the narnia manual annotations to character-cluster format for coreference evaluation.

Input:  narnia/man_annotated_narnia200 - Sheet1.csv
Output: coref/data/narnia_coref_annotated.csv

Each output row represents one sentence:
    sentence_id, sentence, clusters
where clusters is a JSON list of {"character": "<canonical_name>", "mentions": ["<span>", ...]} objects.
Characters with multiple surface mentions in the same sentence are grouped.
Sentences with no annotated characters get clusters = [].

Run:
    python coref/scripts/convert_annotations.py
"""

import os
import csv
import json
from collections import defaultdict, OrderedDict

HERE       = os.path.dirname(os.path.abspath(__file__))
COREF_DIR  = os.path.dirname(HERE)
REPO_ROOT  = os.path.dirname(COREF_DIR)
SOURCE     = os.path.join(REPO_ROOT, "narnia", "man_annotated_narnia200 - Sheet1.csv")
OUT_DIR    = os.path.join(COREF_DIR, "data")
OUT_FILE   = os.path.join(OUT_DIR, "narnia_coref_annotated.csv")


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)

    # sentence_id -> {"text": str, "clusters": {canonical_character: [mention, ...]}}
    by_sent = OrderedDict()

    with open(SOURCE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid       = row["sentence_id"].strip()
            text      = row["sentence_text"].strip()
            mention   = row["character_mention"].strip()
            canonical = row["canonical_character"].strip()

            if sid not in by_sent:
                by_sent[sid] = {"text": text, "clusters": defaultdict(list)}
            elif not by_sent[sid]["text"] and text:
                by_sent[sid]["text"] = text

            # Only add if both mention and canonical character are present
            if mention and canonical:
                # Avoid duplicate mentions for the same canonical character in one sentence
                if mention not in by_sent[sid]["clusters"][canonical]:
                    by_sent[sid]["clusters"][canonical].append(mention)

    rows = [["sentence_id", "sentence", "clusters"]]
    skipped = 0
    for sid, data in by_sent.items():
        if not data["text"]:
            skipped += 1
            continue
        clusters = [
            {"character": char, "mentions": mentions}
            for char, mentions in data["clusters"].items()
        ]
        rows.append([sid, data["text"], json.dumps(clusters)])

    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    n = len(rows) - 1
    print(f"Converted {n} sentences → {OUT_FILE}")
    if skipped:
        print(f"  (skipped {skipped} sentence(s) with empty text)")


if __name__ == "__main__":
    convert()
