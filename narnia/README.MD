# Narnia — Agency-Based Character NER

Source: Chronicles of Narnia — 200 sentences manually annotated with character mentions and their narrative agency role.

## Baseline Results — Entity-level Precision, Recall, F1

<!-- results:start -->
| Model | Sample 1 F1 | Sample 2 F1 | Sample 3 F1 | Precision | Recall | Mean F1 |
| ----- | ----------- | ----------- | ----------- | --------- | ------ | ------- |
<!-- results:end -->

_Run `python narnia/scripts/update_readme.py` after scoring to populate this table._

---

## Task

Given a sentence from _The Lion, the Witch and the Wardrobe_, identify all character mentions and assign each one an agency label describing their narrative role in that sentence.

## Labels

| Label              | Description                                                           |
| ------------------ | --------------------------------------------------------------------- |
| `ACTIVE_SPEAKER`   | Character is mentioned in the context of speaking a dialogue          |
| `ACTIVE_PERFORMER` | Character is written to perform a physical action                     |
| `ACTIVE_THOUGHT`   | Character is written to think or feel something                       |
| `ADDRESSED`        | Character is addressed in dialogue                                    |
| `MENTIONED_ONLY`   | Mentioned by a third-person or narrator                               |
| `MISCELLANEOUS`    | Any other role not covered by the above                               |

---

## Files

| File                                        | Description                                           |
| ------------------------------------------- | ----------------------------------------------------- |
| `man_annotated_narnia200 - Sheet1.csv`      | Raw manual annotations (source of truth)              |
| `data/narnia_annotated.csv`                 | NER-style format: sentence + JSON entity list         |
| `data/train.csv`                            | 80% split (~159 sentences) for few-shot examples      |
| `data/test.csv`                             | 20% split (~40 sentences) for evaluation              |
| `mini/narnia_input.csv`                     | Model-facing eval input (no labels)                   |
| `mini/narnia_answers.csv`                   | Gold answer key (JSON entity lists)                   |
| `mini/narnia_predictions_<model>.csv`       | Model predictions (save here after running a model)   |

### Data Format

`narnia_annotated.csv` and the split files share the same schema:

```
sentence_id, sentence, entities
```

where `entities` is a JSON list of `{"text": "...", "label": "..."}` objects:

```
38,Badgers ! said Lucy .,"[{""text"": ""Lucy"", ""label"": ""ACTIVE_SPEAKER""}]"
2,This story is about something that happened to them ...,[]
```

Sentences with no annotated characters have `entities = []`.

---

## Baselining

### Workflow

1. Convert raw annotations (one-time, already done):

   ```bash
   python narnia/scripts/convert_annotations.py
   ```

2. Create train/test splits (one-time, already done):

   ```bash
   python narnia/scripts/make_splits.py
   ```

3. Generate mini CSVs (one-time):

   ```bash
   python narnia/scripts/make_mini.py
   ```

   Creates `mini/narnia_input.csv` and `mini/narnia_answers.csv` — all 199 sentences
   in shuffled order (zero-shot baseline; no train/test contamination risk).

4. Send the prompt below with `mini/narnia_input.csv` pasted in. Save the response as:

   ```
   mini/narnia_predictions_<model>.csv
   ```

5. Score:

   ```bash
   python narnia/scripts/score_baseline.py --model sonnet
   ```

   Repeat steps 4–5 for each model.

6. Update this README:

   ```bash
   python narnia/scripts/update_readme.py
   ```

Scores are saved to:

- `results/<model>_scores.csv` — per-sample breakdown (precision, recall, F1, TP/FP/FN)
- `results/summary.csv` — all models side by side

---

## Prompt

Paste the contents of `mini/narnia_input.csv` directly after this message:

```
For each row, identify all character mentions in the sentence and assign each one an agency label.
Return ONLY a CSV saved as narnia_predictions_[model].csv with columns: sample_id,sentence_id,predicted_entities
where predicted_entities is a JSON list of {"text": "...", "label": "..."} objects.
No explanation. Do not skip rows.

Valid labels: ACTIVE_SPEAKER, ACTIVE_PERFORMER, ACTIVE_THOUGHT, ADDRESSED, MENTIONED_ONLY, MISCELLANEOUS

Label definitions:
- ACTIVE_SPEAKER: character is mentioned in the context of speaking a dialogue
- ACTIVE_PERFORMER: character is written to perform a physical action
- ACTIVE_THOUGHT: character is written to think or feel something
- ADDRESSED: character is addressed in dialogue
- MENTIONED_ONLY: mentioned by a third-person or narrator
- MISCELLANEOUS: any other role

If a sentence has no character mentions, return an empty list: []

Example input row:  1,1,Badgers ! said Lucy .
Example output row: 1,1,"[{""text"": ""Lucy"", ""label"": ""ACTIVE_SPEAKER""}]"

Example input row:  1,2,This story is about something that happened to them when they were sent away .
Example output row: 1,2,[]

Data:
[paste contents of mini/narnia_input.csv here]
```
