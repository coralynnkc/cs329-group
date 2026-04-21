# CONFER (English): why P1 is so much stronger than the other presupposition prompts

## Executive summary

Across the CONFER English prompt sweep, **P1 is the clear standout**. It is the best-performing prompt for **Chat 5.4** among the six prompts scored so far, and it is also dramatically better than **P0** for **Opus 4.6** in the two-prompt comparison currently available.

The most cautious explanation is **not** simply that “few-shot works.” A narrower and better-supported claim is this:

> **P1 appears to outperform the other prompts because it anchors the task as presupposition-sensitive inference rather than generic semantic entailment, and it does so with minimal overhead.**

In other words, P1 gives the model three concrete demonstrations of what **Entailment**, **Neutral**, and **Contradiction** look like **for this benchmark**. The other prompts either (a) under-specify the task, or (b) over-specify it in a way that pushes the model toward a generic “guarantee / definitely true / compatibility” notion of inference that is not well aligned with presupposition projection.

That interpretation fits both the prompt texts and the score patterns. It is especially visible in the **Neutral** class, where P1 produces the largest improvement over weaker prompts.

## Scope and caution

This document is intended as an explanation of the current results, not a definitive causal proof.

Two points matter here:

1. The present evidence strongly suggests that **P1 is doing something qualitatively different and better** than the rest of the prompt set.
2. The current experiment does **not** isolate every causal variable. P1 differs from P0 not only in “few-shot” status, but also in how it implicitly teaches the label boundary.

So the right conclusion is that **P1 is the best-performing prompt in the current sweep, and its advantage is most plausibly due to better task anchoring**. The safer phrasing is not “few-shot universally helps presupposition tasks,” but rather “for CONFER, this particular one-example-per-class prompt appears to teach the model the benchmark’s label geometry much more effectively than the alternatives.”

---

## 1) Results overview

### Table 1. Chat 5.4 on CONFER English (300 items)

| Prompt | Accuracy | Macro-F1 | Log Loss | Brier Score | F1-E | F1-N | F1-C | Coverage | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **P1** | **0.7867** | **0.7841** | **0.6815** | **0.3686** | **0.8722** | **0.6923** | **0.7879** | **1.0000** | Best overall |
| P2 | 0.7100 | 0.7094 | 0.8589 | 0.4917 | 0.7845 | 0.5700 | 0.7738 | 1.0000 | Second-best |
| P0 | 0.6933 | 0.6828 | 0.9081 | 0.5244 | 0.7857 | 0.4889 | 0.7738 | 1.0000 | Minimal baseline |
| P4 | 0.4767 | 0.4644 | 1.6368 | 0.9029 | 0.4106 | 0.5094 | 0.4733 | 1.0000 | Heavy Neutral bias |
| P5 | 0.4700 | 0.4563 | 1.5819 | 0.8962 | 0.3893 | 0.5062 | 0.4733 | 1.0000 | Very similar to P4 |
| P6 | 0.3967 | 0.3525 | 1.5022 | 0.9054 | 0.4000 | 0.4924 | 0.1651 | 0.9433 | Incomplete / malformed output |

### Table 2. Opus 4.6 on CONFER English (300 items scored so far)

| Prompt | Accuracy | Macro-F1 | Log Loss | Brier Score | F1-E | F1-N | F1-C | Coverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **P1** | **0.9200** | **0.9192** | **0.3649** | **0.1618** | **0.8959** | **0.8667** | **0.9950** | **1.0000** |
| P0 | 0.6033 | 0.5700 | 1.0121 | 0.6163 | 0.7046 | 0.2222 | 0.7831 | 1.0000 |

### Table 3. P1 gain over P0

| Model | Accuracy gain | Macro-F1 gain | F1-E gain | F1-N gain | F1-C gain |
|---|---:|---:|---:|---:|---:|
| Chat 5.4 | +0.0934 | +0.1013 | +0.0865 | +0.2034 | +0.0141 |
| Opus 4.6 | +0.3167 | +0.3492 | +0.1913 | +0.6445 | +0.2119 |

Two things stand out immediately:

- For **Chat 5.4**, P1 is clearly best, but the improvement is concentrated most heavily in **Neutral**.
- For **Opus 4.6**, the jump from P0 to P1 is enormous across **all three classes**, and especially dramatic for **Neutral** and **Contradiction**.

That pattern is exactly what we would expect if P1 is improving the model’s understanding of the **decision boundary**, not merely making it more verbose or more careful.

---

## 2) What P1 changes

### Table 4. Prompt design differences that matter most

