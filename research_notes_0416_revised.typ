= LLMs for Linguistic Annotation — Research Notes
_2026-04-16_

#outline(indent: 1em)

---

== problem statement

challenges we're trying to address:

- *generality:* existing tools are task-specific, often expensive, and may not exist for less-studied phenomena — want to show LLMs can work across multiple tasks without specialized setup
- *training data:* supervised models require labeled data that is rare or costly to produce — want to show prompt engineering alone can match or approach SOTA
- *multilingual:* most tools and evaluations are english-centric — if capacity allows, show LLMs generalize across languages, especially low-resource ones

background / framing:

- #link("https://societaslinguistica.eu/sle2026/wp-content/uploads/sites/9/2025/12/SLE_Large-Language-Models-for-Linguistics_updated.pdf")
- #link("https://link.springer.com/article/10.1007/s10579-025-09839-y")
- #link("https://arxiv.org/abs/2510.12306")
- #link("https://www.refontelearning.com/blog/low-resource-language-models-and-inclusive-ai")

---

== lemmatization (solved, proof of concept)

state of the art: spacy, stanza, udpipe (95-99%)

- #link("https://aclanthology.org/L16-1680/")

LLMs match that, even on out-of-domain data:

- #link("https://aclanthology.org/2025.findings-emnlp.988/")

eval metrics: word-level accuracy, sentence-level accuracy

use as the anchor result — prompting alone works, no training needed.

---

== grammaticality judgments (most promising for prompting)

no dedicated annotation tool exists — BLiMP and CoLA are datasets, not tools.

LLMs > humans (58-60% on gradient judgment tasks):

- #link("https://www.pnas.org/doi/10.1073/pnas.2400917121")
- #link("https://pmc.ncbi.nlm.nih.gov/articles/PMC11388322/")

prompting matters:

- #link("https://aclanthology.org/2025.naacl-long.380/")
- #link("https://arxiv.org/abs/2506.02302")

qualitative breakdown (better on subj-verb agreement and word order violations; worse on island constraints, center embedding, and comparative constructions):

- #link("https://www.englishjournal.net/archives/2025/vol7issue2/PartC/7-2-27-831.pdf")

eval metrics: accuracy (BLiMP), spearman/pearson correlation with gradient judgments, MCC

todo:
- [ ] design prompt variants (zero-shot, few-shot, chain-of-thought) and compare on BLiMP/CoLA
- [ ] test on non-english grammaticality benchmarks if multilingual scope is pursued
- [ ] document which construction types fail — that's the interesting contribution

---

== POS tagging (gap exists, worth pursuing)

state of the art: spacy, udpipe, bert (97-98%)

real-world gap: drops 4-5% out-of-domain, and fixing it requires new labeled training data (rare):

- #link("https://link.springer.com/article/10.1007/s10579-024-09751-x")

LLMs worse (85-90%):

- #link("https://aclanthology.org/2024.propor-1.46.pdf")

argument: even if LLMs don't match SOTA in-domain, they may match or exceed SOTA out-of-domain where SOTA degrades — this is the fairest comparison.

multilingual problems:

- LLMs worse on low-resource languages: #link("https://arxiv.org/html/2404.18286v1")
- UD tagset limited — POS distinctions vary across languages: #link("https://aclanthology.org/2024.acl-long.777/")

eval metrics: token-level accuracy (UPOS), per-tag F1, cross-domain evaluation

todo:
- [ ] run LLM prompting on an out-of-domain test set where SOTA drops
- [ ] test on a low-resource language (e.g. a UD treebank with sparse tooling)
- [ ] compare prompt strategies: tag-by-tag vs. full-sentence annotation

---

== NER (models very specific and good, but not general)

dataset + gold standard: CoNLL (92-95% F1):

- #link("https://arxiv.org/abs/2310.16225")

other datasets: OntoNotes:

- #link("https://www.intechopen.com/journals/1/articles/679")

LLMs worse:

- #link("https://arxiv.org/html/2408.15796v2")
- #link("https://arxiv.org/abs/2304.10428")
- #link("https://arxiv.org/html/2402.09282v3")

training is domain-specific (model trained on news fails on biomedical, social media, etc.) — LLMs as general-purpose NER without domain retraining is the angle:

- #link("https://arxiv.org/abs/2311.08526")
- #link("https://pypi.org/project/gliner/0.2.5/")

real-world problem: gold labels and human annotators disagree — relevant for evaluation

multilingual: underserved:

- #link("https://masterdatascience.ubc.ca/why-data-science/data-stories/seasaltai")

eval metrics: F1, strict vs. relaxed span match (need to decide and document)

todo:
- [ ] pick 2 domains (e.g. news + biomedical) to show cross-domain generality
- [ ] decide strict vs. relaxed match and document rationale
- [ ] consider per-entity-type F1 breakdown

---

== presupposition (basically nothing — risky)

literature is super sparse (~20 papers)

fine-tuned BERT, ~80% on test set:

- #link("https://aclanthology.org/2021.conll-1.28/")

benchmarks: IMPPRES, NOPE, commitment bank, ConFer, PUB — a lot of diversity in trigger types:

- #link("https://github.com/facebookresearch/Imppres")
- #link("https://arxiv.org/html/2506.06133")
- #link("https://arxiv.org/html/2401.07078v1")

LLMs ok but biased — more false positives, bad at conditionals:

- #link("https://aclanthology.org/2025.findings-acl.107.pdf")
- #link("https://arxiv.org/html/2505.22354")

eval metrics: macro F1, spearman correlation, accuracy (NLI framing)

todo:
- [ ] only pursue if another task is dropped — sparse literature makes positioning harder
- [ ] if pursued: use IMPPRES as benchmark, frame as LLMs without fine-tuning vs. fine-tuned BERT
- [ ] focus on trigger-type breakdown — that's where the failure modes are

---

== coreference (very specific, requires training — deprioritize)

gold standard: maverick (83.6 F1), corpipe:

- #link("https://aclanthology.org/2024.acl-long.722.pdf")
- #link("https://arxiv.org/pdf/2404.00727")
- #link("https://aclanthology.org/2025.crac-1.11/")

the rest (spacy, etc.) is bad

LLMs worse than supervised:

- #link("https://arxiv.org/abs/2305.14489")

true for multilingual:

- #link("https://aclanthology.org/2025.crac-1.9.pdf")

training helps, but that's the whole problem:

- #link("https://arxiv.org/html/2509.17505v1")

eval metrics: MUC, B-cubed, CEAF
