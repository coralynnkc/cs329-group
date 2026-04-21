# Pronoun Resolution Prompt Experiments: Full Documentation

## Purpose

This document is the master record for the pronoun-resolution prompt experiments in this repository.

Its job is to make the experimental workflow:

- clear
- comprehensive
- reproducible
- reviewable by someone outside the team

This document records:

1. the dataset source and preprocessing assumptions
2. the split-generation procedure
3. the exact prompt conditions tested
4. the exact inference settings used
5. the validation and scoring procedure
6. the stage-by-stage experiment flow
7. the criteria used to select prompts between stages
8. the qualitative error-analysis framework
9. the output files that should exist after the experiments are run

This document should be updated as the experiments are executed. It is intended to be the definitive reference for how the pronoun-resolution prompt tests were conducted.

---

# 1. Task Definition

## 1.1 What is being evaluated

This experiment evaluates **pronoun resolution framed as forced-choice antecedent selection**.

Each item contains:

- a sentence or short context with a blank / underscore
- two candidate antecedents
- a gold answer indicating whether the blank refers to `Option A` or `Option B`

The model is asked to choose between exactly two candidate antecedents.

## 1.2 Why this framing was chosen

This framing was chosen because it matches the current state of the pronoun-resolution materials in this repository and supports clean prompt comparison.

It also makes automatic evaluation straightforward, because the required output is a single discrete choice.

## 1.3 What this experiment is not

This experiment is **not** full end-to-end coreference clustering.

That distinction matters for evaluation:

- for this experiment, **accuracy** is a valid primary metric because the output is a forced A/B choice
- but accuracy is **not sufficient by itself**
- this experiment also tracks robustness, parseability, refusal behavior, and token usage

Metrics such as **MUC**, **B³**, and **CEAF** are primarily intended for cluster-based coreference systems and are therefore not the main evaluation metrics for this specific experiment.

---

# 2. Repository Location

All files for this experiment live in:

```text
pronoun_resolution/testing/