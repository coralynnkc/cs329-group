# POS Prompt Variants: P0–P3

This document describes the prompt variants used to test whether **task decomposition** can improve Universal Dependencies POS tagging performance relative to the original baseline prompt (**P0**).

The goal of these variants is not to change the task, output format, or evaluation procedure. Instead, each prompt is designed as a **controlled intervention** on the instruction block so that results can be compared directly against the baseline.

---

## Baseline Prompt (P0)

P0 is the original prompt:

> For each row, assign a Universal Dependencies POS tag to every token in the sentence.  
> The sentence tokens are space-separated in the "words" column.  
> Return ONLY a CSV with columns: sample_id,sentence_id,predicted_tags  
> where predicted_tags is a space-separated sequence of tags in the same order as the words.  
> No explanation. Do not skip rows. Do not change the number of tokens.  
> Valid tags: ADJ ADP ADV AUX CCONJ DET INTJ NOUN NUM PART PRON PROPN PUNCT SCONJ SYM VERB X  
>
> Example input row: 1,1,The cat sat on the mat .  
> Example output row: 1,1,DET NOUN VERB ADP DET NOUN PUNCT  
>
> Data:  
> [paste contents of mini/en_input.csv here]

### Characteristics of P0
- Minimal instruction set
- No tag definitions
- No explicit attention to difficult tag boundaries
- No additional reasoning scaffold
- Strongest condition for measuring the effect of added prompt structure

P0 serves as the reference point for all other prompt-engineering experiments.

---

## Why test prompt variants?

Prior POS results suggest that performance is **not equally weak across all POS classes**. Some tags appear to be handled reliably, while a smaller number of tags or tag boundaries are more error-prone. This raises a natural question:

> Can prompt engineering improve performance by helping the model make better decisions specifically on the hardest POS distinctions?

The three prompts below test different answers to that question.

---

## P1 — Definitions-Only Prompt

### Purpose
P1 tests the simplest intervention: adding **short definitions for all tags** while leaving the rest of the task unchanged.

### What changes relative to P0
- Adds one-line descriptions for all valid UD POS tags
- Does **not** add special instructions for hard categories
- Does **not** add a fallback or re-evaluation step

### Hypothesis
If the model benefits from a clearer mapping between labels and categories, P1 may slightly improve performance over P0.

### What this prompt is testing
P1 tests whether **basic category clarification alone** is enough to improve POS tagging.

### Strengths
- Cleanest and simplest ablation over P0
- Easy to interpret experimentally
- Useful for checking whether the model mainly needs label reminders

### Limitations
- Uses prompt space on tags the model may already handle well
- Does not directly target known hard contrasts
- May produce only limited gains if the main problem is ambiguity rather than label knowledge

### Expected outcome
P1 may help a little, but it is not expected to be the strongest variant if errors are concentrated in specific hard tag boundaries rather than spread evenly across the whole tagset.

---

## P2 — Hard-Contrast Instruction Prompt

### Purpose
P2 tests a more targeted intervention: instead of defining every tag equally, it focuses on **the tag boundaries most likely to cause errors**.

### What changes relative to P0
- Adds explicit distinction rules for ambiguity-prone contrasts such as:
  - `SCONJ` vs `ADP` vs `ADV`
  - `PART` vs `ADP` vs `ADV`
  - `AUX` vs `VERB`
  - `PROPN` vs `NOUN`
  - `SYM` vs `X`
- Instructs the model to use `X` only as a last resort
- Keeps output format and evaluation setup identical to P0

### Hypothesis
If most remaining errors come from **difficult decision boundaries**, then targeted instructions should improve performance more efficiently than general definitions.

### What this prompt is testing
P2 tests whether **task decomposition by hard linguistic contrasts** produces a better outcome than a generic POS tagging instruction.

### Strengths
- Focuses prompt budget on the most linguistically difficult distinctions
- Better aligned with a category-level error analysis approach
- More likely than P1 to improve macro-F1 if weaker tags are the main issue

