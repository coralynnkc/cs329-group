import csv
import random
import json

INPUT_FILE = "eng.testb"
OUTPUT_FILE = "conll2003_100_eval.csv"
MAX_SENTENCES = 100
SEED = 42  # reproducibility


def read_conll(path):
    sentences = []
    labels = []

    tokens = []
    tags = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                if tokens:
                    sentences.append(tokens)
                    labels.append(tags)
                    tokens, tags = [], []
                continue

            if line.startswith("-DOCSTART-"):
                continue

            parts = line.split()
            tokens.append(parts[0])
            tags.append(parts[-1])

    return sentences, labels


def extract_entities(tokens, tags):
    entities = []
    current_tokens = []
    current_label = None

    for token, tag in zip(tokens, tags):
        if tag.startswith("B-"):
            if current_tokens:
                entities.append({
                    "text": " ".join(current_tokens),
                    "label": current_label
                })
            current_tokens = [token]
            current_label = tag[2:]

        elif tag.startswith("I-") and current_tokens:
            current_tokens.append(token)

        else:
            if current_tokens:
                entities.append({
                    "text": " ".join(current_tokens),
                    "label": current_label
                })
                current_tokens = []
                current_label = None

    if current_tokens:
        entities.append({
            "text": " ".join(current_tokens),
            "label": current_label
        })

    return entities


# Load data
sentences, labels = read_conll(INPUT_FILE)

# 🔥 Random sample
random.seed(SEED)
indices = random.sample(range(len(sentences)), MAX_SENTENCES)

# Write CSV
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "sentence", "gold_entities"])

    for i, idx in enumerate(indices):
        tokens = sentences[idx]
        tags = labels[idx]

        sentence = " ".join(tokens)
        entities = extract_entities(tokens, tags)

        writer.writerow([i, sentence, json.dumps(entities)])

print(f"Saved {MAX_SENTENCES} RANDOM sentences to {OUTPUT_FILE}")