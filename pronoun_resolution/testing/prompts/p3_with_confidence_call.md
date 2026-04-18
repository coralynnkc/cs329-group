You are labeling a pronoun-resolution dataset in the attached CSV file.
The file contains these columns:

item_id
sentence
option_a
option_b

Task:
For each row, determine whether the blank in the sentence refers to option_a or option_b.
For each row, apply this procedure internally:

Identify the two candidate antecedents: option_a and option_b.
Determine which candidate the blank can refer to in the sentence context.
Choose the candidate that yields the most coherent overall interpretation.
If the sentence does not provide enough information to decide between A and B, output REFUSE.

Output requirements:

Return ONLY CSV
Use exactly this header:
item_id,answer,confidence
For each row, answer must be exactly one of:
A
B
REFUSE
For each row, confidence must be an integer from 1 to 5:
1 = essentially guessing, both options seem equally plausible
2 = slight lean toward chosen answer but the other is nearly as plausible
3 = moderately confident, chosen answer seems more likely but alternative is reasonable
4 = confident, chosen answer is clearly better though alternative is not impossible
5 = certain, only one reading makes sense
If answer is REFUSE, set confidence to 1
Preserve the input row order
Include exactly one output row for every input row
Do not omit any item_id
Do not add explanations, notes, markdown, or code fences

Interpretation:

A means the blank refers to option_a
B means the blank refers to option_b
REFUSE means you cannot determine the answer from the sentence

Use only the attached CSV file and the sentence context in each row. Do not browse the web, search for external sources, retrieve outside documents, or cite external information.
Do not create widgets or other tools for this project. Just label the data and output it.
Now label every row in the attached file.
