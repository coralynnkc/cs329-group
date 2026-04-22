# Presuppositions Experiment README

This directory contains the broader prompt-benchmarking presupposition work copied from `srijon-2.0/presuppositions/`.

It contains **two related but distinct sub-experiments** that both use 3-way semantic labeling:

- **Prompt engineering on CONFER (English only)**  
  This is the focused English presupposition benchmark centered on CONFER and stored primarily in [`confer_en/`](confer_en/) and the `results/CONFER-*` folders.
- **Prompt engineering on the multilingual benchmark ("MLM" in project shorthand)**  
  This is the multilingual presupposition-labeling benchmark across `de`, `fr`, `hi`, `ru`, and `vi`, stored in the language folders at the root of this directory. An archival English split still exists in the tree for provenance, but the current headline multilingual comparison excludes English because English is benchmarked more cleanly in the dedicated CONFER experiment.

The internal layout has been kept intentionally close to the original source so that the existing scripts and result folders still work with minimal path changes.

Clean, pretty data: https://docs.google.com/spreadsheets/d/1lgxXQ80iZjNAnLjoxwhp_ALLh-r1eJDfS4ktZK4ubbs/edit?gid=48303836#gid=48303836 **(start here)**

Writeup: https://docs.google.com/document/d/1FE2MNvQg3cjaUybsyY9nZky-q5gvIz_ROeis55yzFh4/edit?tab=t.0

[Consider everything below, especially the interpretive conclusions, to be provisional. The experimental assets are preserved here as working documentation of the benchmark setup, not as a final paper-ready claim set.]

## TL;DR

### 1. CONFER prompt-engineering experiment

- Task: English-only presupposition classification with labels `E`, `N`, `C`
- Dataset source: **CONFER**
- Main question: which prompt structure best teaches the model the benchmark's presupposition-sensitive label boundary?
- Practical takeaway: the current writeups in this tree suggest that **P1** is the strongest prompt family on CONFER, especially because it anchors the task well by example rather than by abstract NLI instructions alone.

### 2. Multilingual prompt-engineering experiment

- Task: presupposition-style 3-way semantic classification across `de`, `fr`, `hi`, `ru`, and `vi`
- Dataset sources:
  - **French / German / Hindi / Russian / Vietnamese** come from **XNLI**
- Main question: how do different prompt structures change the model's `E / N / C` decision boundaries across languages?
- Practical takeaway: on the current clean multilingual comparison, **P1 is the strongest overall prompt family**, beating `P0` on every non-English language and also outperforming `P2` on average. The present multilingual story is therefore stronger than before: `P1` is not just a good English CONFER prompt, it also transfers well to the non-English MLM benchmark.

## Overall Goal

Both sub-experiments test which **semantic reasoning structure** works best for 3-way labeling:

- **E** = Entailment
- **N** = Neutral
- **C** = Contradiction

The core question is not just “which prompt scores highest,” but **how prompt structure changes class boundaries**, especially:

- **E vs N**: does the model confuse plausibility with entailment?
- **N vs C**: does the model overuse Neutral when contradiction is present?

## The Two Sub-Experiments

### A. Prompt engineering on CONFER

This is the English-only benchmark stored in:

- [`confer_en/`](confer_en/)
- `results/CONFER-chat-5.4/`
- `results/CONFER-opus-4.6/`

This sub-experiment uses CONFER-style inputs and gold answers, then compares prompt variants such as `p0`, `p1`, `p2`, `p4`, `p5`, `p6`, `p7`, `p8`, and `p9`.

The dedicated scorer for this setup is:

```bash
python3 scripts/batch_scorer_CONFER.py --gold confer_en/presupposition_answers.csv --results results/<folder> --output results/<folder>/results_summary.json
```

### B. Prompt engineering on the multilingual benchmark

This is the broader multilingual benchmark stored in:

- `de/`
- `en/`
- `fr/`
- `hi/`
- `ru/`
- `vi/`

This sub-experiment evaluates the same style of prompt variants across multiple languages and then scores prediction files against the corresponding language-specific gold files.

For analysis purposes, the current headline multilingual comparison uses the non-English set:

- `de/`
- `fr/`
- `hi/`
- `ru/`
- `vi/`

The `en/` directory is retained for provenance and script compatibility, but English results are not part of the main multilingual comparison because English is already covered by the cleaner, dedicated CONFER benchmark.

The dedicated scorer for this setup is:

```bash
python3 scripts/batch_scorer_evaluation.py --presup-dir . --results results/<folder> --output results/<folder>/results_summary.json
```

