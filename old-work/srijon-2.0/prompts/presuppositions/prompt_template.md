# Prompt Template — Presupposition / NLI Labeling

## Task description

Given a `premise` and a `hypothesis`, classify the logical relationship between them.
This is a Natural Language Inference (NLI) task focused on presupposition projection.

---

## Inference schema (from `inference/` CSVs)

| Column | Description |
|--------|-------------|
| `item_id` | Stable row identifier (e.g. `ps_fr_000042`) |
| `premise` | The source sentence establishing a context |
| `hypothesis` | The statement to evaluate against the premise |

---

## Label scheme

| Label | Meaning | XNLI numeric | CONFER string |
|-------|---------|--------------|---------------|
| Entailment | The hypothesis follows from the premise | 0 | E |
| Neutral | The hypothesis is neither confirmed nor denied | 1 | N |
| Contradiction | The hypothesis contradicts the premise | 2 | C |

Store model outputs using the three-letter strings `E`, `N`, `C` in `model_label` column.

---

## Prompt template (zero-shot)

```
You are a language analysis expert specializing in natural language inference.

Given a premise and a hypothesis, classify the relationship as one of:
  E — Entailment: the hypothesis is necessarily true given the premise
  N — Neutral: the hypothesis may or may not be true; the premise neither confirms nor denies it
  C — Contradiction: the hypothesis is necessarily false given the premise

Respond with ONLY the single letter E, N, or C. No explanation.

---
Premise: {premise}
Hypothesis: {hypothesis}
---
Label:
```

---

## Prompt template (with brief definitions — recommended for multilingual)

```
You are a language analysis expert. Your task is to determine the logical relationship between two sentences.

Label the relationship using one of three options:
  E (Entailment)    — If the premise is true, the hypothesis must also be true.
  N (Neutral)       — The premise does not conclusively prove or disprove the hypothesis.
  C (Contradiction) — If the premise is true, the hypothesis cannot be true.

Answer with ONLY the letter E, N, or C.

---
Premise: {premise}
Hypothesis: {hypothesis}
---
Answer:
```

---

## Few-shot variant

```
Examples:

Premise: The cat sat on the mat.
Hypothesis: There is a cat.
Label: E

Premise: The cat sat on the mat.
Hypothesis: The cat is sleeping.
Label: N

Premise: The cat sat on the mat.
Hypothesis: There is no cat.
Label: C

---
Now label this pair:

Premise: {premise}
Hypothesis: {hypothesis}
Label:
```

---

## Output format for batch CSV scoring

After collecting model responses, merge into the `full/` CSV:

- `model_label` — raw model output (E / N / C)  
- `gold_label` — ground truth from XNLI or CONFER (populate externally)  
- `correct` — 1 if `model_label` == `gold_label`, else 0

Compute accuracy per language and per label class for breakdown.

---

## Data sources by language

| Language | Dataset | Expected label encoding |
|----------|---------|------------------------|
| en | CONFER (English presupposition corpus) | E / N / C |
| fr | XNLI French | 0 / 1 / 2 (→ E / N / C) |
| de | XNLI German | 0 / 1 / 2 (→ E / N / C) |
| hi | XNLI Hindi | 0 / 1 / 2 (→ E / N / C) |
| ru | XNLI Russian | 0 / 1 / 2 (→ E / N / C) |
| vi | XNLI Vietnamese | 0 / 1 / 2 (→ E / N / C) |

See `docs/label_normalization.md` for the full mapping specification.
