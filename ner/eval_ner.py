import pandas as pd
import json

gold = pd.read_csv("gold_clean.csv")
pred = pd.read_csv("pred_clean.csv")

def parse(x):
    return json.loads(x)

tp = fp = fn = 0

for i in range(len(gold)):
    g = set((e["text"], e["label"]) for e in parse(gold.loc[i, "gold_entities"]))
    p = set((e["text"], e["label"]) for e in parse(pred.loc[i, "predicted_entities"]))

    tp += len(g & p)
    fp += len(p - g)
    fn += len(g - p)

precision = tp / (tp + fp) if tp + fp else 0
recall = tp / (tp + fn) if tp + fn else 0
f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0

print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1:        {f1:.4f}")