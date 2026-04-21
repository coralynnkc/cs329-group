# P4 — Expanded-Definition Batch Prompt

## Hypothesis
A stronger conceptual definition of the task may help the model avoid shallow heuristics like selecting the nearest name.

## What is unique about this condition?
This condition does **not** add examples and does **not** add a numbered reasoning procedure. Instead, it changes the model's framing of the task by explicitly defining pronoun resolution as sentence-level contextual interpretation. It is intended to test whether conceptual guidance alone improves decisions.

## Prompt
```text
You are labeling a pronoun-resolution dataset in the attached CSV file.

The file contains these columns:
- item_id
- sentence
- option_a
- option_b

Task:
For each row, determine whether the blank in the sentence refers to option_a or option_b.

Pronoun resolution means deciding which candidate antecedent a blank refers to in context. Choose the answer that is most consistent with the sentence as a whole, including the event described, the likely speaker or experiencer, and the overall meaning of the sentence. Do not choose based only on which name is closest to the blank.

If the sentence does not provide enough information to decide between the two candidates, output REFUSE.

Output requirements:
- Return ONLY CSV
- Use exactly this header:
item_id,answer
- For each row, answer must be exactly one of:
A
B
REFUSE
- Preserve the input row order
- Include exactly one output row for every input row
- Do not omit any item_id
- Do not add explanations, notes, markdown, or code fences

Interpretation:
- A means the blank refers to option_a
- B means the blank refers to option_b
- REFUSE means you cannot determine the answer from the sentence

Use only the attached CSV file and the sentence context in each row. Do not browse the web, search for external sources, retrieve outside documents, or cite external information.
Do not create weidgets or other tools for this project. Just label the data and output it.

Now label every row in the attached file.
```
