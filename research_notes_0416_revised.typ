= Research Notes — LLMs for Linguistic Annotation
_Revised 2026-04-16_

== Problem Statement

Traditional NLP annotation tools have three core limitations we aim to address:

+ *Generality:* Existing tools are task-specific, often expensive, and may not exist for less-studied phenomena. We want to show LLMs can serve as a general-purpose annotation engine (proof of concept across multiple tasks).
+ *Training data dependency:* Supervised models require labeled data that is rare or costly to produce. We aim to show prompt engineering alone can match or approach SOTA, *obviating the need for fine-tuning*.
+ *Monolinguality:* Most tools and evaluations are English-centric. If capacity allows, we demonstrate LLMs can generalize across languages — especially low-resource ones.

---

== Task Overview & Priority

#table(
  columns: (auto, auto, auto, auto),
  [*Task*], [*LLM vs SOTA*], [*Prompting Angle*], [*Priority*],
  [Lemmatization], [Matches SOTA], [Proven], [Done — PoC],
  [Grammaticality], [LLMs > humans], [Most promising], [High],
  [POS Tagging], [85–90% vs 97–98%], [Out-of-domain gap], [High],
  [NER], [Worse, domain-specific], [Generality gap], [Medium],
  [Presupposition], [OK but biased], [Sparse literature], [Low / risky],
  [Coreference], [Worse, needs training], [Against our approach], [Deprioritize],
)

---

== Lemmatization ✓ (Proof of Concept — Done)

*SOTA:* spaCy, Stanza, UDPipe — 95–99% word-level accuracy.
- Benchmark: #link("https://aclanthology.org/L16-1680/")[ACL Anthology L16-1680]

*LLM result:* Matches SOTA, even on out-of-domain data.
- Evidence: #link("https://aclanthology.org/2025.findings-emnlp.988/")[EMNLP 2025 Findings]

*Eval metrics:* Word-level accuracy, sentence-level accuracy.

*Status:* Completed. Use as the paper's "existence proof" that prompting alone works — no training needed.

---

== Grammaticality Judgments ⭐ (Most Promising)

*Why this task fits our goals:*
- No dedicated annotation tool exists (BLiMP and CoLA are *datasets*, not tools).
- LLMs already outperform humans (58–60% on gradient judgment tasks).
- Prompting is known to matter — prompt design measurably changes outcomes.
- Qualitative variation is interesting: LLMs are *better* on subject-verb agreement and word order violations, *worse* on island constraints, center embedding, and comparative constructions.

*SOTA / human baseline:*
- LLMs beat humans: #link("https://www.pnas.org/doi/10.1073/pnas.2400917121")[PNAS 2024], #link("https://pmc.ncbi.nlm.nih.gov/articles/PMC11388322/")[PMC]
- Qualitative breakdown: #link("https://www.englishjournal.net/archives/2025/vol7issue2/PartC/7-2-27-831.pdf")[English Journal 2025]

*Prompting literature:*
- #link("https://aclanthology.org/2025.naacl-long.380/")[NAACL 2025], #link("https://arxiv.org/abs/2506.02302")[arXiv 2506.02302]

*Eval metrics:* Accuracy (BLiMP), Spearman/Pearson correlation with gradient judgments, MCC.

*Actionable next steps:*
- [ ] Design prompt variants (zero-shot, few-shot, chain-of-thought) and compare on BLiMP/CoLA.
- [ ] Test on non-English grammaticality benchmarks if multilingual scope is pursued.
- [ ] Document which construction types LLMs fail on — good paper contribution.
- [ ] Treat this as the centerpiece task: it's the one where prompting matters most and no prior tool exists.

---

== POS Tagging (Clear Gap Worth Closing)

*SOTA:* spaCy, UDPipe, BERT — 97–98% token-level UPOS accuracy.

*Real-world gap:* Out-of-domain performance drops 4–5%, and recovery requires new labeled training data (which is rare).
- Evidence: #link("https://link.springer.com/article/10.1007/s10579-024-09751-x")[LREV 2024]

*LLM baseline:* 85–90% — worse than SOTA, but the gap is the story.
- Evidence: #link("https://aclanthology.org/2024.propor-1.46.pdf")[PROPOR 2024]

*Multilingual issues:*
- LLMs worse on low-resource languages: #link("https://arxiv.org/html/2404.18286v1")[arXiv 2404.18286]
- UD tagset limited — POS distinctions vary across languages: #link("https://aclanthology.org/2024.acl-long.777/")[ACL 2024]

*Eval metrics:* Token-level UPOS accuracy, per-tag F1, cross-domain evaluation.

*Actionable next steps:*
- [ ] Run LLM prompting on an out-of-domain test set where SOTA drops — this is the fairest comparison.
- [ ] Test on a low-resource language (e.g., a UD treebank with sparse tooling) to hit the multilingual goal.
- [ ] Compare prompt strategies: tag-by-tag vs. full-sentence annotation.
- [ ] Argument to make: even if LLMs don't match SOTA in-domain, they may *match or exceed* SOTA out-of-domain where SOTA degrades.

