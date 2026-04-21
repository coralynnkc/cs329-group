# P2 — Four-Shot Batch Prompt

## Hypothesis
A slightly richer exemplar set may outperform 2-shot while still keeping prompt length manageable.

## Frozen exemplars
- Example 1: item_id 539 → A
- Example 2: item_id 383 → B
- Example 3: item_id 292 → A
- Example 4: item_id 815 → B

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

Examples:

Example 1
item_id: 539
sentence: Firing a shotgun came more naturally for Megan than Tanya because _ grew up around them.
option_a: Megan
option_b: Tanya
answer: A

Example 2
item_id: 383
sentence: Emily said that Victoria's hijab was silly and old fashioned. _ heard some very offensive things.
option_a: Emily
option_b: Victoria
answer: B

Example 3
item_id: 292
sentence: Brian was jealous of Brett's new car because _ couldn't afford to buy a new car.
option_a: Brian
option_b: Brett
answer: A

Example 4
item_id: 815
sentence: The girl broke Leslie's heart but not Kenneth's because _ was never in love with her.
option_a: Leslie
option_b: Kenneth
answer: B

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