| Prompt | Core framing | Examples | Boundary style | Likely inductive bias |
|---|---|---|---|---|
| P0 | Minimal batch prompt | None | Bare label names only | Model must infer the task from prior knowledge |
| **P1** | Same batch scaffold as P0, but with three labeled demonstrations | **Yes: one E, one N, one C** | Implicit, example-based | Model sees what the label space looks like on this benchmark |
| P2 | Generic semantic inference prompt | No | “Guarantee true / guarantee false / otherwise N” | Standard necessity-based NLI |
| P4 | Generic semantic inference prompt | No | “Definitely true / definitely false / otherwise N” | Strict resolution criterion, often conservative |
| P5 | Generic semantic inference prompt | No | Compatibility test, then guarantee test | Standard NLI logic, not presupposition-specific |
| P6 | Underperformed and returned incomplete output | Unknown / not central here | Not reliable for interpretation | Output instability plus poor performance |

P1 does **not** radically change the file format or scoring setup. It keeps the same basic probability-output scaffold as P0. What it adds is just three demonstrations, one per class.

That means its advantage is unlikely to be explained by output format alone. The more plausible explanation is that **those demonstrations give the model the right semantic frame for the task**.

---

## 3) Why P1 is likely better

### 3.1 P1 teaches the benchmark’s label geometry

CONFER is not just ordinary entailment. The task is explicitly about **presupposition triggers** and their behavior in different environments, including negation, questions, and belief contexts. The original presupposition README states this directly:

- the task is to classify whether the premise **triggers / preserves**, **does not clearly trigger or cancel**, or **cancels / contradicts** the presupposition in the hypothesis; and
- the core challenge is **projection**, because presuppositions can survive under negation, questions, and belief contexts.

P1 appears to work because its three examples give the model a compact demonstration of this label space:

- one case where projected content still counts as **Entailment**,
- one case where superficially similar structure is actually **Neutral**, and
- one case of genuine **Contradiction**.

This matters more than it may look at first glance. P1 is not just showing three arbitrary examples. It is showing the model the difference between:
- a presupposition that **projects**,
- a presupposition-like structure that **does not license entailment**, and
- a case where the hypothesis is actively **inconsistent** with the premise.

That is a very strong form of task anchoring.

### 3.2 P0 under-specifies the task

P0 is operationally clean, but semantically thin. It asks the model to assign E/N/C probabilities for each row, but it does not really define how those labels should be interpreted **for presupposition**. There is no projection guidance and no examples.

That leaves the model to rely on its own default notion of entailment. On CONFER, that is risky, because a generic surface-entailment strategy can easily mis-handle cases where the relevant content is presupposed rather than directly asserted.

The score patterns support exactly this reading.

For **Chat 5.4**, P0 is respectable overall, but much weaker on **Neutral** than P1:

- P0 N F1 = **0.4889**
- P1 N F1 = **0.6923**

For **Opus 4.6**, P0 is much worse on Neutral:

- P0 N F1 = **0.2222**
- P1 N F1 = **0.8667**

So P0 is not failing because it is badly formatted. It is failing because it leaves too much of the task definition implicit.

### 3.3 P2 / P4 / P5 anchor the wrong task

The more elaborate prompts do provide semantic guidance, but it is mostly the wrong kind of guidance for this dataset.

P2 asks whether the premise **guarantees** the hypothesis is true or false.
P4 asks whether the premise makes the hypothesis **definitely true** or **definitely false**.
P5 uses a two-step framework: first **compatibility**, then whether the premise **guarantees** the hypothesis.

These are coherent frameworks for **generic NLI**, but CONFER is not a generic NLI benchmark. It is specifically about **presupposition reasoning** and **projection**.

That mismatch matters. If a model is told to label Entailment only when the hypothesis is made “definitely true” or “guaranteed in every possible situation,” it may become too reluctant to treat projected content as entailed, especially in embedded contexts. Conversely, if it treats many unresolved cases as compatible-but-not-guaranteed, it may overuse **Neutral**.

That is exactly what happens for Chat 5.4 with P4 and P5:

- both prompts collapse toward **Neutral**,
- both perform far worse than P1 on every overall metric,
- and both assign very high average Neutral probability even to gold E and gold C items.

In other words, those prompts are not poorly written. They are simply better suited to a different task.

### 3.4 P1 improves the crucial boundary: Entailment vs Neutral

The clearest signal in the current results is that P1 improves the **E/N boundary**.

For Chat 5.4, compared with P0:
- accuracy rises from **0.6933** to **0.7867**
- macro-F1 rises from **0.6828** to **0.7841**
- the largest class-specific jump is **F1-N: +0.2034**

For Opus 4.6, compared with P0:
- accuracy rises from **0.6033** to **0.9200**
- macro-F1 rises from **0.5700** to **0.9192**
- the largest class-specific jump is again **F1-N: +0.6445**

