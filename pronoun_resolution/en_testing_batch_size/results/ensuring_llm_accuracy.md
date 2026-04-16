# Ensuring LLM Accuracy in Batch Annotation

## Generalized Prompt Pattern

A reusable prompt pattern for long-form or batch LLM tasks should emphasize not only answer quality, but also structural consistency. The goal is to make it explicit that faithful alignment between inputs and outputs is part of the task itself.

```text
Solve each input independently and maintain exact structural alignment between each input and its output.

Do not use shortcuts, answer patterns, or low-effort completion strategies.
Do not continue if you can no longer maintain the same quality across the remaining items.
If you lose alignment, begin guessing, rely on patterns, skip inputs, merge outputs, repeat outputs, or cannot preserve the required structure, stop immediately and output:

STOP_QUALITY

Faithful processing is more important than full completion.

## Key takeaway

A central finding from this batch-size experiment is that LLM failure is not always transparent. In several degraded runs, the model did not explicitly refuse the task or stop when quality dropped. Instead, it continued producing plausible-looking outputs while silently failing in more subtle ways, including hallucinated `item_id`s, incomplete coverage, and patterned answering such as alternating `A B A B`. In real-world annotation settings, this behavior is unacceptable: a useful system must either continue performing the task faithfully or stop clearly when it can no longer maintain quality.

This leads to an important methodological conclusion: prompt wording alone is not enough to guarantee trustworthy behavior. The model cannot be assumed to honestly disclose when it is guessing, shortcutting, or no longer solving each item independently. As a result, reliable use of LLMs for bulk annotation should be designed as a monitored workflow with external validation, rather than as a single-shot prompt that depends on the model to self-report failure.

## Why accuracy alone is not enough

Because pronoun resolution is a binary task, a model that guesses can still obtain non-trivial accuracy by chance. That means accuracy on its own can hide serious reliability problems. A run may look superficially acceptable while still failing to complete the dataset correctly or preserve the mapping between examples and outputs.

For this reason, the evaluation should include additional metrics alongside accuracy:

- **Coverage**: whether the model returned a usable prediction for each gold item.
- **Missing rate**: how much of the gold dataset received no aligned answer.
- **Extra or hallucinated IDs**: whether the model invented row identifiers not present in the input.
- **Duplicate IDs**: whether the model repeated rows instead of maintaining one answer per item.

These metrics provide clarity about whether the model is acting as a dependable structured annotator rather than simply producing plausible-looking labels.

## What hallucinated IDs mean

Hallucinated or corrupted `item_id`s do **not necessarily prove** that the model is only guessing on the sentence-level task. The model may still be attempting to solve some examples locally. However, hallucinated IDs do show that the model has lost track of the batch procedure and can no longer be trusted to align answers with the correct items.

This distinction matters. There are two separate kinds of failure in a batch annotation workflow:

1. **Sentence-level failure**: the model sees the example and chooses the wrong answer.
2. **Execution-level failure**: the model no longer reliably tracks rows, preserves IDs, or completes the output faithfully.

Our setup makes this difference visible. By measuring coverage, missing rows, and hallucinated IDs in addition to accuracy, we can distinguish between a model that is simply getting examples wrong and a model that is failing as a structured-output system.

## Practical implication for deployment

The important question for real-world use is not only whether an LLM can solve individual examples, but whether it can be trusted to either:

- maintain quality across a long structured task, or
- stop and signal failure when it can no longer continue reliably.

Our results suggest that current models may fail this second requirement. In several runs, the model did not explicitly refuse. Instead, it continued producing output while quality had already broken down. This means a refusal metric by itself is not enough. Some failure modes are effectively **silent**.

Accordingly, trustworthy deployment should not depend on self-reported honesty from the model. It should depend on external checks.

## Recommended workflow for ensuring LLM accuracy

### 1. Use smaller audited batches

Avoid very large one-shot jobs when possible. Break the task into smaller chunks, such as 25, 50, or 100 items, and evaluate each chunk independently.

This reduces the chance of:
- output drift,
- ID hallucination,
- silent truncation,
- and late-stage shortcutting.

It also allows the pipeline to stop early if quality drops.

### 2. Add explicit stop conditions in the prompt

Prompt the model not only to solve the task, but also to halt if it can no longer continue faithfully. For example:

> Do not guess or use answer patterns to complete the batch. If you cannot continue item-by-item with the same quality, stop immediately and output `STOP_QUALITY` instead of continuing.

Also require:

> Do not invent, alter, omit, or reorder `item_id`s. If you lose track of alignment or cannot verify row integrity, output `STOP_QUALITY`.

This will not fully solve the problem, but it gives the model a clear failure mode and makes monitoring easier.

### 3. Treat structure as a first-class quality requirement

A run should not be considered valid merely because some subset of labels is accurate. It must also satisfy structural integrity:

- exactly one output row per input item,
- no missing gold IDs,
- no extra IDs,
- no duplicate IDs,
- no malformed rows.

If these conditions fail, the run should be marked structurally unreliable.

### 4. Add pattern-detection checks

Binary tasks are especially vulnerable to hidden shortcutting because a model can guess and still achieve moderate-looking accuracy. For that reason, workflows should include detectors for suspicious answer behavior, such as:

- long alternating sequences like `A B A B A B`,
- very long same-label streaks,
- unnatural regular switching patterns,
- extreme label imbalance.

These checks can help identify cases where the model is no longer solving each sentence independently.

### 5. Use audit or sentinel items

Insert a small number of known control items into each batch. These may include:

- easy cases,
- repeated items,
- paraphrased duplicates,
- adversarial controls.

If the model becomes inconsistent on repeats or fails obvious controls, that is a strong indicator of degraded attention or shortcutting.

### 6. Use progressive release instead of full one-shot generation

Rather than asking the model to label hundreds of rows at once, run the workflow in stages:

1. label one chunk,
2. validate coverage and structure,
3. check for suspicious patterns,
4. continue only if the batch passes.

This turns the system into a monitored pipeline rather than an all-or-nothing prompt.

### 7. Consider lightweight redundancy

For especially important annotation jobs, re-run a small random subset in a fresh context or with a second model. Agreement on this audit subset can provide a basic check on whether the original run was stable or bluffing.

## Suggested prompt template

Below is a prompt pattern that can reduce shortcutting, though it should always be paired with external checks:

```text
You are labeling a structured dataset. Accuracy and row integrity are equally important.