## Data Provenance

### CONFER experiment data

The English-only CONFER materials in [`confer_en/`](confer_en/) come from the CONFER presupposition benchmark.

Files in that folder:

- `presupposition_input.csv`
- `presupposition_answers.csv`

These are already prepared as benchmark-ready evaluation files with sample structure and gold answers for scoring.

### Multilingual benchmark data

The multilingual benchmark mixes two sources:

- **English (`en`)**: CONFER
- **French / German / Hindi / Russian / Vietnamese (`fr`, `de`, `hi`, `ru`, `vi`)**: XNLI

This is the important provenance caveat in this experiment family: the multilingual tree has a shared surface schema, but it is **not** a single homogeneous dataset. English and non-English rows come from different underlying corpora.

Because of that provenance mismatch, and because English is already evaluated more directly in the CONFER experiment, the current README treats the multilingual benchmark as a **non-English transfer benchmark** in its topline analysis. The English MLM files are still preserved here, but they are not used for the headline cross-language claims.

## How The Multilingual Data Was Processed

Based on the normalization notes preserved from `srijon-2.0`, the multilingual presupposition files were processed into a consistent schema:

- `source/` files contain the model-readable source rows with gold labels present
- `inference/` files remove the gold label and keep only the model input columns
- `full/` files add scorer-facing columns for model outputs and correctness checks

In practice, the schemas look like this:

### `source/`

```csv
item_id,premise,hypothesis,gold_label
```

### `inference/`

```csv
item_id,premise,hypothesis
```

### `full/`

```csv
item_id,premise,hypothesis,gold_label,model_label,correct
```

The `item_id` column is the stable join key used by the scorers. In this task family, IDs follow the `ps_<lang>_<index>` convention, for example `ps_en_000010`.

The split files currently present in each language folder include:

- `_master`
- `_train`
- `_dev`
- `_test`
- `_sample100`

For the current prompt benchmarking runs, the scorer most often targets the `full/` files and uses filename language codes to find the correct gold file automatically.

## How The CONFER Data Was Processed

The CONFER-specific prompt sweep uses a different packaging style than the multilingual tree.

Instead of `source/inference/full` per language, it uses two prepared benchmark files in [`confer_en/`](confer_en/):

### Model input

```csv
sample_id,row_id,uid,type,premise,hypothesis
```

### Gold answers

```csv
sample_id,row_id,uid,type,gold_label
```

This makes the CONFER prompt sweep easy to run as a prompt-engineering benchmark:

- send the input file through a prompt variant
- save probability outputs or label outputs in `results/<folder>/`
- score against `presupposition_answers.csv`

The CONFER scorer is also more flexible about identifier matching than the multilingual scorer, because some runs key predictions by `uid` while others key them by `sample_id` + `row_id`.

## Folder Map

- `confer_en/` -> English-only CONFER input and answer files used by the CONFER prompt sweep
- `de/`, `en/`, `fr/`, `hi/`, `ru/`, `vi/` -> multilingual data splits and derived files
- `prompts/` -> prompt variants (`p0`, `p1`, `p2`, `p4`, `p5`, `p6`, `p7`, `p8`, `p9`)
- `results/` -> model outputs and JSON summaries
- `scripts/` -> scorers for multilingual evaluation and CONFER evaluation

## Shared Task Format

Across both sub-experiments, the model output is typically probabilistic:

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

**P1: few-shot benchmark-anchored labeling**
P1 keeps the probability-output format but adds benchmark-shaped examples that demonstrate the intended `E / N / C` boundary directly. In practice, this has become the most important comparison point in the project because it performs strongly on CONFER English and also transfers well to the non-English multilingual benchmark.

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
From the `presuppositions-all/prompt_benchmarking/` root:

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
## Current multilingual snapshot: P0 vs P1 vs P2

The newest clean multilingual comparison asks a simpler question than the earlier `P0 / P2 / P4` sweep: how does the stronger few-shot `P1` prompt compare against both the minimal baseline `P0` and the decision-first `P2` prompt on the non-English multilingual benchmark?

For the current headline comparison, we exclude the MLM English file and compare only `de`, `fr`, `hi`, `ru`, and `vi`.

### Non-English MLM results for Chat 5.4