That is a strong hint that P1 is teaching the model where **Neutral actually lives**. It is not merely making the model more confident; it is helping the model avoid collapsing unresolved cases into Entailment, and in Opus it also sharpens the Contradiction boundary dramatically.

### 3.5 P1 also improves calibration-like behavior

The probability summaries tell a similar story.

For Chat 5.4:
- on gold **N** items, P0 averages roughly **0.48 E / 0.48 N / 0.04 C**
- on the same class, P1 shifts to roughly **0.33 E / 0.61 N / 0.06 C**

For Opus 4.6:
- on gold **N** items, P0 averages roughly **0.76 E / 0.17 N / 0.07 C**
- on the same class, P1 shifts to roughly **0.28 E / 0.63 N / 0.09 C**

For gold **C** items, Opus also becomes much cleaner under P1:
- P0 averages about **0.60 C**
- P1 averages about **0.89 C**

So P1 is not only improving hard-label metrics; it is also making the model’s probability mass line up better with the gold classes.

---

## 4) Why the jump is so large

This is the most striking point in the current presupposition work.

The P1 jump is larger than the prompt-to-prompt changes we have usually seen elsewhere in the project. The most plausible reason is that **CONFER is unusually sensitive to task framing**. Small wording differences can matter more when the task depends on recognizing a specific semantic phenomenon — here, presupposition projection — rather than on generic sentence-pair inference.

P1 seems to hit an unusually effective balance:

- it is still short,
- it keeps the batch setup simple,
- it does not overload the model with extra metareasoning,
- but it gives just enough benchmark-specific structure to tell the model what counts as E, N, and C on this dataset.

That combination may explain why it works so much better than:
- a fully minimal prompt (P0), and
- more rule-heavy prompts that steer the model toward generic NLI criteria (P2 / P4 / P5).

This is also why it would be a mistake to summarize the result as “more prompt engineering is better.” The current evidence points in the opposite direction: **the best prompt is not the longest or most procedural one. It is the one that teaches the right task in the simplest way.**

---

## 5) Why the other prompts are not “unanchored,” but mis-anchored

A useful way to phrase the result is:

> The weaker prompts are not failing to anchor the task at all. They are anchoring the wrong task.

- **P0** anchors the output format, but not the semantic phenomenon.
- **P2 / P4 / P5** anchor a stricter, generic entailment task based on guarantee, necessity, or compatibility.
- **P1** anchors the actual CONFER label space by example.

That distinction matters, because it keeps the interpretation focused and conservative. The result is not that the model “needs more instructions” in general. The result is that, for CONFER, the model needs to be shown what **presupposition-sensitive E/N/C** looks like.

---

## 6) What we can say confidently

### Strong claims that are supported

1. **P1 is the best-performing prompt in the current CONFER English sweep.**
2. **Its advantage is large, especially for Opus 4.6.**
3. **The improvement is concentrated most clearly at the Entailment/Neutral boundary, with additional gains for Contradiction in Opus.**
4. **The prompt text suggests that P1 succeeds because it provides compact, benchmark-aligned demonstrations rather than generic NLI heuristics.**

### Claims that should remain cautious

1. We cannot yet say that **few-shot prompting in general** is what helps.
2. We cannot yet say that the effect would be identical on a different presupposition dataset.
3. We cannot yet fully separate “few-shot” from “better task anchoring,” because in P1 those two things come together.

Those cautions do not weaken the central finding. They just keep the write-up honest.

---

## 7) Bottom-line conclusion

The current CONFER English results suggest that **P1 succeeds because it anchors the model to the right semantic task**.

Unlike P0, it does not leave the model to infer the label space from scratch.
Unlike P2, P4, and P5, it does not reframe the task as generic compatibility or guarantee-based inference.
Instead, it gives the model a very small number of **benchmark-shaped demonstrations** that show how presupposition-sensitive Entailment, Neutral, and Contradiction should be recognized.

That appears to be enough to substantially improve performance for Chat 5.4 and to transform performance for Opus 4.6.

The safest overall conclusion is:

> **On CONFER, prompt quality seems to matter less in terms of length or procedural complexity than in terms of whether the prompt teaches the model the benchmark’s presupposition-specific decision boundary. P1 does that better than the alternatives tested so far.**

---

## Source notes

- `srijon-2.0/presuppositions/prompts/p0.md`
- `srijon-2.0/presuppositions/prompts/p1.md`
- `srijon-2.0/presuppositions/prompts/p2.md`
- `srijon-2.0/presuppositions/prompts/p4.md`
- `srijon-2.0/presuppositions/prompts/p5.md`
- `presupposition/README.md`
- CONFER English score dump for Chat 5.4
- CONFER English score dump for Opus 4.6