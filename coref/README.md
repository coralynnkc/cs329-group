# Coref — Character Coreference NER (Narnia)

Source: Chronicles of Narnia — same 199 sentences used in agency-based NER (`narnia/`), re-annotated for character identity resolution.

## Task

Given a sentence, identify all character mentions and assign each one their canonical character name. The model must resolve both named references ("the Faun", "the Professor") and nicknames to the correct canonical label — this is NER where the label set is the set of characters, not entity types.

Combined with the agency labels from `narnia/`, each `(span, character, agency_role)` triple enables corpus-level insights like "how often is Lucy Pevensie an ACTIVE_SPEAKER?"

## Canonical Characters

| Canonical name | Notes |
| -------------- | ----- |
| Peter Pevensie | |
| Susan Pevensie | |
| Edmund Pevensie | |
| Lucy Pevensie | |
| Professor Digory Kirke | |
| Mrs. Macready | |
| Mr. Tumnus | |
| Jadis | the White Witch |
| Bacchus | |
| Silenus | |
| Ivy | servant |
| Margaret | servant |
| Betty | servant |

## Baseline Results — Entity-level Precision, Recall, F1

<!-- results:start -->
| Model | Precision | Recall | F1 |
| ----- | --------- | ------ | -- |
<!-- results:end -->

_Run `python coref/scripts/update_readme.py` after scoring to update this table._

## Few-shot Results — Entity-level Precision, Recall, F1

<!-- results-fewshot:start -->
| Model | Precision | Recall | F1 |
| ----- | --------- | ------ | -- |
<!-- results-fewshot:end -->

_Run `python coref/scripts/update_readme.py` after scoring to update this table._

---

## Data Format

`data/narnia_coref_annotated.csv` shares the same schema as `narnia/data/narnia_annotated.csv`:

```
sentence_id, sentence, entities
```

where `entities` is a JSON list of `{"text": "...", "character": "..."}` objects:

```
1,"Once there were four children whose names were Peter , Susan , Edmund and Lucy .","[{""text"": ""Peter"", ""character"": ""Peter Pevensie""}, {""text"": ""Susan"", ""character"": ""Susan Pevensie""}, ...]"
2,This story is about something that happened to them ...,[]
```

Sentences with no character mentions have `entities = []`.

---

## Files

| File | Description |
| ---- | ----------- |
| `data/narnia_coref_annotated.csv` | Character NER format: sentence + JSON entity list |
| `mini/narnia_coref_input.csv` | Model-facing eval input (no labels) |
| `mini/narnia_coref_answers.csv` | Gold answer key (JSON entity lists) |
| `mini/narnia_coref_predictions_<model>.csv` | Model predictions (save here after running a model) |

---

## Workflow

1. _(One-time)_ Convert raw annotations and generate mini eval files:

   ```bash
   python coref/scripts/convert_annotations.py
   python coref/scripts/make_mini.py
   ```

2. Send the prompt below with `mini/narnia_coref_input.csv` pasted in. Save the response as:

   ```
   mini/narnia_coref_predictions_<model>.csv
   ```

3. Score:

   ```bash
   python coref/scripts/score_baseline.py --model <model>
   python coref/scripts/score_baseline.py --model <model> --per_character
   ```

4. For few-shot runs, use the few-shot prompt. Save the response as:

   ```
   mini/narnia_coref_predictions_<model>_fewshot.csv
   ```

5. Score few-shot:

   ```bash
   python coref/scripts/score_baseline.py --model <model> --prompt fewshot
   ```

6. Update this README:

   ```bash
   python coref/scripts/update_readme.py
   ```

Scores are saved to:
- `results/<model>_scores.csv` — precision, recall, F1, TP/FP/FN per sample
- `results/<model>_fewshot_scores.csv` — same for few-shot runs
- `results/summary.csv` — all models side by side

---

## Prompts

### Zero-shot prompt

Paste the contents of `mini/narnia_coref_input.csv` directly after this message.
Save the response as `mini/narnia_coref_predictions_[model].csv`.

