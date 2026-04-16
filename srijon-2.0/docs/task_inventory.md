# Task Inventory

Authoritative record of every language and schema actually found per task in the
srijon-2.0 restructuring (as of April 2026). Use this before writing any scoring
script or LLM batch job so you know exactly what columns to expect.

---

## 1. Pronoun Resolution

**Task family:** Winograd-style coreference resolution  
**Source datasets:** WinoGrande (EN), Wino-X (FR / DE / RU)

### Languages present

| Language | Code | Source file | Original columns | Rows |
|----------|------|-------------|-----------------|------|
| English | `en` | `Pronoun Resolution English.xlsx` | `sentence` | 10,234 |
| French | `fr` | `Pronoun Resolution French.xlsx` | `context_fr`, `option1_fr`, `option2_fr` | 2,793 |
| German | `de` | `Pronoun Resolution German.xlsx` | `context_de:`, `option1_de:`, `option2_de:` | 5,835 |
| Russian | `ru` | `Pronoun Resolution Russian.xlsx` | `context_ru`, `option1_ru`, `option2_ru` | 1,487 |

**Languages NOT present:** Hindi (`hi`), Vietnamese (`vi`)

### Normalized schemas in srijon-2.0

#### English (`en`) — source / full
```
item_id | sentence
```

#### English (`en`) — inference
```
item_id | sentence
```
No option columns. `_` marks the pronoun position. Referent must be inferred from
sentence context alone or joined from WinoGrande annotations.

#### French / German / Russian (`fr`, `de`, `ru`) — source / full
```
item_id | sentence | option_a | option_b
```

#### French / German / Russian — inference
```
item_id | sentence | option_a | option_b
```

### Schema differences across languages

| Column | EN | FR | DE | RU |
|--------|----|----|----|----|
| `item_id` | ✓ | ✓ | ✓ | ✓ |
| `sentence` | ✓ | ✓ | ✓ | ✓ |
| `option_a` | ✗ | ✓ | ✓ | ✓ |
| `option_b` | ✗ | ✓ | ✓ | ✓ |
| `model_prediction` (full only) | ✓ | ✓ | ✓ | ✓ |
| `correct` (full only) | ✓ | ✓ | ✓ | ✓ |

### Encoding notes

| Language | Encoding repair needed | Method |
|----------|----------------------|--------|
| EN | No | — |
| FR | Yes | `cp1252 → utf-8` |
| DE | Yes | `cp1252 → utf-8` (critical for `ß` and umlauts) |
| RU | No (Cyrillic read correctly) | — |

### Known gaps

- English: no `option_a` / `option_b` and no gold answer in source file.
  Re-join from WinoGrande using sentence text as key.
- No Hindi or Vietnamese pronoun resolution data exists in `/srijon`.

---

## 2. Presuppositions

**Task family:** NLI / presupposition projection classification (E / N / C)  
**Source datasets:** CONFER (EN), XNLI (FR / DE / HI / RU / VI)

### Languages present

| Language | Code | Source file | Original columns | Rows |
|----------|------|-------------|-----------------|------|
| English | `en` | `Presuppositions English.xlsx` | `premise`, `hypothesis` | 6,981 |
| French | `fr` | `Presuppositions French.csv` | `premise`, `hypothesis` | 5,010 |
| German | `de` | `Presuppositions German.csv` | `premise`, `hypothesis` | 5,010 |
| Hindi | `hi` | `Presuppositions Hindi.csv` | `premise`, `hypothesis` | 5,010 |
| Russian | `ru` | `Presuppositions Russian.csv` | `premise`, `hypothesis` | 5,010 |
| Vietnamese | `vi` | `Presuppositions Vietnamese.csv` | `premise`, `hypothesis` | 5,010 |

**All 6 languages present.** This is the most complete multilingual task in the set.

### Normalized schema in srijon-2.0 (all languages identical)

#### Source / inference
```
item_id | premise | hypothesis
```

