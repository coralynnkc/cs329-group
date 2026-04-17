"""
Generate mini evaluation sets for manual LLM baselining.

Task: given a sentence, identify named entities (PER, ORG, LOC, MISC).

Reads eng.testa (CoNLL-2003 validation set) and creates 3 samples x 100 sentences,
randomised (not contiguous — the file is contextually ordered so sequential slices
let zero-shot models learn the tag pattern).

CoNLL-2003 uses IOB1 tagging: entities begin with I- (or B- when two entities of the
same type are adjacent). This script handles both.

Output:
  mini/ner_input.csv    — sentences for the model (no labels)
  mini/ner_answers.csv  — gold entity lists as JSON

Run:
    python ner/scripts/make_mini.py
"""

import os
import csv
import json
import random

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(HERE)
OUT_DIR  = os.path.join(DATA_DIR, "mini")

SOURCE_FILE  = os.path.join(DATA_DIR, "eng.testa")
SAMPLE_SIZE  = 100
SEEDS        = [42, 123, 7]


def read_conll(path):
    """Parse CoNLL-2003 file into list of (tokens, ner_tags) sentence tuples."""
    sentences = []
    tokens, tags = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                if tokens:
                    sentences.append((tokens, tags))
                    tokens, tags = [], []
                continue
            if line.startswith("-DOCSTART-"):
                continue
            parts = line.split()
            tokens.append(parts[0])
            tags.append(parts[-1])   # NER tag is always the last column
    if tokens:
        sentences.append((tokens, tags))
    return sentences


def extract_entities(tokens, tags):
    """
    Extract named entities from IOB1/IOB2 tagged tokens.

    IOB1: I-X continues or starts an entity; B-X starts a new entity of the same
    type as the preceding one. A transition from I-X to I-Y (different type) also
    starts a new entity.
    """
    entities = []
    cur_tokens = []
    cur_label  = None

    for token, tag in zip(tokens, tags):
        if tag == "O":
            if cur_tokens:
                entities.append({"text": " ".join(cur_tokens), "label": cur_label})
                cur_tokens, cur_label = [], None
        elif tag.startswith("B-"):
            if cur_tokens:
                entities.append({"text": " ".join(cur_tokens), "label": cur_label})
            cur_tokens = [token]
            cur_label  = tag[2:]
        elif tag.startswith("I-"):
            label = tag[2:]
            if cur_label == label:
                cur_tokens.append(token)          # continue current entity
            else:
                if cur_tokens:                    # close previous entity
                    entities.append({"text": " ".join(cur_tokens), "label": cur_label})
                cur_tokens = [token]              # start new entity
                cur_label  = label

    if cur_tokens:
        entities.append({"text": " ".join(cur_tokens), "label": cur_label})

    return entities


def write_csv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


print(f"Reading {SOURCE_FILE} ...")
sentences = read_conll(SOURCE_FILE)
print(f"  {len(sentences)} sentences loaded")

input_rows  = [["sample_id", "sentence_id", "sentence"]]
answer_rows = [["sample_id", "sentence_id", "entities"]]

for sample_num, seed in enumerate(SEEDS, start=1):
    rng = random.Random(seed)
    indices = rng.sample(range(len(sentences)), SAMPLE_SIZE)
    for sent_id, idx in enumerate(indices, start=1):
        tokens, tags = sentences[idx]
        sentence = " ".join(tokens)
        entities = extract_entities(tokens, tags)
        input_rows.append([sample_num, sent_id, sentence])
        answer_rows.append([sample_num, sent_id, json.dumps(entities)])

write_csv(input_rows,  os.path.join(OUT_DIR, "ner_input.csv"))
write_csv(answer_rows, os.path.join(OUT_DIR, "ner_answers.csv"))

n = len(input_rows) - 1
print(f"  {n} rows written  ({len(SEEDS)} samples x {SAMPLE_SIZE} sentences)")
print(f"\nDone. Files in {OUT_DIR}/")
print("Upload ner_input.csv to a model, save output as ner_predictions_<model>.csv")
