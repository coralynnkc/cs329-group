# NER — CoNLL-2003 (English)

Source: [CoNLL-2003](https://www.clips.uantwerpen.be/conll2003/ner/) — newswire text (Reuters corpus) annotated with four entity types: PER, ORG, LOC, MISC.

## Baseline Results — Entity-level Precision, Recall, F1

<!-- results:start -->
| Model | Sample 1 F1 | Sample 2 F1 | Sample 3 F1 | Precision | Recall | Mean F1 |
| ----- | ----------- | ----------- | ----------- | --------- | ------ | ------- |
| chatgpt 5.4 | 0.2147 | 0.2254 | 0.347 | 0.2266 | 0.3117 | 0.2624 |
| gemini 3 | 0.9308 | 0.9425 | 0.9169 | 0.9325 | 0.9282 | 0.9301 |
| sonnet 4.6 | 0.9137 | 0.9267 | 0.9183 | 0.9278 | 0.9116 | 0.9196 |
| opus 4.6 | 0.949 | 0.956 | 0.9435 | 0.9579 | 0.9414 | 0.9495 |
<!-- results:end -->

_Run `python ner/scripts/update_readme.py` after scoring to populate this table._

---

## Files

| File         | Split      | Sentences |
| ------------ | ---------- | --------- |
| `eng.train`  | Train      | ~14,000   |
| `eng.testa`  | Validation | ~3,250    |
| `eng.testb`  | Test       | ~3,680    |

CoNLL-2003 uses space-separated columns and IOB1 tagging (entities begin with `I-`; `B-` only appears when two entities of the same type are adjacent):

```
token       POS   chunk  NER_tag
LONDON      NNP   I-NP   I-LOC
1996-08-30  CD    I-NP   O
```

We use the **token** (col 1) and **NER tag** (col 4). Evaluation is on `eng.testa`.

### Entity Types

| Tag    | Description                                           |
| ------ | ----------------------------------------------------- |
| `PER`  | Person names                                          |
| `ORG`  | Organisations                                         |
| `LOC`  | Locations                                             |
| `MISC` | Miscellaneous (nationalities, events, products, etc.) |

---

## Baselining

### Workflow

1. Generate mini CSVs (one-time):

   ```bash
   python ner/scripts/make_mini.py
   ```

   Creates `mini/ner_input.csv` and `mini/ner_answers.csv` — 3 samples × 100 sentences,
   randomly drawn from `eng.testa` (so the model cannot learn from sequential context).

2. Send the prompt below with `mini/ner_input.csv` pasted in. Save the response as:

   ```
   mini/ner_predictions_<model>.csv
   ```

3. Score:

   ```bash
   python ner/scripts/score_baseline.py --model sonnet
   ```

   Repeat steps 2–3 for each model.

4. Update this README:

   ```bash
   python ner/scripts/update_readme.py
   ```

Scores are saved to:

- `results/<model>_scores.csv` — per-sample breakdown (precision, recall, F1, TP/FP/FN)
- `results/summary.csv` — all models side by side

---

## Prompt

Paste the contents of `mini/ner_input.csv` directly after this message:

```
For each row, identify all named entities in the sentence.
Return ONLY a CSV saved as ner_predictions_[model].csv with columns: sample_id,sentence_id,predicted_entities
where predicted_entities is a JSON list of {"text": "...", "label": "..."} objects.
No explanation. Do not skip rows.

Valid labels: PER, ORG, LOC, MISC
If a sentence has no entities, return an empty list: []

Example input row:  1,1,London is the capital of England .
Example output row: 1,1,"[{""text"": ""London"", ""label"": ""LOC""}, {""text"": ""England"", ""label"": ""LOC""}]"

Data:
[paste contents of mini/ner_input.csv here]
```