```
For each row, identify all character mentions in the sentence and assign each one their canonical character name.
Return ONLY a CSV saved as narnia_coref_predictions_[model].csv with columns: sample_id,sentence_id,predicted_entities
where predicted_entities is a JSON list of {"text": "...", "character": "..."} objects.
No explanation. Do not skip rows.

Valid canonical character names:
- Peter Pevensie
- Susan Pevensie
- Edmund Pevensie
- Lucy Pevensie
- Professor Digory Kirke
- Mrs. Macready
- Mr. Tumnus
- Jadis
- Bacchus
- Silenus
- Ivy
- Margaret
- Betty

Assign every mention — including epithets and titles — to the correct canonical name.
If a sentence has no character mentions, return an empty list: []

Example input:  1,1,Once there were four children whose names were Peter , Susan , Edmund and Lucy .
Example output: 1,1,"[{""text"": ""Peter"", ""character"": ""Peter Pevensie""}, {""text"": ""Susan"", ""character"": ""Susan Pevensie""}, {""text"": ""Edmund"", ""character"": ""Edmund Pevensie""}, {""text"": ""Lucy"", ""character"": ""Lucy Pevensie""}]"

Example input:  1,2,This story is about something that happened to them .
Example output: 1,2,[]

Data:
[paste contents of mini/narnia_coref_input.csv here]
```

---

### Few-shot prompt

Paste the contents of `mini/narnia_coref_input.csv` after the examples block below.
Save the response as `mini/narnia_coref_predictions_[model]_fewshot.csv`.

```
You are annotating sentences from The Chronicles of Narnia for character coreference.

For each row, identify all character mentions in the sentence and assign each one
their canonical character name. Return ONLY a CSV saved as narnia_coref_predictions_[model]_fewshot.csv
with columns: sample_id,sentence_id,predicted_entities
where predicted_entities is a JSON list of {"text": "...", "character": "..."} objects.
No explanation. Do not skip rows.

Valid canonical character names:
- Peter Pevensie
- Susan Pevensie
- Edmund Pevensie
- Lucy Pevensie
- Professor Digory Kirke
- Mrs. Macready
- Mr. Tumnus
- Jadis
- Bacchus
- Silenus
- Ivy
- Margaret
- Betty

Key rules:
- The text field should be the span as it appears in the sentence.
- Resolve all epithets and titles to the correct canonical name (e.g. "the Faun" → Mr. Tumnus, "the Professor" → Professor Digory Kirke, "the White Witch" → Jadis).
- If a sentence has no character mentions, return [].

--- EXAMPLES ---

Input:  1,1,Once there were four children whose names were Peter , Susan , Edmund and Lucy .
Output: 1,1,"[{""text"": ""Peter"", ""character"": ""Peter Pevensie""}, {""text"": ""Susan"", ""character"": ""Susan Pevensie""}, {""text"": ""Edmund"", ""character"": ""Edmund Pevensie""}, {""text"": ""Lucy"", ""character"": ""Lucy Pevensie""}]"

Input:  1,2,This story is about something that happened to them when they were sent away .
Output: 1,2,[]

Input:  1,3,"This is the land of Narnia , said the Faun , where we are now ."
Output: 1,3,"[{""text"": ""Faun"", ""character"": ""Mr. Tumnus""}]"

Input:  1,4,"They were sent to the house of an old Professor who lived in the heart of the country ."
Output: 1,4,"[{""text"": ""Professor"", ""character"": ""Professor Digory Kirke""}]"

Input:  1,5,He had no wife and he lived in a very large house with a housekeeper called Mrs. Macready and three servants .
Output: 1,5,"[{""text"": ""Mrs. Macready"", ""character"": ""Mrs. Macready""}]"

Input:  1,6,"And may I ask , O Lucy , said Mr. Tumnus , how you have come into Narnia ?"
Output: 1,6,"[{""text"": ""Lucy"", ""character"": ""Lucy Pevensie""}, {""text"": ""Mr. Tumnus"", ""character"": ""Mr. Tumnus""}]"

Input:  1,7,"It was she who had enchanted the whole country so that it was always winter ."
Output: 1,7,"[{""text"": ""she"", ""character"": ""Jadis""}]"

--- DATA ---
[paste contents of mini/narnia_coref_input.csv here]
```