---

== NER (Generality Problem is the Hook)

*SOTA:* CoNLL benchmark — 92–95% F1.
- #link("https://arxiv.org/abs/2310.16225")[arXiv 2310.16225], OntoNotes: #link("https://www.intechopen.com/journals/1/articles/679")[IntechOpen]

*LLM performance:* Worse than SOTA.
- #link("https://arxiv.org/html/2408.15796v2")[arXiv 2408.15796], #link("https://arxiv.org/abs/2304.10428")[arXiv 2304.10428], #link("https://arxiv.org/html/2402.09282v3")[arXiv 2402.09282]

*Key problem:* NER tools are domain-specific — a model trained on news fails on biomedical text, social media, etc. Our angle: LLMs as *general-purpose* NER without domain-specific training.
- Domain-specificity evidence: #link("https://arxiv.org/abs/2311.08526")[arXiv 2311.08526], #link("https://pypi.org/project/gliner/0.2.5/")[GLiNER]

*Annotation quality problem:* Even gold labels have human annotator disagreement — relevant for any evaluation we do.

*Multilingual:* Underserved.
- #link("https://masterdatascience.ubc.ca/why-data-science/data-stories/seasaltai")[SeasaltAI case study]

*Eval metrics:* F1, strict vs. relaxed span match (decision needed).

*Actionable next steps:*
- [ ] Pick 2 domains (e.g., news + biomedical or social media) to show cross-domain LLM generality.
- [ ] Decide: strict or relaxed match — document the choice and rationale.
- [ ] Consider entity-type F1 breakdown (not just aggregate) to show where LLMs succeed/fail.
- [ ] If time allows, test on non-English data to hit multilingual angle.

---

== Presupposition (High Risk — Proceed with Caution)

*Why it's interesting:* No dedicated tool; pure linguistics phenomenon.

*Literature:* Very sparse — ~20 papers.

*Current best:* Fine-tuned BERT, ~80% on test set.
- #link("https://aclanthology.org/2021.conll-1.28/")[CoNLL 2021]

*Benchmarks:* IMPPRES, NOPE, Commitment Bank, ConFer, PUB.
- Diversity in trigger types is a challenge: #link("https://github.com/facebookresearch/Imppres")[IMPPRES], #link("https://arxiv.org/html/2506.06133")[arXiv 2506.06133], #link("https://arxiv.org/html/2401.07078v1")[arXiv 2401.07078]

*LLM performance:* Functional but biased — more false positives, poor at conditionals.
- #link("https://aclanthology.org/2025.findings-acl.107.pdf")[ACL Findings 2025], #link("https://arxiv.org/html/2505.22354")[arXiv 2505.22354]

*Eval metrics:* Macro F1, Spearman correlation, accuracy (NLI framing).

*Actionable next steps:*
- [ ] Only pursue if another task is dropped. Sparse literature = harder to position contribution.
- [ ] If pursued: use IMPPRES as benchmark; frame as "LLMs without fine-tuning vs. fine-tuned BERT."
- [ ] Focus on trigger-type breakdown — that's where the interesting failure modes live.

---

== Coreference Resolution (Deprioritize)

*Why it doesn't fit:* Best systems (Maverick, CorPipe) require training. LLMs are worse than supervised models. This directly contradicts our "no training data" goal.

*SOTA:* Maverick — 83.6 F1; CorPipe.
- #link("https://aclanthology.org/2024.acl-long.722.pdf")[ACL 2024], #link("https://arxiv.org/pdf/2404.00727")[arXiv 2404.00727], #link("https://aclanthology.org/2025.crac-1.11/")[CRAC 2025]

*LLM status:* Worse than supervised; multilingual also lagging; training helps but defeats our purpose.
- #link("https://arxiv.org/abs/2305.14489")[arXiv 2305.14489], #link("https://aclanthology.org/2025.crac-1.9.pdf")[CRAC 2025 multilingual], #link("https://arxiv.org/html/2509.17505v1")[arXiv 2509.17505]

*Eval metrics:* MUC, B-Cubed, CEAF.

*Recommendation:* Drop unless the project scope expands significantly. The task fundamentally requires training data to be competitive.

---

== Background / Framing Articles

- General LLM-for-linguistics overview: #link("https://societaslinguistica.eu/sle2026/wp-content/uploads/sites/9/2025/12/SLE_Large-Language-Models-for-Linguistics_updated.pdf")[SLE 2026]
- Recent survey: #link("https://link.springer.com/article/10.1007/s10579-025-09839-y")[LREV 2025]
- Prompt-based NLP: #link("https://arxiv.org/abs/2510.12306")[arXiv 2510.12306]
- Low-resource language models: #link("https://www.refontelearning.com/blog/low-resource-language-models-and-inclusive-ai")[Refonte Learning]
