# Prompt Template — Lemmatization

## Task description

Given an inflected word form, predict its **lemma** (dictionary/base form).
The dataset is English only (UniMorph English).

---

## Inference schema (from `inference/` CSVs)

| Column | Description |
|--------|-------------|
| `item_id` | Stable row identifier (e.g. `lm_en_000042`) |
| `word` | Inflected word form (e.g. `running`, `flies`, `ran`) |

---

## Prompt template (zero-shot)

```
You are a linguistics expert. Your task is to find the lemma (dictionary base form) of a given word.

The lemma is the canonical uninflected form you would look up in a dictionary.
Examples: "running" → "run", "flies" → "fly", "better" → "good", "ran" → "run"

Respond with ONLY the lemma. No explanation, no punctuation, no extra words.

---
Word: {word}
Lemma:
```

---

## Prompt template (with morphological guidance)

```
You are a morphology expert. Given an inflected English word form, return its base lemma.

Rules to follow:
- Verbs: return the infinitive (e.g. "running" → "run", "flies" → "fly")
- Nouns: return the singular (e.g. "geese" → "goose", "boxes" → "box")
- Adjectives: return the positive degree (e.g. "better" → "good", "happier" → "happy")
- For compound or unfamiliar words, apply standard English morphological rules

Respond with ONLY the lemma word, lowercase. No explanation.

---
Word: {word}
Lemma:
```

---

## Few-shot variant

```
Examples:
Word: running → Lemma: run
Word: geese → Lemma: goose
Word: happier → Lemma: happy
Word: boxes → Lemma: box
Word: went → Lemma: go

Now answer:
Word: {word}
Lemma:
```

---

## Output format for batch CSV scoring

After collecting model responses, merge into the `full/` CSV:

- `model_lemma` — raw model output  
- `gold_lemma` — ground truth from UniMorph (must be joined externally; see notes)  
- `correct` — 1 if `model_lemma.lower().strip()` == `gold_lemma.lower().strip()`, else 0

---

## Important notes on gold labels

The `full/` CSV has a placeholder `gold_lemma` column that is **empty**.
The UniMorph English corpus stores (inflected_form, lemma, morphological_features) triples.
Gold lemmas must be joined from the full UniMorph dataset using `word` as the key.

One inflected form may map to multiple lemmas (e.g. homographs). When joining, keep all
gold lemmas and mark `correct=1` if the model matches any of them.

The original `/srijon/scripts/English_lemma_benchmarked.ipynb` contains an example
join pipeline using the UniMorph data.
