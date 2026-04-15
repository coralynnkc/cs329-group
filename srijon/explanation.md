# NLP Benchmark Analysis — Zero-Shot LLM Evaluation

## Overview

This documents a series of zero-shot evaluations across three NLP tasks: **coreference resolution**, **presupposition/NLI labeling**, and **lemmatization**. All experiments used Claude as the model, with no API calls or external packages — relying purely on the model's in-context language understanding.

---

## 1. Referent & Antecedent Pronouns — Winograd-Style Coreference

### Dataset
- **WinoGrande** (English): 10,234 sentences
- **Wino-X** (multilingual): German, French, Russian variants

### Task
Fill in a `_` blank in each sentence with the correct referent, chosen from two options based on contextual reasoning.

### Prompt
> *"I don't want to run API. As a LLM just try and put for your best guess, and output me the excel of words."*

### Method
Rule-based coreference resolution using semantic/logical reasoning:
- Pronoun coreference with named people
- Object references and contextual clues (e.g., wealth comparisons, behavioral traits, contrasting adjectives)
- Iterative refinement across 4+ versions to fix systematic inversion errors

### Results

| Language | Accuracy |
|----------|----------|
| English | 35.72% |
| German | 51.85% |
| French | 52.38% |
| Russian | 51.91% |

**Note:** English performance (35.72%) fell below chance (~50%), indicating systematic answer inversions. Multilingual variants performed near chance, suggesting the task difficulty is consistent across languages.

---

## 2. Presupposition Labeling — NLI Classification

### Datasets
- **XNLI** (multilingual NLI): English, French, Russian, German, Hindi, Vietnamese
- **Conditional-NLI / CONFER**: English presupposition projection

### Task
Classify premise–hypothesis pairs with a presupposition label.

### Labels
| Label | Meaning |
|-------|---------|
| `E` / `0` | Entailment |
| `N` / `1` | Neutral |
| `C` / `2` | Contradiction |

### Prompt
> *"As a LLM just try and put for your best guess for presupposition label (0, 1, or 2) of the attached words, and output me the excel of labels. Just your own training."*

### Method
Rule-based labeling derived from presupposition projection principles:
- **E**: Hypothesis entity directly referenced in premise; presupposition projects through negation, belief contexts, and questions; *never...again* presupposes prior occurrence
- **C**: Hypothesis negates something the premise directly presupposes
- **N**: Hypothesis adds unrelated qualifiers, mentions extraneous entities, or the inference is only conditional

Output: 6,981 rows — E: 3,806 | C: 1,623 | N: 1,552

### Results (XNLI)

| Language | Accuracy |
|----------|----------|
| English | 45.46% |
| German | 45.68% |
| French | 44.99% |
| Russian | 40.41% |
| Hindi | 41.43% |
| Vietnamese | 52.03% |

**CONFER (English):** 45.46%

---

## 3. Lemmatization — UniMorph English

### Dataset
- **unimorph/eng**: ~22,765 unique words × 5 inflections = 91,870 total entries

### Task
Predict the base (lemma) form of each inflected word.

### Prompt
> *"Output — I don't want to run API or package. As a LLM just try and put for your best guess for lemmas of the attached words, and output me the excel of lemmas. For example, you can't use simplemma — just your own training."*

### Method
Pure rule-based lemmatizer built from linguistic knowledge (no spaCy, NLTK, or simplemma):

| Pattern | Example |
|---------|---------|
| Consonant doubling | `running → run`, `stopped → stop` |
| Silent-e restoration | `loving → love`, `using → use` |
| `-ify` verbs | `zombifying → zombify` |
| Compound words | `glasspapering → glasspaper` |
| `-ise`/`-ize` variants | `abelianizing → abelianize` |
| Irregular verbs | `ran → run`, `went → go`, `taught → teach` |
| Numeric tokens | `3rding → 3rd`, `86ed → 86` |

### Results
**Accuracy: 67.76%**

This was the strongest result across all three tasks, reflecting that morphological rules are more systematic and learnable than pragmatic coreference or presupposition inference.

---

## Summary

| Task | Dataset | Best Accuracy |
|------|---------|--------------|
| Coreference (English) | WinoGrande | 35.72% |
| Coreference (Multilingual) | Wino-X | ~52% |
| Presupposition / NLI | XNLI / CONFER | ~45–52% |
| Lemmatization | UniMorph ENG | **67.76%** |

All tests were **zero-shot**, using only the model's internal training with no fine-tuning, API calls, or external packages.
