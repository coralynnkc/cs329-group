# CONFER (English): explaining P1's unusually strong performance

## Executive summary

Across the current CONFER English prompt sweep, **P1 is the strongest prompt overall**. It is the best-performing prompt for **Chat 5.4** and **Opus 4.6**, and it is also the only prompt that is clearly strong **across both models**.

That matters because the size of the P1 jump is larger than most prompt effects we have seen elsewhere in this project. At the same time, the safest interpretation is **not** simply "few-shot works." A narrower and better-supported claim is this:

> **P1 appears to work because it teaches the model the benchmark's presupposition-sensitive label boundary more effectively than the alternative prompts.**

In particular, P1 seems to do three things at once:

1. It keeps the operational setup simple.
2. It gives the model **one example of each label**.
3. It teaches the task by **benchmark-shaped examples** rather than by abstract, generic NLI rules.

This is an important distinction. Some of the other prompts are not weak because they are vague. In fact, several are quite explicit. The problem is that many of them appear to anchor the task as **generic semantic inference** rather than **presupposition-sensitive inference**. P1 seems to avoid that mistake.

A second important result is that the new **hard-label prompts** are not strong. The especially notable case is **P9**, the no-probability counterpart to P1. Its weak performance suggests that probability output may not be a superficial formatting choice. At least for Opus, it may be part of what makes P1 work so well.

## Scope and caution

This document is meant to explain the current results carefully, not to overclaim.

Two cautions matter:

- These results strongly suggest that **P1 is doing something importantly right**.
- They do **not** yet prove which single ingredient is responsible.

P1 differs from the weaker prompts in more than one way. It differs in examples, in how it anchors the label space, and in the fact that it asks for probabilities rather than a single hard label. So the safest conclusion is that **P1 is the best-tested prompt so far, and its advantage is most plausibly due to better task anchoring, with possible additional benefit from probability elicitation**.

`p1_redux` is intentionally excluded from this write-up.

---

## 1) Current results overview

### Table 1. Chat 5.4 on CONFER English (probability prompts only)

| Prompt | Accuracy | Macro-F1 | Log Loss | Brier Score | F1-E | F1-N | F1-C | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **P1** | **0.7867** | **0.7841** | **0.6815** | **0.3686** | **0.8722** | **0.6923** | **0.7879** | Best overall |
| P2 | 0.7100 | 0.7094 | 0.8589 | 0.4917 | 0.7845 | 0.5700 | 0.7738 | Best non-few-shot Chat prompt |
| P0 | 0.6933 | 0.6828 | 0.9081 | 0.5244 | 0.7857 | 0.4889 | 0.7738 | Minimal baseline |
| P4 | 0.4767 | 0.4644 | 1.6368 | 0.9029 | 0.4106 | 0.5094 | 0.4733 | Strong Neutral bias |
| P5 | 0.4700 | 0.4563 | 1.5819 | 0.8962 | 0.3893 | 0.5062 | 0.4733 | Similar to P4 |
| P6 | 0.4700 | 0.4563 | 1.5028 | 0.8689 | 0.3893 | 0.5062 | 0.4733 | Revised results; low-performing but structurally normal |
| P7 | 0.4567 | 0.4042 | 1.8956 | 0.9854 | 0.6875 | 0.0355 | 0.4895 | Presupposition-specific wording alone did not help |

### Table 2. Opus 4.6 on CONFER English

| Prompt | Output type | Accuracy | Macro-F1 | Log Loss | Brier Score | F1-E | F1-N | F1-C | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| **P1** | Probabilities | **0.9200** | **0.9192** | **0.3649** | **0.1618** | **0.8959** | **0.8667** | **0.9950** | Best overall |
| P4 | Probabilities | 0.8633 | 0.8626 | 0.5004 | 0.2483 | **0.9688** | 0.8313 | 0.7879 | Strong rule-based alternative |
| P2 | Probabilities | 0.6833 | 0.6601 | 0.8197 | 0.5040 | 0.8750 | 0.6801 | 0.4252 | Over-neutralizes contradiction |
| P0 | Probabilities | 0.6033 | 0.5700 | 1.0121 | 0.6163 | 0.7046 | 0.2222 | 0.7831 | Minimal baseline |
| P9 | Hard label | 0.4700 | 0.4563 | — | — | 0.3893 | 0.5062 | 0.4733 | P1-style few-shot, no probabilities |
| P8 | Hard label | 0.3467 | 0.1888 | — | — | 0.0588 | 0.5075 | 0.0000 | Projection-aware, no probabilities |