Rules:
1. Solve each item independently. Do not use answer patterns, shortcuts, or guesses based on position.
2. Return exactly one row for each provided item_id.
3. Do not invent, alter, omit, or reorder item_ids.
4. If you cannot maintain item-by-item quality or lose track of alignment, stop immediately and output STOP_QUALITY instead of continuing.
5. Do not continue with partial completion once quality has degraded.

Output format:
item_id,answer,confidence

Allowed answers: A, B, REFUSE
Allowed confidence values: high, medium, low

If you cannot continue faithfully, output only:
STOP_QUALITY
```

## Paper-ready conclusion

A key practical finding is that the model did not reliably signal when it had stopped performing the task faithfully. In several degraded runs, it neither issued an explicit refusal nor halted cleanly; instead, it continued producing plausible-looking but structurally unreliable outputs, including hallucinated item IDs and patterned responses. This suggests that prompting alone is insufficient to guarantee that an LLM will disclose when it is shortcutting or no longer maintaining quality.

Accordingly, a safe annotation workflow should not depend on self-reported refusal. Instead, it should combine explicit stop instructions with external validation mechanisms such as chunked batching, structural checks on row coverage and ID integrity, pattern detection for suspicious answer sequences, and audit subsets with repeated or control items. In this framework, trust is established not by the model’s willingness to admit failure, but by automated checks that detect when the output no longer satisfies the requirements of faithful batch annotation.

For real-world deployment, the relevant question is not only whether an LLM can solve individual examples, but whether it can be trusted to either maintain quality across a long structured task or stop when it cannot. Our results suggest that current models may fail this second requirement unless the workflow includes external safeguards. As a result, reliable use of LLMs for bulk annotation should be designed as a monitored pipeline rather than a single-shot prompt.
