# grammaticality-2.0

A parallel upgrade of the existing `grammatical/` folder for stronger **binary grammaticality** and **pairwise BLiMP** evaluation.

This version is designed around two principles:

1. **Separate task formats cleanly**
   - **CoLA-style binary judgment**: one sentence, predict `0` or `1`
   - **BLiMP-style pairwise judgment**: given two sentences, choose `A` or `B`

2. **Optimize for robust evaluation before prompt tweaking**
   - CoLA scoring includes **accuracy, MCC, precision, recall, F1, coverage, invalid rate, refusal rate**
   - BLiMP scoring includes **overall pairwise accuracy**, plus **per-dataset breakdown**, coverage, invalid rate, and refusal rate

## Why this folder exists

Your original `grammatical/` folder is a clean manual baseline, but it is centered on:
- mini sampling from CoLA train
- one direct prompt
- accuracy-only scoring

This `grammaticality-2.0/` folder adds:
- stronger prompt baselines for binary classification
- a dedicated BLiMP pairwise pipeline
- MCC as a first-class metric for CoLA
- better bookkeeping for invalid/refused outputs
- result summaries that are easier to compare across prompt styles

---

## Folder layout

```text
grammaticality-2.0/
├── README.md
├── data/
│   └── README.md
├── prompts/
│   ├── cola_direct_binary.txt
│   ├── cola_linguist_checklist.txt
│   ├── cola_minimal_repair.txt
│   ├── cola_fewshot_anchor.txt
│   ├── blimp_pairwise_direct.txt
│   ├── blimp_pairwise_checklist.txt
│   └── blimp_pairwise_repair.txt
├── mini/
├── results/
│   ├── cola_summary.csv
│   └── blimp_summary.csv
└── scripts/
    ├── make_cola_eval.py
    ├── score_cola.py
    ├── make_blimp_eval.py
    ├── score_blimp.py
    └── update_readme.py
```

---

## Prompt baselines included

I left out a gradient-rating prompt because you said you do **not** want to lean on scalar ratings that map poorly onto binary classification.

Instead, this folder gives you four stronger **binary** prompt families for CoLA and three **pairwise** prompt families for BLiMP.

### CoLA prompt families

1. **Direct binary**
   - simplest baseline
   - just define grammatical acceptability clearly and require `0/1`

2. **Linguist checklist**
   - instruct the model to judge syntax rather than truth, style, plausibility, or prescriptive rules
   - encourages attention to agreement, argument structure, binding, word order, extraction, etc.

3. **Minimal repair**
   - ask the model to internally decide whether the sentence would need grammatical repair before it could appear in native English
   - return only `0/1`

4. **Few-shot anchor**
   - same binary task, but with carefully chosen positive and negative examples
   - useful when the model confuses odd semantics with bad syntax

### BLiMP prompt families

1. **Pairwise direct**
   - pick which sentence is more grammatically acceptable: `A` or `B`

2. **Pairwise checklist**
   - same output format, but explicitly tell the model to focus on syntax and ignore plausibility

3. **Pairwise repair**
   - ask which sentence would require fewer grammatical repairs
   - can help on subtle minimal pairs

---

## Recommended experiment order

### Phase 1: CoLA
Use the existing CoLA files from `../grammatical/` and compare prompt variants on:
- `in_domain_dev.tsv`
- `out_of_domain_dev.tsv`

Run:
```bash
python scripts/make_cola_eval.py --split in_domain_dev
python scripts/make_cola_eval.py --split out_of_domain_dev
```

Then paste `mini/cola_<split>_input.csv` into a model using one of the prompt files.

Save outputs as:
```text
mini/predictions_<model>_<prompt>_<split>.csv
```

Examples:
```text
mini/predictions_sonnet_direct_in_domain_dev.csv
mini/predictions_sonnet_checklist_out_of_domain_dev.csv
```

Score:
```bash
python scripts/score_cola.py --model sonnet --prompt direct --split in_domain_dev
python scripts/score_cola.py --model sonnet --prompt checklist --split out_of_domain_dev
```

### Phase 2: BLiMP
Put BLiMP files under `data/blimp/` (details in `data/README.md`).

Build an evaluation file:
```bash
python scripts/make_blimp_eval.py --source-dir data/blimp
```

Paste `mini/blimp_input.csv` into a model using one of the BLiMP prompt files.

Save outputs as:
```text
mini/predictions_<model>_<prompt>_blimp.csv
```

Score:
```bash
python scripts/score_blimp.py --model sonnet --prompt direct
```

---

## File naming conventions

### CoLA predictions
```text
predictions_<model>_<prompt>_<split>.csv
```

Where:
- `<model>`: `sonnet`, `opus`, `gpt5`, etc.
- `<prompt>`: `direct`, `checklist`, `repair`, `fewshot`
- `<split>`: `in_domain_dev`, `out_of_domain_dev`

### BLiMP predictions
```text
predictions_<model>_<prompt>_blimp.csv
```

Where:
- `<prompt>`: `direct`, `checklist`, `repair`

---

## Output formats expected from the model

### CoLA
The model should return only:
```csv
id,predicted_label
1,1
2,0
3,1
```

or:
```csv
sample_id,id,predicted_label
1,1,1
1,2,0
```

Both are accepted.

### BLiMP
The model should return only:
```csv
pair_id,predicted_option
1,A
2,B
3,A
```

or:
```csv
id,predicted_option
1,A
2,B
3,A
```

Both are accepted.

---

## Metrics tracked

### CoLA
- accuracy
- MCC
- precision for label 1
- recall for label 1
- F1 for label 1
- coverage
- refusal rate
- invalid prediction rate
- counts of TP / TN / FP / FN

### BLiMP
- overall pairwise accuracy
- per-dataset pairwise accuracy
- coverage
- refusal rate
- invalid prediction rate

---

## Suggested starting matrix

### CoLA
- sonnet × direct
- sonnet × checklist
- sonnet × repair
- sonnet × fewshot
- opus × direct
- opus × checklist

### BLiMP
- sonnet × direct
- sonnet × checklist
- sonnet × repair

This is enough to see whether:
- syntax-focused prompting beats the plain baseline
- repair framing helps or hurts
- few-shot anchors improve subtle discrimination
- improvements transfer out of domain

---

## Notes on Pearson / Spearman with gradient judgments

This folder intentionally does **not** implement gradient scoring because you said you do not want a gradient-style prompting regime. That is a reasonable choice for a binary-first workflow.

If you later decide you still want Pearson/Spearman, the clean version is:
- keep the binary track for CoLA and BLiMP
- add a **separate** scalar-confidence or rating track
- do **not** mix the two into one primary metric

---

## Refresh the README tables

After scoring runs, update the README tables:
```bash
python scripts/update_readme.py
```

This script rebuilds:
- CoLA results table
- BLiMP results table


## CoLA Results Table

| Model | Prompt | Split | N | Accuracy | MCC | Precision(1) | Recall(1) | F1(1) | Coverage | Refusal rate | Invalid rate |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |

## BLiMP Results Table

| Model | Prompt | N | Accuracy | Coverage | Refusal rate | Invalid rate |
| --- | --- | ---: | ---: | ---: | ---: | ---: |

## Suggested next upgrade

The next clean step after this folder is not more prompt complexity. It is:
1. run the binary prompt sweep on both CoLA dev splits
2. identify where MCC improves without coverage collapsing
3. then run the top 1-2 prompt families on BLiMP
4. only after that decide whether gradient judgments are worth adding back as a separate track