### Limitations
- Still relies on a single-pass tagging decision
- May help only if the chosen contrasts really are the dominant source of error
- Does not explicitly encourage the model to pause or re-check hard cases

### Expected outcome
P2 is expected to outperform P1 if POS errors are concentrated in a few difficult categories or boundaries.

---

## P3 — Hard-Contrast + Silent Re-Check Prompt

### Purpose
P3 extends P2 by adding a lightweight internal fallback mechanism. It keeps the hard-contrast instructions, but also tells the model to **silently re-check ambiguity-prone tags before finalizing**.

### What changes relative to P0
- Includes all targeted hard-contrast distinctions from P2
- Adds an instruction to silently re-evaluate tokens that plausibly belong to ambiguity-prone tags:
  - `SCONJ ADP ADV PART AUX VERB NOUN PROPN SYM X`
- Keeps the same output format and evaluation procedure as P0

### Hypothesis
If the model is usually correct on easy tags but makes mistakes on harder cases because it commits too quickly, then a targeted re-check step may improve performance more than either P1 or P2.

### What this prompt is testing
P3 tests whether **structured internal fallback behavior** helps the model resolve hard POS distinctions more accurately.

### Strengths
- Most directly reflects a task-decomposition strategy
- Encourages extra effort only where ambiguity is likely
- Preserves strict comparability with P0 while adding a minimal reasoning scaffold

### Limitations
- Still depends on the model following an implicit internal process
- Improvements may be modest if the model already re-checks ambiguous tokens on its own
- Harder to interpret than P1 because it combines two interventions:
  - targeted contrast instructions
  - silent fallback review

### Expected outcome
P3 is the prompt most likely to improve **macro-F1**, especially if gains come from better handling of weaker tags rather than broad improvements to already-easy categories.

---

## Summary of the prompt family

| Prompt | Main intervention | Experimental question |
|---|---|---|
| **P0** | No added scaffold | How well does the model do with a minimal task instruction? |
| **P1** | Definitions for all tags | Does general category clarification help POS tagging? |
| **P2** | Targeted hard-contrast rules | Does focusing on difficult tag boundaries improve performance? |
| **P3** | Hard-contrast rules + silent re-check | Does a lightweight fallback process improve hard-tag decisions further? |

---

## Predicted ranking

Based on prior POS results and the idea that remaining errors are likely concentrated in harder categories, the expected ranking is:

1. **P3**
2. **P2**
3. **P1**
4. **P0** (baseline)

This prediction is based on the assumption that:
- many easy tags are already near ceiling,
- average performance may hide category-level weaknesses,
- and prompt engineering is most likely to help when it targets ambiguity rather than restating obvious label definitions.

---

## Experimental comparison notes

To keep these prompts side-by-side comparable, the following should remain fixed across runs:
- same model
- same dataset split
- same input format
- same output format
- same scorer
- same batching strategy
- same evaluation metrics

Only the **instruction block** should change.

This makes it possible to interpret differences in performance as the effect of prompt design rather than changes to data handling or evaluation conditions.

---

## Interpretation guide

When comparing results, it is useful to look at:
- **overall accuracy**
- **macro-F1**
- **per-tag F1**

If improvements are real, they may appear more clearly in **macro-F1** and **per-tag performance** than in raw accuracy, especially if the prompt helps mainly on rarer or more difficult tags.

In other words, a successful decomposition-based prompt may not dramatically change the easiest tags, but it may still produce a meaningful analytical improvement by reducing errors in the hardest parts of the task.

---

## Takeaway

These prompt variants are designed to test a broader claim:

> POS tagging performance may improve when prompt design reflects the internal linguistic structure of the task.

Rather than treating POS as one uniform labeling problem, P1–P3 progressively test whether performance improves when the prompt:
1. clarifies label meanings,
2. highlights difficult contrasts,
3. and encourages extra care only on hard decisions.

That makes this prompt family a small but useful experiment in **task decomposition as prompt engineering**.