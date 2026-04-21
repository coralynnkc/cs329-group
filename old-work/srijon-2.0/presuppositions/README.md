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

**P0: direct probability-first labeling**
P0 asks the model to assign E/N/C probabilities directly from the row, with formatting constraints but no explicit class definitions, no anti-plausibility warning, and no forced hard-label step. That makes it a probability-first method.

**P2: decision-first, direct semantic classification**
P2 gives explicit semantic definitions for E, C, and N, warns against treating plausibility as entailment, and then tells the model to use this decision procedure:
ask whether the premise guarantees the hypothesis is true
if not, ask whether it guarantees the hypothesis is false
if neither, choose Neutral
then assign probabilities after the hard label is decided.
So P2 is not just “stronger definitions.” It is also: classification before distribution generation , a sequential direct classification rule rather than free probability allocation.

**P4: explicitly decomposed two-question reasoning**
P4 says “Do not decide the label in one step” and explicitly frames the task as two binary questions:
Does the premise make the hypothesis definitely true?
Does the premise make the hypothesis definitely false?
Then it maps those answers to E/N/C. After that, it asks for probabilities.
So P4 is:
also classification before distribution generation
but more explicitly factorized into two binary judgments than P2.


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
## Findings so far

- **Prompt structure matters for semantic reasoning.**  
  The main contrast is between **P0** (probability-first) and **P2/P4** (decision-first). Forcing class commitment before probability assignment changes model behavior in meaningful ways.

- **P2 and P4 are not fully distinct methodologies.**  
  Both are **decision-first prompts** that use truth/falsity-style semantic framing.  
  The difference is that **P4 makes the decomposition more explicit**, while **P2 uses a sequential guarantee-based rule**.  
  So the strongest clean contrast is still **P0 vs P2/P4**, not **P2 vs P4 as totally different reasoning systems**.

- **P2 most strongly improves the Entailment–Neutral (E/N) boundary.**  
  This is clearest in English, where P2 most strongly reduces the model’s tendency to treat plausible or compatible hypotheses as Entailment.

- **P2 appears to overcorrect.**  
  P2 improves Neutral handling, but often at the cost of shifting too many Contradiction cases into Neutral.  
  In other words, it fixes part of the E/N problem by creating more N/C confusion.

- **P4 does not overcorrect in the same way.**  
  P4 is more balanced than P2, but it also does not preserve P2’s strongest E/N gains, especially in English.  
  In the hardest cases, P4 often looks like a partial retreat toward the older P0-style behavior.

- **P4 does not clearly outperform P2 overall.**  
  The results are mixed:
  - **P2** is slightly better on average hard-label metrics like accuracy and Macro-F1.
  - **P4** tends to be somewhat better on probability-quality metrics like log loss and Brier score.
  So neither prompt is a universal winner.

- **P0 is stronger than it first appeared after rerunning DE.**  
  The original DE-P0 run had ID mismatch issues; after rerunning it cleanly, P0’s average performance improved.  
  This reduced the size of the apparent P0 → P2/P4 gains, but did not eliminate the main pattern.

- **English remains the hardest language.**  
  English consistently shows the clearest class-boundary instability:
  - under **P0**, Neutral collapses into Entailment
  - under **P2**, Neutral improves but Contradiction collapses into Neutral
  - under **P4**, English still struggles and often drifts back toward the P0-style pattern

- **French is the easiest and most stable language.**  
  French performs strongly across prompts and achieves the best overall results under P4.  
  This suggests the task is not equally difficult across languages.

- **The most important metric for hard-label performance is Macro-F1.**  
  Macro-F1 is the best headline metric because it evaluates whether the model distinguishes all three classes well, not just whether it gets the top label right often.

- **The most important metric for probability quality is log loss.**  
  Log loss best captures whether the model assigns meaningful probability mass to the correct class.  
  Brier score is also useful as a more stable, easier-to-interpret probability-fit metric.

- **Centroid is useful, but not evaluative.**  
  Centroid helps explain *how* prompts change class geometry in probability space, especially whether Neutral drifts toward Entailment or Contradiction.  
  But centroid is not a primary evaluation metric because it averages away item-level correctness.

- **The strongest current conclusion is about class-boundary behavior, not raw score wins.**  
  The experiment shows that prompt design changes which semantic distinctions the model prioritizes.  
  The key result is not simply that one prompt is “best,” but that different prompts improve or distort different class boundaries.

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
