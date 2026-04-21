# Assumptions and Ambiguities

This document records every non-obvious decision made during the normalization of
`/srijon/data/` into `srijon-2.0/`. Future maintainers should read this before
modifying the pipeline.

---

## A1 — Lemmatization: first Excel row treated as header

**File:** `srijon/data/Lemmas English.xlsx`  
**Observation:** The file has a single column. When read with `header=0` (default),
pandas treats the first data value (`3rded`) as the column name, discarding it as a
row. The file actually contains 115,523 word forms; with default reading, only 115,522
would appear.

**Decision:** Read with `header=None, names=["word"]` to recover all 115,523 rows.
The column is named `word` in all srijon-2.0 output files.

**Impact:** Item IDs start at `lm_en_000001` = `3rded`. If the original `/srijon`
scripts used 0-indexed row numbers, there is an off-by-one relative to those.

---

## A2 — Pronoun Resolution English: no option_a / option_b columns

**File:** `srijon/data/Pronoun Resolution English.xlsx`  
**Observation:** The file has exactly one column (`sentence`). The sentences contain
a `_` placeholder but no candidate options are stored.

**Decision:** Inference schema for English is `(item_id, sentence)` only. The original
WinoGrande dataset has `(sentence, option1, option2, answer)`. If gold labels or
options are needed, re-join from the WinoGrande source using sentence text as a key.

**Impact:** The English pronoun resolution task cannot be scored without the WinoGrande
gold labels. The `full/` file has empty `model_prediction` and `correct` columns.

---

## A3 — Pronoun Resolution: encoding repair (FR, DE)

**Files:** `Pronoun Resolution French.xlsx`, `Pronoun Resolution German.xlsx`  
**Observation:** Text data stored in Excel with UTF-8 byte sequences mis-labelled as
Windows-1252 (cp1252). Symptoms: `é` appears as `Ã©`, `ß` appears as `ÃŸ`, `ü`
appears as `Ã¼`, etc.

**Decision:** Applied `s.encode("cp1252").decode("utf-8")` to all string values in
FR and DE pronoun resolution files. Russian uses Cyrillic and was read correctly
without any repair.

**Verification:** After repair, `Die Frau suchte nach einer anderen Vase für den
Blumenstrauß` and `La femme a cherché un vase différent` display correctly.

**Note:** Latin-1 is NOT sufficient for German because `0x9F` (which encodes `ß` in
multi-byte UTF-8) maps to U+0178 (`Ÿ`) in cp1252 but has no representation in
ISO-8859-1. Only cp1252 fixes both `é` and `ß` correctly.

---

## A4 — German column name had trailing colon

**File:** `srijon/data/Pronoun Resolution German.xlsx`  
**Observation:** Column names were `context_de:`, `option1_de:`, `option2_de:` (with
trailing colon). This is likely a data entry artifact.

**Decision:** Strip trailing colons/whitespace from all column names before renaming.
The colon is not preserved in any output file.

---

## A5 — No gold labels in any source file

**All presupposition files, pronoun resolution files, lemmatization file**  
**Observation:** None of the source Excel/CSV files contain gold label columns.
The original `/srijon/scripts/` notebooks appear to have sourced gold labels from
separate API calls or XNLI/WinoGrande datasets at runtime.

**Decision:** Add empty placeholder columns (`gold_label`, `model_prediction`,
`model_lemma`, `correct`) in `full/` files. Do not invent label values.

**Required action:** Before scoring, join gold labels from:
- Presuppositions (FR/DE/HI/RU/VI): XNLI test set (labels: 0=E, 1=N, 2=C)
- Presuppositions (EN): CONFER dataset (labels: E/N/C)
- Pronoun Resolution (EN): WinoGrande annotations
- Pronoun Resolution (FR/DE/RU): Wino-X annotations
- Lemmatization (EN): UniMorph English corpus

---

## A6 — Row ordering preserved

All rows are output in the same order as the source file. No sorting, shuffling, or
deduplication was applied. Duplicate sentences (common in presupposition datasets where
the same premise appears with multiple hypotheses) are preserved as-is.

---

## A7 — No splits created

The original data has no train/dev/test split. All files are exported as `_master`
(full dataset). See `docs/split_strategy.md` for a documented plan for future splits.

---

## A8 — Presuppositions English vs multilingual: different source datasets

The English presupposition file originates from CONFER (a presupposition-focused
English dataset, 6,981 rows), while the French/German/Hindi/Russian/Vietnamese files
originate from XNLI (5,010 rows each). They share the same surface schema
(`premise`, `hypothesis`) but come from different corpora with potentially different
label distributions and difficulty profiles.

---

## A9 — item_id format

Item IDs are `{task}_{lang}_{zero_padded_index}`, e.g. `pr_fr_000001`.

| Task prefix | Task |
|-------------|------|
| `pr` | pronoun_resolution |
| `ps` | presuppositions |
| `lm` | lemmatization |

IDs are 1-indexed. Padding width is `max(6, len(str(n)))` to future-proof for very
large datasets. IDs are stable across re-runs because row order is preserved and
IDs are derived from row position only.
