# Presuppositions Experiment README

This directory contains multilingual presupposition-labeling experiments using LLMs.

Clean, pretty data: https://docs.google.com/spreadsheets/d/1lgxXQ80iZjNAnLjoxwhp_ALLh-r1eJDfS4ktZK4ubbs/edit?gid=48303836#gid=48303836 **(start here)**

Writeup: https://docs.google.com/document/d/1FE2MNvQg3cjaUybsyY9nZky-q5gvIz_ROeis55yzFh4/edit?tab=t.0


[consider everything below, especially conclusions, to be provisional. I don't necessarily agree that P2 is better than P4]

## Goal

Test which **semantic reasoning structure** works best for 3-way labeling:

- **E** = Entailment
- **N** = Neutral
- **C** = Contradiction

The core question is not just “which prompt scores highest,” but **how prompt structure changes class boundaries**, especially:

- **E vs N**: does the model confuse plausibility with entailment?
- **N vs C**: does the model overuse Neutral when contradiction is present?

---

## Dataset + task format

Each CSV row has:

- `item_id`
- `premise`
- `hypothesis`

The model returns:

```csv
item_id,e_probability,n_probability,c_probability
```

Probabilities must sum to 1. We score both:

- the **top label** (argmax of E/N/C)
- the **full probability distribution**

---

## Prompts compared

### P0 — probability-first baseline
Minimal prompt. The model reads each pair and directly assigns E/N/C probabilities.

What it tests:
- weak semantic guidance
- likely to rely on plausibility heuristics

### P2 — strict semantic boundary prompt
Adds explicit class definitions:

- **E**: hypothesis is necessarily true
- **C**: hypothesis is necessarily false
- **N**: neither is guaranteed

Also warns:
- plausible ≠ entailment
- unlikely ≠ contradiction

What it tests:
- whether stronger semantic framing improves the **E/N** boundary

### P4 — two-question decomposition prompt
The model answers two binary questions first:

1. Is the hypothesis definitely true?
2. Is the hypothesis definitely false?

Then maps to:
- true / not false → **E**
- false / not true → **C**
- neither → **N**

What it tests:
- whether factorizing the decision improves difficult boundaries, especially **N/C**

---

## Why these prompts matter

These are not just wording variants. They test different **reasoning structures**:

P0 asks the model to generate an E/N/C probability distribution directly, while P2 first forces a discrete semantic classification and only then asks for a probability distribution. This means P2 differs from P0 both in semantic definitions and in the order of reasoning. Because of this, P2 should be interpreted as a decision-first prompt, not just a more explicit version of P0. P4 forces two decision boundaries to further clarify boundaries prior to assigning the probability distribution.

- **P0**: one-step probability judgment
- **P2**: one-step judgment with strict semantic definitions
- **P4**: two-step decomposed semantic judgment

The experiment asks whether stronger decision structure produces more linguistically grounded labeling.

---

## Metrics

We use five main diagnostics.

### 1. Accuracy
How often the model’s highest-probability label matches the gold label.

Use:
- simplest overall success rate

Limitation:
- can hide class imbalance and boundary failures

### 2. Macro-F1
Average F1 across E, N, and C, giving each class equal weight.

Use:
- best single summary of **balanced label performance**
- most important hard-label metric in this project

### 3. Log loss
Measures how much probability the model assigns to the true class. Penalizes confident mistakes heavily.

Use:
- best metric for **probability quality**
- especially useful when two prompts have similar accuracy but different confidence behavior

### 4. Brier score
Measures how close the full E/N/C probability vector is to the one-hot gold label.

Use:
- broad probability-fit metric
- easier to interpret than log loss
- lower is better

### 5. Centroid (diagnostic only)
For each gold class, average the predicted E/N/C vectors across all items in that class.

Use:
- shows **class geometry**
- useful for diagnosing whether, for example, gold-N items drift toward E

Important:
- **centroid is not a primary evaluation metric**
- it averages away item-level variation
- two systems can have similar centroids but very different item-level correctness

### Practical metric priority

Use this hierarchy:

- **Macro-F1** → main hard-label metric
- **Log loss** → main probability-quality metric
- **Accuracy** → supporting summary
- **Brier** → supporting probability metric
- **Centroid** → explanatory diagnostic

---

## Scoring workflow

### 1. Generate predictions
Run a prompt over a language-specific CSV and save results in:

```text
results/<model_name>/
```

Each prediction file should be named like:

```text
chat_5.4_dev_en_p0.csv
chat_5.4_dev_fr_p2.csv
chat_5.4_dev_vi_p4.csv
```

### 2. Run the batch scorer
From the `presuppositions/` root:

```bash
python3 scripts/batch_scorer_evaluation.py   --presup-dir .   --results results/chat_5.4   --output results/chat_5.4/results_summary.json
```

### 3. Check that matching is correct
The scorer matches prediction files to gold files by language code in the filename:

- `*_en_*` → `en/full/...`
- `*_fr_*` → `fr/full/...`
- etc.

Make sure:
- filenames contain the correct language code
- each language has the correct `full` gold file
- row counts and `item_id`s line up

### 4. Review outputs
The scorer reports:
- accuracy
- macro-F1
- log loss
- Brier
- classwise precision / recall / F1
- centroid summaries
- nearest-centroid diagnostics
- coverage / missing rows / extra IDs

---

## Main findings so far

### 1. Prompt structure matters
Changing semantic reasoning structure changes which class boundaries the model gets right or wrong.

### 2. P2 most strongly improves the E/N boundary
P2 reduces the model’s tendency to treat “plausible” as entailment.

Most visible in English:
- P0 showed strong **Neutral → Entailment** drift
- P2 moved many of those cases back toward Neutral

### 3. P2 overcorrects
P2 often improves Neutral handling but can push too many true contradictions into Neutral.

So P2 is a good **probe prompt**, but not always the best practical prompt.

### 4. P4 is the best balanced overall prompt
P4 is the best compromise:
- good class balance
- strong probability behavior
- less contradiction collapse than P2

### 5. English is hardest
English is the clearest failure case across prompts.

Likely reason:
- the model treats many English hypotheses as **plausible continuations** rather than strict semantic consequences

### 6. French is easiest
French is the strongest and most stable language in these runs.

Possible reason:
- cleaner class separation in the dataset / translation
- less pragmatic overreading than English

### 7. Hard-label quality and probability quality are not the same
A prompt can improve:
- accuracy / Macro-F1

without equally improving:
- log loss / Brier

That is why both hard-label and probability metrics are necessary.

---

## How to interpret centroid in this project

Use centroid to answer:

- Are gold-N items drifting toward E?
- Are gold-C items being treated like unresolved N?
- Does a prompt make class clusters cleaner?

Do **not** use centroid to decide which prompt “wins.”

Best one-line explanation:

> Centroid is a descriptive diagnostic of class geometry, not a primary performance metric.

---

## Recommended default interpretation

If reporting one metric from each category:

- **Macro-F1** = headline hard-label metric
- **Log loss** = headline probability-quality metric
- **Centroid** = diagnostic explanation of class-boundary behavior

---

## Recommended follow-up work

Highest-value next steps:

1. Run **P4 on a larger sample or full set**
2. Do a focused **English error audit**:
   - N predicted as E
   - C predicted as N
   - E predicted as N
3. Compare **hard-label-only** vs **probability-output** versions of the same prompt
4. Test a **contradiction-anchored** prompt:
   - first decide compatibility
   - then split compatible cases into E vs N
5. Replicate the final prompt family on another model

Probably not worth doing:
- lots of minor wording variants
- more probability-only prompts
- more file-compliance prompt tricks

---

## Bottom line

This experiment shows that **semantic decision framing matters** for presupposition labeling.

- **P0** is a useful baseline, but weakly constrained
- **P2** is the best prompt for probing whether the model is confusing plausibility with entailment
- **P4** is the best all-around prompt for balanced real-world labeling

Use standard evaluation metrics for performance, and use centroid to explain **why** prompts fail or succeed.
