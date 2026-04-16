= Prompting for NER — Notes
_2026-04-16_

#outline(indent: 1em)

---

== glossary

/ NER (Named Entity Recognition): identifying and classifying spans of text into predefined categories (e.g. person, org, gene, disease). a span is a contiguous sequence of tokens.
/ LLM (Large Language Model): a neural network trained on large text corpora to generate text; e.g. GPT-4, Claude, Llama.
/ fine-tuning: further training a pretrained model on a smaller task-specific dataset to specialize it.
/ zero-shot: prompting without any examples — the model has to rely entirely on what it learned during pretraining.
/ few-shot / in-context learning: including a small number of input-output examples in the prompt so the model can infer the task pattern.
/ distillation (knowledge distillation): training a smaller "student" model to mimic a larger "teacher" model's outputs — transfers capability without copying weights.
/ chain-of-thought (CoT): asking the model to reason step-by-step before producing a final answer.
/ self-consistency: sampling multiple CoT outputs and taking majority vote — a decoding strategy layered on top of CoT, not the same thing as CoT.
/ span: a contiguous stretch of tokens (e.g. "New York City" is a 3-token span).
/ position bias: model performance varies based on where in the input the relevant info appears.
/ prompt sensitivity: small wording changes in the prompt cause large output quality swings.
/ overclassification: model labels too many spans as entities, erring towards inclusion.
/ hallucination: model generates entities or facts not present in the input text.
/ agentic IE: information extraction via multi-step tool-using agents that query, verify, and iterate — not single-pass prompting.
/ retrieval-augmented generation (RAG): augmenting the prompt with relevant passages retrieved from an external corpus at inference time.
/ Vicuna: open-weight instruction-following model fine-tuned from LLaMA; used as student model in distillation experiments here.
/ SOTA: best-known performance on a benchmark at a given point in time.

---

== why NER for our PoC

NER is a good task for demonstrating proof-of-concept for task-specific (TS) prompting:

- well-benchmarked across domains (general, biomedical, clinical)
- strong supervised baselines to compare against
- requires structured output, so the effect of prompting choices is directly observable

---

== baseline models to benchmark against

*PubMedBERT* — best in class for biomedical NER; beats BioBERT because it was pretrained from scratch on PubMed rather than fine-tuned from general BERT. training corpus matters more than architecture.
- #link("https://arxiv.org/html/2508.01630v1")
- #link("https://arxiv.org/html/2305.04928v5")

*BioBERT* — solid baseline, weaker than PubMedBERT for the reason above.

*BioGPT* — generative biomedical model; beats BERT-style on some tasks, COVID benchmarks show this.
- #link("https://arxiv.org/pdf/2210.10341")

PubMedBERT is the ceiling to compare against.

---

== where LLMs underperform fine-tuned models

general LLMs tend to lag fine-tuned specialists on standard NER benchmarks:
- #link("https://arxiv.org/abs/2203.08410") — early evidence

known failure modes:

- *overclassification* — errs toward labeling on edge cases; needs training data to correct
- *span boundary errors* — right entity type, wrong span offsets
  - #link("https://www.semanticscholar.org/reader/97782a67971c4ff1a74bf07e82fe20b2c4bf86c4")
- *hallucination* — invents entities not in the source text
  - #link("https://arxiv.org/abs/2304.10428v2")
- *position bias* — performance degrades based on where in context entities appear
  - #link("https://aclanthology.org/2024.tacl-1.9/")
- *prompt sensitivity* — minor prompt rewording causes big output swings
  - #link("https://openreview.net/forum?id=RIu5lyNXjT")
- *multilingual weakness* — notably worse on non-English NER

---

== where LLMs win

- *unseen domains* — no labeled data, fine-tuning not feasible
- *novel / dynamic label schemas* — entity types not in any training set
- *complex extractions requiring reasoning* — nested entities, implicit references

this is the argument for zero-shot / few-shot prompting: it generalizes where supervised models can't.

---

== prompting techniques

=== text-to-text with special tokens
reformulate NER as generation — model marks entities inline with special tokens (e.g. `[GENE]...[/GENE]`). add a self-verification step to reduce hallucinations.
- #link("https://arxiv.org/abs/2304.10428")

=== chain-of-thought
model reasons step-by-step before producing the entity list. helps on complex or ambiguous spans.
- #link("https://arxiv.org/abs/2305.15444")

layering self-consistency on top (majority vote across multiple CoT samples) lifts performance further:
- #link("https://arxiv.org/abs/2203.11171")

=== dialogue-based decomposition (ChatIE)
two-stage: first identify entity spans, then classify relations. breaks up the prediction complexity.
- #link("https://www.scribd.com/document/888484398/ChatIE-Zero-Shot-Information-Extraction-via-Chatting-With-ChatGPT")

=== code-based extraction
cast NER as Python code generation (e.g. populate a dataclass). code-pretrained models handle structured output better and the result is machine-parseable natively.
- #link("https://www.semanticscholar.org/reader/a86dd6c62d3dc9c7989c98a3e4ace3fd8000e515")

=== in-context learning: label permutation finding
randomly permuting labels in few-shot examples barely hurts performance — models rely on the format more than the label semantics. so getting the prompt format right matters more than perfect label alignment.

---

== distillation

distilling a large LLM into a smaller specialist (e.g. Vicuna-based) substantially beats just prompting the large model directly — and can approach SOTA:

- #link("https://arxiv.org/abs/2305.05003")
- #link("https://pmc.ncbi.nlm.nih.gov/articles/PMC10482322/")
- #link("https://openreview.net/pdf?id=r65xfUb76p") — Vicuna distillation was way better than standard chat baseline

if raw prompting isn't competitive enough, distillation is the next step — not just more prompt tuning.

---

== takeaways

- distillation into specialist models is dominant — prompting alone rarely beats fine-tuned baselines
- structured output infra (special tokens, code-based extraction) is making generative IE more reliable
- agentic + retrieval-augmented IE is the current frontier
- open-weight parity means self-hosted pipelines are now viable

for our PoC: lead with the cases where LLMs win (zero-shot, novel schemas), use structured output to reduce failure modes, and treat distillation as the upgrade path if needed.
