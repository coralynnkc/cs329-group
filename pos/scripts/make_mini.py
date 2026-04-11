"""
Generate mini evaluation sets for manual LLM baselining.

Task: given a sentence, predict the Universal Dependencies POS tag for each token.

Reads en_ewt-ud-train.conllu and creates 3 samples x 100 sentences = 300 sentences,
stratified by sentence length.

Output:
  mini/en_input.csv     — sentences for the model
  mini/en_answers.csv   — gold POS tag sequences

Run:
    python scripts/make_mini.py
"""

import os
import csv
import random
from collections import defaultdict

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(HERE)
OUT_DIR  = os.path.join(DATA_DIR, "mini")

SAMPLE_SIZE = 100
SEEDS = [42, 123, 7]

TRAIN_FILE = os.path.join(DATA_DIR, "en_ewt-ud-train.conllu")


def read_sentences(path):
    """Parse a .conllu file into a list of (word, upos) sentence lists."""
    sentences = []
    current = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("#") or line == "":
                if line == "" and current:
                    sentences.append(current)
                    current = []
                continue
            parts = line.split("\t")
            # skip multi-word tokens (ID like "1-2") and empty nodes ("1.1")
            if "-" in parts[0] or "." in parts[0]:
                continue
            word = parts[1]
            upos = parts[3]
            current.append((word, upos))
    if current:
        sentences.append(current)
    return sentences


def length_bucket(sent):
    n = len(sent)
    if n <= 10:
        return "short"
    elif n <= 20:
        return "medium"
    return "long"


def stratified_sample(sentences, n, seed):
    by_bucket = defaultdict(list)
    for sent in sentences:
        by_bucket[length_bucket(sent)].append(sent)

    rng = random.Random(seed)
    buckets = sorted(by_bucket.keys())
    per_bucket = max(1, n // len(buckets))

    sample = []
    for bucket in buckets:
        pool = list(by_bucket[bucket])
        rng.shuffle(pool)
        sample.extend(pool[:per_bucket])

    # top up to exactly n if needed
    used = set(id(s) for s in sample)
    remainder = [s for s in sentences if id(s) not in used]
    rng.shuffle(remainder)
    sample.extend(remainder[:n - len(sample)])

    rng.shuffle(sample)
    return sample[:n]


def write_csv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)


os.makedirs(OUT_DIR, exist_ok=True)

print(f"Reading {TRAIN_FILE} ...")
sentences = read_sentences(TRAIN_FILE)
print(f"  {len(sentences)} sentences loaded")

input_rows  = [["sample_id", "sentence_id", "words"]]
answer_rows = [["sample_id", "sentence_id", "tags"]]

for sample_num, seed in enumerate(SEEDS, start=1):
    sample = stratified_sample(sentences, SAMPLE_SIZE, seed)
    for sent_id, sent in enumerate(sample, start=1):
        words = " ".join(w for w, _ in sent)
        tags  = " ".join(t for _, t in sent)
        input_rows.append([sample_num, sent_id, words])
        answer_rows.append([sample_num, sent_id, tags])

write_csv(input_rows,  os.path.join(OUT_DIR, "en_input.csv"))
write_csv(answer_rows, os.path.join(OUT_DIR, "en_answers.csv"))

print(f"  {len(input_rows)-1} rows written  ({len(SEEDS)} samples x {SAMPLE_SIZE} sentences)")
print(f"\nDone. Files in {OUT_DIR}/")
print("Upload en_input.csv to a model, save output as en_predictions_<model>.csv")