**Note:** P8 and P9 were scored manually as hard-label runs, so probability-based metrics such as log loss and Brier score are not available for them.

### Table 3. P1 gain over selected alternatives

| Model | Comparison | Δ Accuracy | Δ Macro-F1 | Δ F1-E | Δ F1-N | Δ F1-C |
|---|---|---:|---:|---:|---:|---:|
| Chat 5.4 | P1 vs P0 | +0.0934 | +0.1013 | +0.0865 | +0.2034 | +0.0141 |
| Chat 5.4 | P1 vs P2 | +0.0767 | +0.0747 | +0.0877 | +0.1223 | +0.0141 |
| Chat 5.4 | P1 vs P7 | +0.3300 | +0.3799 | +0.1847 | +0.6568 | +0.2984 |
| Opus 4.6 | P1 vs P0 | +0.3167 | +0.3492 | +0.1913 | +0.6445 | +0.2119 |
| Opus 4.6 | P1 vs P4 | +0.0567 | +0.0566 | -0.0729 | +0.0354 | +0.2071 |
| Opus 4.6 | P1 vs P9 | +0.4500 | +0.4629 | +0.5066 | +0.3605 | +0.5217 |

Two immediate points follow from these tables:

- **P1 is not just the best prompt on one model. It is the best prompt across both models.**
- The biggest repeated gain is at the **Entailment/Neutral boundary**, though for Opus P1 also produces a very large gain on **Contradiction**.

---

## 2) Prompt families and what each one is trying to do

### Table 4. Prompt design map

| Prompt | Output | Few-shot? | Presupposition-specific framing? | Core decision style | Working interpretation |
|---|---|---|---|---|---|
| P0 | Probabilities | No | No | Minimal batch prompt | Lets the model infer the task from priors |
| **P1** | Probabilities | **Yes: 1 E, 1 N, 1 C** | Implicitly, by example | Example-based anchoring | Teaches the label geometry directly |
| P2 | Probabilities | No | No | Guarantee true / guarantee false / else N | Generic necessity-based NLI |
| P4 | Probabilities | No | No | Definitely true / definitely false / else N | Stricter rule-based NLI |
| P5 | Probabilities | No | No | Compatibility, then determination | Generic compatibility-based NLI |
| P6 | Probabilities | No | No | Independent E / C / N tests | Another rule-heavy NLI framing |
| P7 | Probabilities | No | **Yes** | Explicit projection-aware definitions | Presupposition-specific wording without examples |
| P8 | Hard label | No | **Yes** | Projection-aware hard-label prompt | Hard-label counterpart to P7 |
| P9 | Hard label | **Yes: 1 E, 1 N, 1 C** | Implicitly, by example | P1-style few-shot, but no probabilities | Hard-label counterpart to P1 |

This table helps clarify an important point: **P1 is not the only prompt that tries to help the model.** Some other prompts are quite elaborate. The issue is not whether they add instructions. The issue is **what kind of task they teach**.

---

## 3) Why P1 is so much stronger

### 3.1 P1 teaches the benchmark's label space by example

P1 does something deceptively simple: it gives the model **one example each of E, N, and C** before asking it to score the dataset. That seems to matter a great deal.

The key is not just that there are examples. It is that the examples are **benchmark-shaped**. They are not generic textbook entailment pairs. They are close to the kind of presupposition-sensitive reasoning that CONFER is testing.

That gives P1 a practical advantage over both extremes:

- over **P0**, which leaves the model to infer the task almost entirely from its own priors, and
- over **P2/P4/P5/P6**, which try to impose explicit reasoning pipelines that are more natural for generic NLI than for presupposition projection.

P1 does not lecture the model about semantics. It simply shows the model what counts as E, N, and C **on this benchmark**.

### 3.2 P1 appears to anchor the right task, not just any task

A useful way to frame the result is:

> The weak prompts are not necessarily unanchored. Many of them are **mis-anchored**.

This seems especially true of P2, P4, P5, and P6. All of them define the problem in terms like:

- must the hypothesis be true,
- definitely true / definitely false,
- compatible or not compatible,
- guaranteed or not guaranteed.

Those are sensible concepts for **standard sentence-pair inference**. But CONFER is probing **presupposition triggers** and **projection behavior**, where the relevant information is often not asserted in the simplest surface way. A prompt that pushes the model to behave like a strict theorem prover may therefore be teaching the wrong boundary.

P1 seems to avoid this. It does not try to replace the model's semantic reasoning with a rigid procedure. Instead, it gives the model three demonstrations that implicitly show what the benchmark designers mean by E, N, and C.

### 3.3 The clearest repeated gain is at the E/N boundary