| Language | P0 Acc | P1 Acc | P2 Acc | Best Acc | P0 Macro-F1 | P1 Macro-F1 | P2 Macro-F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `de` | 0.7900 | 0.8500 | 0.8300 | **P1** | 0.8161 | 0.8499 | 0.8288 |
| `fr` | 0.8500 | 0.8700 | 0.8400 | **P1** | 0.8487 | 0.8709 | 0.8417 |
| `hi` | 0.7500 | 0.8000 | 0.8000 | **P1 / P2 tie** | 0.7509 | 0.8016 | 0.8039 |
| `ru` | 0.7900 | 0.8200 | 0.7800 | **P1** | 0.7884 | 0.8197 | 0.7837 |
| `vi` | 0.7800 | 0.7900 | 0.7800 | **P1** | 0.7831 | 0.7920 | 0.7811 |
| **Average** | **0.7920** | **0.8260** | **0.8060** | **P1** | **0.7974** | **0.8268** | **0.8078** |

Interpretation:

- `P1` is the strongest overall prompt family on this non-English MLM comparison.
- `P1` improves over `P0` in **every non-English language** in both accuracy and Macro-F1.
- `P1` also beats `P2` on average accuracy and average Macro-F1.
- `P2` is competitive, but it only matches `P1` on accuracy in `hi` and trails it in the other four languages.
- The largest `P0 -> P1` gains appear in `de` and `hi`.
- `fr` remains the strongest overall language, and `P1` is also the best prompt there.

### Why English is excluded from the MLM headline table

The MLM English file is preserved in the repository, but it is no longer part of the main benchmark claim for two reasons:

1. English is already evaluated more directly in the dedicated CONFER experiment.
2. The latest `chat_5.4` MLM English `P1` run had severe ID mismatch / coverage problems, so it is not a fair comparison point for prompt effects.

---
## Findings so far

- **P1 is now the most important multilingual result.**  
  On the clean non-English multilingual comparison, `P1` beats `P0` in every language we re-scored and also beats `P2` overall. That makes `P1` more than just the strongest CONFER-English prompt family: it also appears to transfer well across the multilingual benchmark.

- **The multilingual benchmark should be interpreted as a non-English transfer test.**  
  English is still preserved in the directory tree, but the headline comparison should focus on `de`, `fr`, `hi`, `ru`, and `vi`. That keeps the multilingual claim methodologically cleaner because English already has its own dedicated CONFER benchmark.

- **Few-shot benchmark anchoring looks more useful than either lighter prompting or stricter decision-first prompting.**  
  The multilingual comparison now points in the same direction as the English CONFER results: benchmark-shaped examples appear to teach the label boundary better than either the minimal probability-only baseline `P0` or the more rule-structured `P2` prompt.

- **French remains the strongest language overall.**  
  `fr` is still the highest-scoring language in the current multilingual runs, and it remains strong under both prompts.

- **German and Hindi show the clearest prompt effects.**  
  The largest `P0 -> P1` improvements appear in `de` and `hi`, and `hi` is also the one language where `P2` remains genuinely competitive with `P1`.

- **Macro-F1 remains the best headline hard-label metric.**  
  Macro-F1 is still the most useful single summary because it checks whether the model is separating all three classes well rather than winning by overusing the largest or easiest class.

- **Probability metrics still matter, but they are secondary to clean coverage.**  
  Log loss and Brier remain important for probability quality, but they are only meaningful once a run has clean ID alignment and near-complete coverage.

- **Centroid is useful, but not evaluative.**  
  Centroid helps explain *how* prompts change class geometry in probability space, especially whether Neutral drifts toward Entailment or Contradiction.  
  But centroid is not a primary evaluation metric because it averages away item-level correctness.

- **The main current claim is now stronger and simpler.**  
  For the multilingual benchmark, the clearest defensible result is that `P1` is the best current non-English prompt family: it yields a modest but consistent boost over `P0` and also outperforms `P2` overall.

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

1. Do a focused **non-English error audit** on `P1`:
   - N predicted as E
   - C predicted as N
   - E predicted as N
2. Compare **hard-label-only** vs **probability-output** versions of the same prompt
3. Test a **contradiction-anchored** prompt:
   - first decide compatibility
   - then split compatible cases into E vs N
4. Replicate the final prompt family on another model

Probably not worth doing:
- lots of minor wording variants
- more probability-only prompts
- more file-compliance prompt tricks

---

## Bottom line

This experiment shows that **semantic decision framing matters** for presupposition labeling.

- **P0** is a useful baseline, but weakly constrained
- **P1** is currently the strongest multilingual prompt family
- the best current multilingual claim is that **P1 improves non-English MLM performance over both P0 and, overall, P2**

Use standard evaluation metrics for performance, and use centroid to explain **why** prompts fail or succeed.
