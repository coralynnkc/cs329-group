# Prompt Template — Pronoun Resolution (Winograd-style)

## Task description

Given a sentence with a pronoun placeholder (`_`) and two candidate referents (`option_a`, `option_b`), identify which option correctly fills the blank based on world knowledge and contextual reasoning.

---

## Inference schema (from `inference/` CSVs)

| Column | Description |
|--------|-------------|
| `item_id` | Stable row identifier (e.g. `pr_fr_000042`) |
| `sentence` | Sentence with `_` as pronoun placeholder |
| `option_a` | First candidate referent |
| `option_b` | Second candidate referent |

**Note (English only):** The English dataset (`en`) has no `option_a`/`option_b` columns.
The model must infer the referent directly from the sentence using in-context reasoning.

---

## Prompt template (multilingual: FR / DE / RU)

```
You are a careful language analyst. Your task is to resolve a pronoun reference.

You will be given a sentence in which _ marks the pronoun position, along with two candidate referents (option_a and option_b). Decide which candidate the pronoun refers to.

Respond with ONLY "option_a" or "option_b". No explanation.

---
Sentence: {sentence}
option_a: {option_a}
option_b: {option_b}
---
Answer:
```

---

## Prompt template (English — no options provided)

```
You are a careful language analyst. Your task is to resolve a pronoun reference.

You will be given a sentence in which _ marks the pronoun position. The two people or things in the sentence are the possible referents. Decide which one _ refers to and write the exact word or phrase from the sentence.

Respond with ONLY the referent word or phrase. No explanation.

---
Sentence: {sentence}
---
Answer:
```

---

## Few-shot variant

Prepend 3–5 resolved examples before the target row to improve zero-shot calibration:

```
Examples:
Sentence: The trophy didn't fit in the suitcase because _ was too big.
Answer: trophy

Sentence: The city councilmen refused the demonstrators a permit because _ feared violence.
Answer: councilmen

---
Now answer this one:
Sentence: {sentence}
option_a: {option_a}
option_b: {option_b}
---
Answer:
```

---

## Output format for batch CSV scoring

After collecting model responses, merge predictions into the `full/` CSV under column `model_prediction`. Then compute:

- `correct` = 1 if `model_prediction` == gold referent, else 0  
- Report overall accuracy and breakdown by language.

---

## Notes

- The `_` placeholder is preserved exactly from the source dataset (WinoGrande / Wino-X).
- For multilingual files the sentence is already in the target language; do not translate.
- The correct answer for the English file is not stored in the source CSV and must be joined from WinoGrande annotations externally.
