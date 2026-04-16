= overall

challenges:

- generality = computational complexity, tools are for a specific purpose and can be expensive or difficult to use or not exist
- task alignment (what linguists want and what pipelines exist)
- lack of training data (need a way to circumvent training models via prompting)
- multilingual! https://www.refontelearning.com/blog/low-resource-language-models-and-inclusive-ai

some articles + attempts ab ts:

- https://link.springer.com/article/10.1007/s10579-025-09839-y
- https://arxiv.org/abs/2510.12306
- https://societaslinguistica.eu/sle2026/wp-content/uploads/sites/9/2025/12/SLE_Large-Language-Models-for-Linguistics_updated.pdf

= lemmatization (solved, proof of concept)

state of the art: spacy, stanza and udpipe (95-99%)

- https://aclanthology.org/L16-1680/

llms match that, even on out-of-domain data

- https://aclanthology.org/2025.findings-emnlp.988/

eval metric: word-level accuracy, sentence-level accuracy

= pos tagging (solved through nlp, less on llms)

state of the art: spacy, udpipe, bert (97-98%)

real-world gap: hard on out-of domain = drops 4-5 percent, restoration requires new training data (rare)

- https://link.springer.com/article/10.1007/s10579-024-09751-x

llms are worse (85-90%)

- https://aclanthology.org/2024.propor-1.46.pdf

worse on low-resource languages:

- https://arxiv.org/html/2404.18286v1

limited UD tagset creates challenges (different POS in different languages)

- https://aclanthology.org/2024.acl-long.777/

eval metric: token-evel accuracy (upos), per-tag F1, cross-domain evaluation

= NER (models VERY specific and good, but not GENERAL)

dataset + gold standard: conll (92-95%)

- https://arxiv.org/abs/2310.16225

other datasets, ontonet

- https://www.intechopen.com/journals/1/articles/679

llms worse

- https://arxiv.org/html/2408.15796v2
- https://arxiv.org/abs/2304.10428
- https://arxiv.org/html/2402.09282v3

training is domain-specific:

- https://arxiv.org/abs/2311.08526
- https://pypi.org/project/gliner/0.2.5/

real-world problem: gold labels & human annotators disagree

multilingual problem

- https://masterdatascience.ubc.ca/why-data-science/data-stories/seasaltai

eval metric: f1, SOTA scores, strict or relaxed match?

= grammaticality (most promising for prompting & qualitative)

llms > humans (58-60%)

- https://www.pnas.org/doi/10.1073/pnas.2400917121
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11388322/
- https://www.englishjournal.net/archives/2025/vol7issue2/PartC/7-2-27-831.pdf

prompting is necessary:

- https://aclanthology.org/2025.naacl-long.380/
- https://arxiv.org/abs/2506.02302

qualitative difference (better on subj-verb agreement, word order vvilations; worse on island constranits, center embedding & comparative construction)

- https://www.englishjournal.net/archives/2025/vol7issue2/PartC/7-2-27-831.pdf

no dedicated tools for grammaticality judgements: BLiMP, CoLA = datasets

evaluation: accuracy (BLiMP), spearman/pearson correlation with gradient judgements, mcc

= presupposition (basically nothing)

literature is super sparse (only like 20 papers)

bert is fine-tuned, but still only like 80% on TEST set:

- https://aclanthology.org/2021.conll-1.28/

benchmarks: imppres, nope, commitment bank, confer and pub

- a lot of diversity in things like trigger types
- https://github.com/facebookresearch/Imppres
- https://arxiv.org/html/2506.06133
- https://arxiv.org/html/2401.07078v1

llms r ok, but biased and hallucinate, more false positives and bad at conditionals:

- https://aclanthology.org/2025.findings-acl.107.pdf
- https://arxiv.org/html/2505.22354

evaluation: macro f_1, spearman correlation, accuracy (NLI)

= coreference (sososo specific, requires training, being done now)

gold standard: maverick (83.6 f_1), corpipe

- https://aclanthology.org/2024.acl-long.722.pdf
- https://arxiv.org/pdf/2404.00727
- https://aclanthology.org/2025.crac-1.11/

the rest of stuff (spacy, etc.) is kinda bad

llms worse than supervised models

- https://arxiv.org/abs/2305.14489

true for multilingual:

- https://aclanthology.org/2025.crac-1.9.pdf

training helps:

- https://arxiv.org/html/2509.17505v1

evaluation: standard is MuC, B Cubed, CEAF
