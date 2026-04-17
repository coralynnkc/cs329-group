# P0 — Base Zero-Shot Batch Prompt

## Hypothesis
A minimal operational batch prompt may already be sufficient for strong performance.

## Prompt
```text
You are labeling a presupposition dataset in the attached CSV file.

The file contains these columns:
- item_id
- premise
- hypothesis

Task:
For each row, allot probability scores whether the hypothesis of the premise could be Entailment, Neutral, or Contradiction.

Output requirements:
- Return ONLY CSV
- Use exactly this header:
item_id,e_probability,n_probability,c_probability
- For each row, the answer must be exactly three numbers following item_id, between 0 and 1, with the relation e_probability + n_probability + c_probability = 1.

- Preserve the input row order
- Include exactly one output row for every input row
- Do not omit any item_id
- Do not add explanations, notes, markdown, or code fences

Use only the attached CSV file and the sentence context in each row. Do not browse the web, search for external sources, retrieve outside documents, or cite external information.

Now label every row in the attached file.
