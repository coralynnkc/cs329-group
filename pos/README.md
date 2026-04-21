# POS Tagging — Universal Dependencies (English EWT)

Source: [UD English EWT](https://universaldependencies.org/treebanks/en_ewt/index.html) — English Web Treebank from Universal Dependencies, covering weblogs, newsgroups, emails, reviews, and Yahoo! Answers.

## Baseline Results — Token-level POS Accuracy & Macro-F1

| Model | Sample 1 | Sample 2 | Sample 3 | Mean Acc | Macro-F1 |
|---|---:|---:|---:|---:|---:|
| ChatGPT 5.4 | 0.8232 | 0.8001 | 0.7967 | 0.8067 | 0.7636 |
| Gemini | 0.8557 | 0.8410 | 0.7821 | 0.8263 | 0.7383 |
| Opus 4.6 | 0.9403 | 0.9456 | 0.9328 | 0.9396 | 0.8547 |
| Opus 4.7 | 0.7652 | 0.7762 | 0.7547 | 0.7654 | 0.6791 |
| Sonnet | 0.8616 | 0.8480 | 0.8411 | 0.8503 | 0.7126 |

Run `python scripts/update_readme.py` after scoring to populate this table.

## Baseline Results — Per-tag F1

| Tag | ChatGPT 5.4 | Gemini | Opus 4.6 | Opus 4.7 | Sonnet |
|---|---:|---:|---:|---:|---:|
| ADJ | 0.5882 | 0.7977 | 0.9125 | 0.7033 | 0.8100 |
| ADP | 0.8771 | 0.8329 | 0.9061 | 0.7788 | 0.7950 |
| ADV | 0.7056 | 0.7955 | 0.8592 | 0.6958 | 0.6944 |
| AUX | 0.9083 | 0.8639 | 0.9472 | 0.8090 | 0.8762 |
| CCONJ | 0.9304 | 0.8372 | 0.9854 | 0.7942 | 0.9240 |
| DET | 0.8137 | 0.8615 | 0.9870 | 0.7903 | 0.9010 |
| INTJ | 0.5833 | 0.7000 | 0.9474 | 0.1667 | 0.3333 |
| NOUN | 0.7470 | 0.8293 | 0.9512 | 0.7831 | 0.8909 |
| NUM | 0.8609 | 0.7673 | 0.9182 | 0.7867 | 0.8462 |
| PART | 0.9355 | 0.8475 | 0.9967 | 0.7551 | 0.1258 |
| PRON | 0.8250 | 0.8532 | 0.9791 | 0.8237 | 0.9063 |
| PROPN | 0.7321 | 0.8262 | 0.8953 | 0.7739 | 0.8495 |
| PUNCT | 0.9858 | 0.8593 | 0.9934 | 0.7710 | 0.9702 |
| SCONJ | 0.4224 | 0.6154 | 0.6353 | 0.5949 | 0.5257 |
| SYM | 0.6250 | 0.4545 | 0.7059 | 0.5333 | 0.6000 |
| VERB | 0.7812 | 0.8388 | 0.9408 | 0.7781 | 0.8859 |
| X | 0.2857 | 0.0000 | 0.0000 | 0.0000 | 0.1905 |

***

## Additional Experiment — ChatGPT 5.4 and Batch Size

To test whether ChatGPT 5.4’s weaker POS performance might be caused by batching, I ran three additional `n=100` trials (`results/n_100`). Those runs were highly variable: accuracy ranged from **0.7518** to **0.9302**, and macro-F1 ranged from **0.6932** to **0.8472**. By comparison, the original `n=300` ChatGPT 5.4 baseline averaged **0.8067** accuracy and **0.7636** macro-F1.

Taken together, these `n=100` trials do **not** show a stable or clearly superior performance regime relative to the `n=300` baseline. The small-batch condition can sometimes score higher, but it can also score substantially lower, so batching alone does not appear to be a meaningful or sufficient explanation for the observed ChatGPT performance deterioration.

### ChatGPT 5.4 batch-size check

| Setting | Run / Sample 1 | Run / Sample 2 | Run / Sample 3 | Mean Acc | Macro-F1 |
|---|---:|---:|---:|---:|---:|
| `n=300` baseline | 0.8232 | 0.8001 | 0.7967 | 0.8067 | 0.7636 |
| `n=100` check | 0.9302 | 0.8556 | 0.7518 | 0.8459 | 0.7859 |

***

## Files

| File | Sentences |
|---|---:|
| `en_ewt-ud-train.conllu` | ~12,500 |
| `en_ewt-ud-dev.conllu` | ~2,000 |
| `en_ewt-ud-test.conllu` | ~2,000 |

The `.conllu` format has 10 tab-separated columns per token, blank lines between sentences:

    ID  FORM    LEMMA   UPOS  XPOS  FEATS  HEAD  DEPREL  DEPS  MISC
    1   killed  kill    VERB  VBD   ...    ...   ...     ...   ...

We use FORM (col 2) and UPOS (col 4).

### Universal Dependencies POS Tags

| Tag | Description | Tag | Description |
|---|---|---|---|
| `ADJ` | Adjective | `NOUN` | Noun |
| `ADP` | Adposition | `NUM` | Numeral |
| `ADV` | Adverb | `PART` | Particle |
| `AUX` | Auxiliary | `PRON` | Pronoun |
| `CCONJ` | Coordinating conjunction | `PROPN` | Proper noun |
| `DET` | Determiner | `PUNCT` | Punctuation |
| `INTJ` | Interjection | `SCONJ` | Subordinating conjunction |
| `VERB` | Verb | `SYM` | Symbol |
| `X` | Other |

***

## Baselining

### Workflow

1. Generate mini CSVs (one-time):

       python scripts/make_mini.py

   Creates `mini/en_input.csv` and `mini/en_answers.csv` — 3 samples × 100 sentences.

2. Send the prompt below with `mini/en_input.csv` pasted in. Save the response as:

       mini/en_predictions_<model>.csv

3. Score:

       python scripts/score_baseline.py --model sonnet

   Repeat steps 2–3 for each model.

4. Update this README:

       python scripts/update_readme.py

Scores are saved to:
- `results/<model>_scores.csv` — per-sample token accuracy
- `results/summary.csv` — all models side by side

***

## Prompt

Paste the contents of `mini/en_input.csv` directly after this message:

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