#### Full (scorer-ready)
```
item_id | premise | hypothesis | gold_label | model_label | correct
```
`gold_label` is empty — must be joined externally (see below).

### Schema differences across languages

None. All 6 languages share the same 2-column source schema.

### Gold label sources

| Language | Dataset | Label encoding | Normalized |
|----------|---------|---------------|-----------|
| EN | CONFER | `E` / `N` / `C` | direct |
| FR | XNLI | `0` / `1` / `2` | `{0→E, 1→N, 2→C}` |
| DE | XNLI | `0` / `1` / `2` | `{0→E, 1→N, 2→C}` |
| HI | XNLI | `0` / `1` / `2` | `{0→E, 1→N, 2→C}` |
| RU | XNLI | `0` / `1` / `2` | `{0→E, 1→N, 2→C}` |
| VI | XNLI | `0` / `1` / `2` | `{0→E, 1→N, 2→C}` |

See `docs/label_normalization.md` for detailed mapping.

### Historical accuracy (from /srijon evaluation)

| Language | Accuracy | Rows evaluated |
|----------|---------|---------------|
| EN | 45.46% | 6,982 |
| DE | 45.68% | 5,010 |
| FR | 44.99% | 5,010 |
| RU | 40.41% | 5,010 |
| HI | 41.43% | 5,010 |
| VI | 52.03% | 5,010 |

---

## 3. Lemmatization

**Task family:** Morphological lemmatization (inflected form → base form)  
**Source dataset:** UniMorph English

### Languages present

| Language | Code | Source file | Original columns | Rows |
|----------|------|-------------|-----------------|------|
| English | `en` | `Lemmas English.xlsx` | `word` (no header in original) | 115,523 |

**Only English.** No other languages are represented in the lemmatization data.

### Normalized schema in srijon-2.0

#### Source / inference
```
item_id | word
```

#### Full (scorer-ready)
```
item_id | word | gold_lemma | model_lemma | correct
```
`gold_lemma` is empty — must be joined from UniMorph corpus using `word` as key.

### Data notes

- The original Excel file had no header row; the first data value (`3rded`) was
  being treated as the column name by pandas. Fixed by reading with `header=None`.
- All 115,523 word forms are included.
- The UniMorph data has ~22,765 unique base words × ~5 inflections = ~91,870 entries
  (the extra rows in the file may include duplicates from cross-paradigm forms).
- One `word` may map to multiple valid `gold_lemma` values (homographs / conversion).
  See `docs/label_normalization.md` for scoring rule.

### Historical accuracy (from /srijon evaluation)

| Metric | Value |
|--------|-------|
| Accuracy | 67.76% |
| Rows evaluated | ~23,394 (sample from full set) |

---

## Cross-task coverage summary

| Task | EN | FR | DE | HI | RU | VI |
|------|----|----|----|----|----|----|
| pronoun_resolution | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ |
| presuppositions | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| lemmatization | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |

**Total unique language-task pairs: 11**

---

## Common column reference

| Column | Type | Tasks | Notes |
|--------|------|-------|-------|
| `item_id` | string | all | `{task}_{lang}_{index}`, 1-indexed, zero-padded to 6 digits |
| `sentence` | string | pronoun_resolution | Contains `_` placeholder |
| `option_a` | string | pronoun_resolution (FR/DE/RU) | First candidate referent |
| `option_b` | string | pronoun_resolution (FR/DE/RU) | Second candidate referent |
| `premise` | string | presuppositions | Source context sentence |
| `hypothesis` | string | presuppositions | Statement to classify |
| `word` | string | lemmatization | Inflected word form |
| `gold_label` | string | presuppositions full | E / N / C (fill externally) |
| `model_label` | string | presuppositions full | E / N / C (fill from LLM output) |
| `gold_lemma` | string | lemmatization full | Base form (fill from UniMorph) |
| `model_lemma` | string | lemmatization full | LLM output lemma |
| `model_prediction` | string | pronoun_resolution full | `option_a` or `option_b` |
| `correct` | int (0/1) | all full files | 1 = correct, 0 = wrong |
