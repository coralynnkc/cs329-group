# Label Normalization

This document specifies how gold labels from external sources map to the normalized
label scheme used in srijon-2.0 `full/` files.

---

## Presuppositions

### Normalized label scheme

All presupposition `full/` files use three-letter string labels in `gold_label`:

| Normalized | Meaning |
|-----------|---------|
| `E` | Entailment — the hypothesis follows from the premise |
| `N` | Neutral — the hypothesis is neither confirmed nor denied |
| `C` | Contradiction — the hypothesis contradicts the premise |

Model output (`model_label`) should also use `E`, `N`, `C`.

### Source-specific label encodings

#### English (CONFER dataset)
CONFER uses string labels directly compatible with the normalized scheme:

| CONFER | Normalized |
|--------|-----------|
| `E` or `entailment` | `E` |
| `N` or `neutral` | `N` |
| `C` or `contradiction` | `C` |

#### French, German, Hindi, Russian, Vietnamese (XNLI)
XNLI uses integer labels:

| XNLI integer | Meaning | Normalized |
|-------------|---------|-----------|
| `0` | Entailment | `E` |
| `1` | Neutral | `N` |
| `2` | Contradiction | `C` |

**Mapping snippet (Python):**
```python
XNLI_MAP = {0: "E", 1: "N", 2: "C"}
df["gold_label"] = df["xnli_gold"].map(XNLI_MAP)
```

Do NOT silently remap without verifying against the XNLI documentation for the
specific split (test vs. validation) you are using.

### Label distribution notes

From the original `/srijon` evaluation:
- English accuracy: 45.46% (6,982 rows)
- German accuracy: 45.68%
- French accuracy: 44.99%
- Russian accuracy: 40.41%
- Hindi accuracy: 41.43%
- Vietnamese accuracy: 52.03%

All accuracies are well above chance for a 3-class task (33.3%), suggesting moderate
but imperfect model calibration. Label distribution in XNLI is roughly balanced across
E/N/C — verify this before assuming balanced accuracy is meaningful.

---

## Pronoun Resolution

The pronoun resolution task is binary (two options): `option_a` or `option_b`.

Normalized `model_prediction` values: `option_a` or `option_b` (string).

For English (no option columns), the `model_prediction` should be the exact text
of the referent noun phrase as it appears in the sentence.

Gold labels (`correct` column):
- `1` — model prediction matches gold referent
- `0` — model prediction does not match gold referent

---

## Lemmatization

The lemmatization task is open-ended: the model outputs a lemma string.

Scoring rule:
```
correct = 1  if  model_lemma.strip().lower() == gold_lemma.strip().lower()
correct = 0  otherwise
```

When one word form has multiple valid gold lemmas (e.g. homographs), mark `correct=1`
if the model output matches ANY valid gold lemma. Document the join logic in the
scoring script.

---

## Accuracy formula

For all tasks:

```
accuracy = sum(correct) / len(correct)   [excluding rows where correct is NaN]
```

Report accuracy:
- Overall (all rows)
- Per-language (for multilingual tasks)
- Per gold label class (for presuppositions: E/N/C breakdown)
