# Coref — Character Cluster Coreference (Narnia)

Source: Chronicles of Narnia — same 199 sentences used in agency-based NER, re-annotated for character identity clustering.

## Task

Given a sentence, identify all character mentions and group them under their canonical character name. This is a hybrid of NER (find the spans) and coreference resolution (cluster them by identity) — neither task alone gives you character-centric annotation where every mention of a character maps to their canonical name, including nicknames and epithets.

## Canonical Characters

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

## Baseline Results — Mention-level Precision, Recall, F1

<!-- results:start -->
| Model | Precision | Recall | F1 |
| ----- | --------- | ------ | -- |
<!-- results:end -->

_Run `python coref/scripts/update_readme.py` after scoring to update this table._

## Few-shot Results — Mention-level Precision, Recall, F1

<!-- results-fewshot:start -->
| Model | Precision | Recall | F1 |
| ----- | --------- | ------ | -- |
<!-- results-fewshot:end -->

_Run `python coref/scripts/update_readme.py` after scoring to update this table._

---

## Data Format

`data/narnia_coref_annotated.csv` and the split files share the schema:

```
sentence_id, sentence, clusters
```

where `clusters` is a JSON list of `{"character": "<canonical_name>", "mentions": ["<span>", ...]}` objects:

```
1,"Once there were four children whose names were Peter , Susan , Edmund and Lucy .","[{""character"": ""Peter Pevensie"", ""mentions"": [""Peter""]}, {""character"": ""Susan Pevensie"", ""mentions"": [""Susan""]}, {""character"": ""Edmund Pevensie"", ""mentions"": [""Edmund""]}, {""character"": ""Lucy Pevensie"", ""mentions"": [""Lucy""]}]"
2,This story is about something that happened to them ...,[]
```

Sentences with no character mentions have `clusters = []`.

---

## Files

| File | Description |
| ---- | ----------- |
| `data/narnia_coref_annotated.csv` | Character-cluster format: sentence + JSON cluster list |
| `mini/narnia_coref_input.csv` | Model-facing eval input (no labels) |
| `mini/narnia_coref_answers.csv` | Gold answer key (JSON cluster lists) |
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

Paste the contents of `mini/narnia_coref_input.csv` directly after this message:

```
For each row, identify all character mentions in the sentence and group them by their canonical character name.
Return ONLY a CSV with columns: sample_id,sentence_id,predicted_clusters
where predicted_clusters is a JSON list of {"character": "<canonical_name>", "mentions": ["<span>", ...]} objects.
No explanation. Do not skip rows.

Canonical characters and their common surface forms:
- Peter Pevensie (Peter, he)
- Susan Pevensie (Susan, she)
- Edmund Pevensie (Edmund, Ed, he)
- Lucy Pevensie (Lucy, she)
- Professor Digory Kirke (Professor, the Professor, he)
- Mrs. Macready (Mrs. Macready, she)
- Mr. Tumnus (Mr. Tumnus, Tumnus, the Faun, he)
- Jadis (Jadis, the White Witch, the Queen, she)
- Bacchus (Bacchus, he)
- Silenus (Silenus, he)
- Ivy, Margaret, Betty (servants — use their names as canonical)

Only tag named character mentions that appear explicitly in the sentence.
Do not tag pronouns (he, she, they) unless you are certain from the sentence alone.
If a sentence has no character mentions, return an empty list: []

Example input:  1,1,Once there were four children whose names were Peter , Susan , Edmund and Lucy .
Example output: 1,1,"[{""character"": ""Peter Pevensie"", ""mentions"": [""Peter""]}, {""character"": ""Susan Pevensie"", ""mentions"": [""Susan""]}, {""character"": ""Edmund Pevensie"", ""mentions"": [""Edmund""]}, {""character"": ""Lucy Pevensie"", ""mentions"": [""Lucy""]}]"

Example input:  1,2,This story is about something that happened to them .
Example output: 1,2,[]

Data:
[paste contents of mini/narnia_coref_input.csv here]
```

---

### Few-shot prompt

Paste the contents of `mini/narnia_coref_input.csv` after the examples block below.
Save the response as `mini/narnia_coref_predictions_<model>_fewshot.csv`.

```
You are annotating sentences from The Chronicles of Narnia for character coreference.

For each row, identify all character mentions in the sentence and group them under
their canonical character name. Return ONLY a CSV with columns:
sample_id,sentence_id,predicted_clusters
where predicted_clusters is a JSON list of {"character": "<canonical_name>", "mentions": ["<span>", ...]} objects.
No explanation. Do not skip rows.

Canonical characters:
- Peter Pevensie — surface forms: Peter
- Susan Pevensie — surface forms: Susan
- Edmund Pevensie — surface forms: Edmund, Ed
- Lucy Pevensie — surface forms: Lucy
- Professor Digory Kirke — surface forms: Professor, the Professor
- Mrs. Macready — surface forms: Mrs. Macready
- Mr. Tumnus — surface forms: Mr. Tumnus, Tumnus, the Faun, Faun
- Jadis — surface forms: Jadis, the White Witch, the Queen, the Witch
- Bacchus — surface forms: Bacchus
- Silenus — surface forms: Silenus
- Ivy, Margaret, Betty — use the name as written

Key rules:
- Only tag spans that appear explicitly in the sentence text.
- A name like "the Faun" or "the Professor" counts as a mention — use the canonical name.
- If a character is mentioned twice (e.g. "Mr. Tumnus" and "the Faun" in one sentence), both go in the same mentions list.
- Group labels like "Son of Adam" or "Daughter of Eve" are NOT character names — omit them.
- If a sentence has no character mentions, return [].

--- EXAMPLES ---

Input:  1,1,Once there were four children whose names were Peter , Susan , Edmund and Lucy .
Output: 1,1,"[{""character"": ""Peter Pevensie"", ""mentions"": [""Peter""]}, {""character"": ""Susan Pevensie"", ""mentions"": [""Susan""]}, {""character"": ""Edmund Pevensie"", ""mentions"": [""Edmund""]}, {""character"": ""Lucy Pevensie"", ""mentions"": [""Lucy""]}]"

Input:  1,2,This story is about something that happened to them when they were sent away .
Output: 1,2,[]

Input:  1,3,"This is the land of Narnia , said the Faun , where we are now ."
Output: 1,3,"[{""character"": ""Mr. Tumnus"", ""mentions"": [""Faun""]}]"

Input:  1,4,"And may I ask , O Lucy , said Mr. Tumnus , how you have come into Narnia ?"
Output: 1,4,"[{""character"": ""Lucy Pevensie"", ""mentions"": [""Lucy""]}, {""character"": ""Mr. Tumnus"", ""mentions"": [""Mr. Tumnus""]}]"

Input:  1,5,He had no wife and he lived in a very large house with a housekeeper called Mrs. Macready and three servants .
Output: 1,5,"[{""character"": ""Mrs. Macready"", ""mentions"": [""Mrs. Macready""]}]"

Input:  1,6,"We 've fallen on our feet and no mistake , said Peter ."
Output: 1,6,"[{""character"": ""Peter Pevensie"", ""mentions"": [""Peter""]}]"

--- DATA ---
[paste contents of mini/narnia_coref_input.csv here]
```