For Chat 5.4, the biggest P1 gain over P0 is **F1-N: +0.2034**.

For Opus 4.6, the biggest P1 gain over P0 is again **F1-N: +0.6445**.

That is a strong signal. It suggests that P1 is especially good at teaching the model where **Neutral actually lives** on CONFER.

This is exactly where a presupposition benchmark can confuse a generic inference prompt. A model can easily over-read projected content as Entailment, or under-read it as Neutral, depending on how the task is framed. P1 seems to reduce both kinds of mistake better than the alternatives.

### 3.4 P1 is better than explicit presupposition wording alone

One of the most important newer results is **P7**.

P7 was designed to be presupposition-specific. It explicitly defines the labels in terms of triggering, preserving, or canceling presuppositions, and it warns that presuppositions can project through negation, questions, and belief/report contexts. On paper, that should have been a strong fit for CONFER.

But on Chat 5.4, P7 performs badly: **0.4567 accuracy** and **0.4042 macro-F1**.

That matters because it rules out a too-simple explanation. P1 is **not** strong merely because it somehow mentions the right topic. In fact, P1 does not explicitly define presupposition at all. Instead, it **shows** the model the correct boundary by example.

So the evidence currently points to this stronger claim:

> **Examples seem to help more than abstract semantic definitions.**

That is a more interesting and more precise finding than simply saying that task-specific wording helps.

### 3.5 P1 is strong without being over-engineered

P1 is not long. It does not have a multi-stage reasoning procedure. It does not ask the model to answer multiple meta-questions before labeling. It does not require explicit verification steps.

This is important because it suggests that the gain is **not** coming from prompt length or complexity. If anything, the current results point the other way:

- **P0** is too sparse.
- **P2/P4/P5/P6/P7** are more explicit, but that explicitness does not reliably help.
- **P1** hits a useful middle ground: enough structure to teach the task, but not so much structure that it teaches the wrong task.

In that sense, P1 may be strong partly because it is **light-touch but highly diagnostic**.

---

## 4) Model-by-model interpretation

### 4.1 Chat 5.4

For Chat 5.4, P1 is clearly best. P2 is the next best probability prompt, but it still trails P1 by **0.0767 accuracy** and **0.0747 macro-F1**.

This is useful because it shows that P1 is not only beating obviously weak prompts. It is also beating the best of the more formal rule-based prompts.

At the same time, the Chat results also show that **not every alternative is equally bad**:

- P0 is respectable, but weaker on Neutral.
- P2 is decent, but still not as good as P1.
- P4, P5, P6, and P7 all fall off sharply.

So for Chat 5.4, the current story is not that only one prompt works at all. It is that **P1 works best by a real margin, and the weaker prompts seem to fail for different reasons**.

### 4.2 Opus 4.6

For Opus 4.6, the story is even more striking.

P1 is best by a large margin over P0 and P2, and still clearly ahead of P4. But unlike Chat, Opus also performs well on **P4**. That is important because it shows that Opus is not simply allergic to rule-based prompting. It can handle it.

Still, P1 remains best overall, and its advantage over P4 is highly informative:

- P4 actually has the better **F1-E**.
- But P1 is better on **F1-N** and much better on **F1-C**.

That suggests that P4 is a strong prompt for high-confidence entailment-style reasoning, while P1 is better at preserving the **full three-way label balance**, especially contradiction.

This is one reason P1 looks more attractive as a general-use prompt: it is the most robust across both models and across all three labels.

---

## 5) Revised interpretation of P6

An earlier version of this write-up described P6 as incomplete or structurally problematic because the original score dump included missing items, duplicates, and other output mismatches.

That is **no longer the right interpretation** for the updated data.

In the revised Chat 5.4 results, P6 now has full matched coverage and can be treated as a normal prompt run. Its performance is still poor, but the issue is now performance, not output integrity.

In fact, the revised P6 looks very similar to P5 on the core metrics:

- P5: **0.4700 accuracy / 0.4563 macro-F1**
- P6: **0.4700 accuracy / 0.4563 macro-F1**

So the clean updated reading is:

> **P6 is not a broken prompt in the revised results. It is simply another low-performing rule-heavy prompt.**

That is important for keeping the analysis honest. It also strengthens the overall argument, because it means the pattern is not being driven by one anomalous failed run.

---

## 6) Why P9 matters so much

P9 is one of the most interesting additions to the experiment.

P9 is the hard-label, no-probability counterpart to the P1-style few-shot prompt. If it truly differs from P1 only in the output format, then it gives the cleanest current test of whether **probability elicitation** is doing real work.

The result is dramatic for Opus 4.6:

- **P1:** 0.9200 accuracy / 0.9192 macro-F1
- **P9:** 0.4700 accuracy / 0.4563 macro-F1

That is a collapse of:

- **-0.4500 accuracy**
- **-0.4629 macro-F1**

The class-level drops are also large:

- **F1-E:** 0.8959 -> 0.3893
- **F1-N:** 0.8667 -> 0.5062
- **F1-C:** 0.9950 -> 0.4733

This does not prove that probabilities are always better. But it does strongly suggest that, at least for Opus on CONFER, the probability request is **not cosmetic**.

### Table 5. Hard-label ablation on Opus 4.6

| Family | Probability version | Accuracy | Macro-F1 | Hard-label version | Accuracy | Macro-F1 |
|---|---|---:|---:|---|---:|---:|
| Few-shot | P1 | 0.9200 | 0.9192 | P9 | 0.4700 | 0.4563 |
| Projection-aware | P7 | 0.4567* | 0.4042* | P8 | 0.3467 | 0.1888 |

\*P7 was run on Chat 5.4, not Opus 4.6, so this row is only a directional comparison of prompt family behavior, not a within-model ablation.

The P8 result points in the same direction. The projection-aware hard-label prompt is also weak. So the pattern is at least suggestive:

- explicit presupposition instructions alone do not seem sufficient,
- and removing probabilities from these prompts does not help.

The most careful current interpretation is:

> **P1's success may come from a combination of good example-based task anchoring and the probability-output format.**

That is especially worth noting because this was one of the original questions behind the experiment.

### Table 6. Manual split accuracies for hard-label Opus prompts

| Prompt | S1 Acc | S2 Acc | S3 Acc | Mean Acc | Macro-F1 |
|---|---:|---:|---:|---:|---:|
| P8 | 0.3600 | 0.3500 | 0.3300 | 0.3467 | 0.1888 |
| P9 | 0.4500 | 0.4800 | 0.4800 | 0.4700 | 0.4563 |

P9 is therefore interesting not because it is good, but because it is **bad in a very informative way**. A hard-label mirror of the best-performing prompt does not preserve that performance. That strongly suggests that P1's success cannot be reduced to "same prompt, but shorter output." The probability request appears to matter.

---

## 7) What we can say confidently

### Strong claims that are supported

1. **P1 is the strongest prompt tested so far on CONFER English.**
2. **P1 is the only prompt that is clearly strong across both Chat 5.4 and Opus 4.6.**
3. **Its gains are especially clear at the Entailment/Neutral boundary, with additional major gains for Contradiction on Opus.**
4. **P1 seems to outperform the alternatives because it teaches the benchmark's label geometry by example rather than by abstract NLI rules.**
5. **The hard-label result for P9 suggests that probability elicitation may be an important part of P1's effectiveness.**

### Claims that should remain cautious

1. We cannot yet say that **few-shot prompting in general** is the reason.
2. We cannot yet say that **probability output alone** explains the entire effect.
3. We cannot yet assume the same pattern will hold on every presupposition dataset.
4. We should not describe P6 as unreliable or malformed in the revised results.
5. We should not say that P1 is literally the **only** successful prompt, because **P4 is also strong on Opus**.

Those cautions do not undermine the main result. They simply keep the analysis precise.

---

## 8) Bottom-line conclusion

The most defensible conclusion from the current CONFER English results is this:

> **P1 is powerful because it teaches the model the right task in the right way.**

It does not leave the model to guess the label space from scratch, like P0.
It does not overconstrain the task with generic compatibility or guarantee-based NLI rules, like P2, P4, P5, and P6.
It does not rely only on abstract presupposition definitions, like P7.

Instead, it gives the model a compact, benchmark-aligned demonstration of what **Entailment**, **Neutral**, and **Contradiction** look like for this dataset.

That appears to be enough to produce the strongest overall performance on both Chat 5.4 and Opus 4.6.

The new P9 result makes the story even more interesting. A hard-label mirror of P1 does **not** retain P1's strength. So the best current explanation is not just "few-shot helps." It is something narrower and more informative:

> **P1 likely benefits from a combination of benchmark-shaped example anchoring and probability elicitation.**

That is a stronger and more publication-worthy finding than a generic claim about prompt engineering.

---

## Source notes

This summary is based on:

- the current CONFER English score dumps for Chat 5.4 and Opus 4.6,
- the current prompt files in `srijon-2.0/presuppositions/prompts`,
- the earlier `presupposition/README.md` framing of CoNFER as a presupposition-projection task,
- and the manually calculated hard-label metrics provided for P8 and P9.
