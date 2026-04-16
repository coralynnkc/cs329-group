ner seems like the ideal task to demonstrate poc for ts

specific models we can benchmark against: pubmedbert

pubmedbert > biobert, demonstrating that training is extremely, extremely important
- https://arxiv.org/html/2508.01630v1
- https://arxiv.org/html/2305.04928v5

llms worse
- https://arxiv.org/abs/2203.08410

something complex (distillation?) can do this, managing to reach sota? performance:

- https://arxiv.org/abs/2305.05003
- https://pmc.ncbi.nlm.nih.gov/articles/PMC10482322/

other improvement techniques:
- reformulate ner as text-to-text generation with special tokens marking entities; self-verification curbs hallucations; https://arxiv.org/abs/2304.10428
- cot: https://arxiv.org/abs/2305.15444
- decompose extraction into entity-then-relation dialogues: https://www.scribd.com/document/888484398/ChatIE-Zero-Shot-Information-Extraction-via-Chatting-With-ChatGPT
- code-based ie casts extraction as python code generation, leveraging code-pretrained models' stronger structured-output capabilities: https://www.semanticscholar.org/reader/a86dd6c62d3dc9c7989c98a3e4ace3fd8000e515

randomly permuting labels in in-context examples barely hurts classification performance

self-consistency (how is this different than cot?) lifts chain-of-thought performance
- https://arxiv.org/abs/2203.11171

when llms win:
- unseen domains
- novel / dynamic label schemas
- complex extractions requiring reasoning

distillation into a vicuna-based model was WAY better than normal chat

- https://openreview.net/pdf?id=r65xfUb76p

biogpt:
- https://arxiv.org/pdf/2210.10341

better than bert - covid proves

problems:
- systematic overclassification, requires training data to correct - errs towards correct on edge cases
- pretty weak on multilingual ner tagging
- hallucination: https://arxiv.org/abs/2304.10428v2 
- span boundariy errors: https://www.semanticscholar.org/reader/97782a67971c4ff1a74bf07e82fe20b2c4bf86c4
- position bias: https://aclanthology.org/2024.tacl-1.9/
- prompt sensitivity: https://openreview.net/forum?id=RIu5lyNXjT

conclusion:
- distillation into specialist models is dominant
- structured output infra is making generative ie more reliable
- agentic and retrieval-augmented ie is the frontier for extraction
- open-weight parity enables self-hosted pipelines
