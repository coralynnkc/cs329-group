# POS Tagging — Universal Dependencies (English EWT)

Source: [UD English EWT](https://github.com/UniversalDependencies/UD_English-EWT) — English Web Treebank from Universal Dependencies, covering weblogs, newsgroups, emails, reviews, and Yahoo! Answers.

## Baseline Results — Token-level POS Accuracy & Macro-F1

<!-- results:start -->
| Model | Sample 1 | Sample 2 | Sample 3 | Mean Acc | Macro-F1 |
| ------- | -------- | -------- | -------- | -------- | -------- |
| chatgpt | 0.8232 | 0.8001 | 0.7967 | 0.8067 | 0.7636 |
| gemini | 0.8557 | 0.841 | 0.7821 | 0.8263 | 0.7383 |
| opus | 0.9403 | 0.9456 | 0.9328 | 0.9396 | 0.8547 |
| sonnet | 0.8616 | 0.848 | 0.8411 | 0.8503 | 0.7126 |
<!-- results:end -->

_Run `python scripts/update_readme.py` after scoring to populate this table._

## Baseline Results — Per-tag F1

<!-- tag-f1:start -->
| Tag | placeholder |
| --- | --- |
<!-- tag-f1:end -->

---

## Files

| File                     | Sentences |
| ------------------------ | --------- |
| `en_ewt-ud-train.conllu` | ~12,500   |
| `en_ewt-ud-dev.conllu`   | ~2,000    |
| `en_ewt-ud-test.conllu`  | ~2,000    |

The `.conllu` format has 10 tab-separated columns per token, blank lines between sentences:

```
ID  FORM    LEMMA   UPOS  XPOS  FEATS  HEAD  DEPREL  DEPS  MISC
1   killed  kill    VERB  VBD   ...    ...   ...     ...   ...
```

We use **FORM** (col 2) and **UPOS** (col 4).

### Universal Dependencies POS Tags

| Tag     | Description              | Tag     | Description               |
| ------- | ------------------------ | ------- | ------------------------- |
| `ADJ`   | Adjective                | `NOUN`  | Noun                      |
| `ADP`   | Adposition               | `NUM`   | Numeral                   |
| `ADV`   | Adverb                   | `PART`  | Particle                  |
| `AUX`   | Auxiliary                | `PRON`  | Pronoun                   |
| `CCONJ` | Coordinating conjunction | `PROPN` | Proper noun               |
| `DET`   | Determiner               | `PUNCT` | Punctuation               |
| `INTJ`  | Interjection             | `SCONJ` | Subordinating conjunction |
| `VERB`  | Verb                     | `SYM`   | Symbol                    |
| `X`     | Other                    |         |                           |

---

## Baselining

### Workflow

1. Generate mini CSVs (one-time):

   ```bash
   python scripts/make_mini.py
   ```

   Creates `mini/en_input.csv` and `mini/en_answers.csv` — 3 samples × 100 sentences.

2. Send the prompt below with `mini/en_input.csv` pasted in. Save the response as:

   ```
   mini/en_predictions_<model>.csv
   ```

3. Score:

   ```bash
   python scripts/score_baseline.py --model sonnet
   ```

   Repeat steps 2–3 for each model.

4. Update this README:
   ```bash
   python scripts/update_readme.py
   ```

Scores are saved to:

- `results/<model>_scores.csv` — per-sample token accuracy
- `results/summary.csv` — all models side by side

---

## Prompt

Paste the contents of `mini/en_input.csv` directly after this message:

```
For each row, assign a Universal Dependencies POS tag to every token in the sentence.
The sentence tokens are space-separated in the "words" column.
Return ONLY a CSV with columns: sample_id,sentence_id,predicted_tags
where predicted_tags is a space-separated sequence of tags in the same order as the words.
No explanation. Do not skip rows. Do not change the number of tokens.

Valid tags: ADJ ADP ADV AUX CCONJ DET INTJ NOUN NUM PART PRON PROPN PUNCT SCONJ SYM VERB X

Example input row:  1,1,The cat sat on the mat .
Example output row: 1,1,DET NOUN VERB ADP DET NOUN PUNCT

Data:
[paste contents of mini/en_input.csv here]
```
