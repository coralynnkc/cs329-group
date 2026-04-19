# grammaticality-2.0

A CoLA-focused evaluation folder for testing how prompt design affects English grammaticality judgments.

## Overview

This folder currently documents a **prompt comparison on CoLA** using **Chat 5.4**.


## What this folder contains

- CoLA sample and evaluation files in `mini/`
- prompt templates in `prompts/`
- scoring and data-prep scripts in `scripts/`
- canonical result files in `results/`
- a summary file in `results/cola_summary.csv`

## Experimental setup

### Task
Binary grammaticality judgment on CoLA.

### Model
Chat 5.4

### Prompts compared
- `direct`
- `anchor`
- `repair`
- `finetuned`
- `checklist`

### Splits evaluated
- `in_domain_dev_sample100`
- `out_of_domain_dev_sample100`

### Metrics tracked
- Accuracy
- MCC
- F1 for label 0
- F1 for label 1
- Macro-F1
- Coverage
- Refusal rate
- Invalid prediction rate

## Canonical files

### Gold / input files
- `mini/cola_in_domain_dev_sample100_input.csv`
- `mini/cola_in_domain_dev_sample100_answers.csv`
- `mini/cola_out_of_domain_dev_sample100_input.csv`
- `mini/cola_out_of_domain_dev_sample100_answers.csv`

### Result files
- `results/CHAT_5.4_cola_100_direct.csv`
- `results/CHAT_5.4_cola_100_anchor.csv`
- `results/CHAT_5.4_cola_100_repair.csv`
- `results/CHAT_5.4_cola_100_finetuned.csv`
- `results/CHAT_5.4_cola_100_checklist.csv`
- `results/CHAT_5.4_cola_100_direct_out_of_domain_.csv`
- `results/CHAT_5.4_cola_100_anchor_out_of_domain_.csv`
- `results/CHAT_5.4_cola_100_repair_out_of_domain_.csv`
- `results/CHAT_5.4_cola_100_finetuned_out_of_domain_.csv`
- `results/CHAT_5.4_cola_100_checklist_out_of_domain_.csv`
- `results/cola_summary.csv`

### Main scripts
- `scripts/make_cola_sample.py`
- `scripts/make_cola_eval.py`
- `scripts/cli_score_cola_updated.py`
- `scripts/update_readme.py`

## Main results

### Cleaned results table

| Prompt | Split | N | Accuracy | MCC | Macro-F1 | Coverage | Refusal rate | Invalid rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| direct | in-domain | 100 | 0.88 | 0.7252 | 0.8621 | 1.00 | 0.00 | 0.00 |
| anchor | in-domain | 100 | 0.89 | 0.7453 | 0.8725 | 1.00 | 0.00 | 0.00 |
| repair | in-domain | 100 | 0.89 | 0.7453 | 0.8725 | 1.00 | 0.00 | 0.00 |
| finetuned | in-domain | 100 | 0.89 | 0.7453 | 0.8725 | 1.00 | 0.00 | 0.00 |
| checklist | in-domain | 100 | 0.56 | -0.0472 | 0.4762 | 1.00 | 0.00 | 0.00 |
| direct | out-of-domain | 100 | 0.86 | 0.6638 | 0.8300 | 1.00 | 0.00 | 0.00 |
| anchor | out-of-domain | 100 | 0.86 | 0.6616 | 0.8264 | 1.00 | 0.00 | 0.00 |
| repair | out-of-domain | 100 | 0.86 | 0.6638 | 0.8300 | 1.00 | 0.00 | 0.00 |
| finetuned | out-of-domain | 100 | 0.85 | 0.6357 | 0.8075 | 1.00 | 0.00 | 0.00 |
| checklist | out-of-domain | 100 | 0.90 | 0.7615 | 0.8760 | 1.00 | 0.00 | 0.00 |

## Interpretation

On the 100-example in-domain sample, anchor, repair, and finetuned tie for best at 0.89 accuracy and 0.7453 MCC, with direct just behind at 0.88 / 0.7252. checklist collapses badly in-domain at 0.56 accuracy and -0.0472 MCC. On the 100-example out-of-domain sample, the ranking flips: checklist is best at 0.90 accuracy and 0.7615 MCC, while direct, repair, and anchor cluster around 0.86 accuracy and ~0.66 MCC, and finetuned lands at 0.85 / 0.6357. Across all ten runs, coverage is 1.0 with 0 refusal and 0 invalid rate, so these differences reflect actual classification behavior rather than output-format failures.
The main conclusion is not “one universally best prompt.” It is that prompt effectiveness is split-sensitive in this folder. Direct is the safest overall baseline because it stays strong on both splits, while checklist is highly unstable: worst by far in-domain, best out-of-domain. Also, the apparent in-domain improvements among the top prompts are very small in practical terms: anchor and direct differ on only one in-domain prediction, and anchor/repair differ on only two.

### 1. There is no universally best prompt
Prompt quality depends on the split.

- On the **in-domain** sample, `anchor`, `repair`, and `finetuned` tie for best.
- On the **out-of-domain** sample, `checklist` performs best.

That means this folder does **not** support the claim that one prompt cleanly dominates across settings.

### 2. `direct` is the safest general baseline
`direct` is not always the top performer, but it is consistently strong on both splits and avoids the instability seen with `checklist`.

If you need one default prompt for follow-up testing, `direct` is the safest choice.

### 3. `checklist` is highly split-sensitive
`checklist` is the clearest example of prompt instability:

- worst by far in-domain
- best out-of-domain

That makes it interesting analytically, but risky as a general-purpose default.

### 4. The in-domain gains among top prompts are small
The top in-domain prompts are extremely close.

For example:
- `anchor` and `direct` differ on only **one** in-domain prediction
- `anchor` and `repair` differ on only **two** in-domain predictions

So the differences are real, but modest.

### 5. These are genuine classification differences
All runs have:
- **100% coverage**
- **0 refusal rate**
- **0 invalid prediction rate**

So the performance differences are coming from model judgments, not formatting failures or missing outputs.

## Recommended conclusions

A careful summary of this folder would be:

> Prompt engineering does matter for CoLA-style grammaticality judgments, but its effects are split-sensitive rather than universally beneficial. `Direct` is the strongest all-purpose baseline in this folder, while `checklist` appears especially sensitive to domain shift.

## Recommended repo cleanup

### Suggested `results/` structure

```text
results/
├── canonical/
│   ├── CHAT_5.4_cola_100_direct.csv
│   ├── CHAT_5.4_cola_100_anchor.csv
│   ├── CHAT_5.4_cola_100_repair.csv
│   ├── CHAT_5.4_cola_100_finetuned.csv
│   ├── CHAT_5.4_cola_100_checklist.csv
│   ├── CHAT_5.4_cola_100_direct_out_of_domain_.csv
│   ├── CHAT_5.4_cola_100_anchor_out_of_domain_.csv
│   ├── CHAT_5.4_cola_100_repair_out_of_domain_.csv
│   ├── CHAT_5.4_cola_100_finetuned_out_of_domain_.csv
│   └── CHAT_5.4_cola_100_checklist_out_of_domain_.csv
├── summaries/
│   ├── cola_summary.csv
│   ├── grammaticality_cleaned_metrics.csv
│   └── grammaticality_prompt_summary.csv
└── archive/
    └── chat_README.md
```

## Example commands

### Build 100-example CoLA samples

```bash
python scripts/make_cola_sample.py --split in_domain_dev --sample-size 100 --seed 42
python scripts/make_cola_sample.py --split out_of_domain_dev --sample-size 100 --seed 42
```

### Build full CoLA evaluation exports

```bash
python scripts/make_cola_eval.py --split in_domain_dev
python scripts/make_cola_eval.py --split out_of_domain_dev
```

### Score a run

```bash
python scripts/cli_score_cola_updated.py \
  --gold mini/cola_in_domain_dev_sample100_answers.csv \
  --pred results/CHAT_5.4_cola_100_direct.csv
```

```bash
python scripts/cli_score_cola_updated.py \
  --gold mini/cola_out_of_domain_dev_sample100_answers.csv \
  --pred results/CHAT_5.4_cola_100_checklist_out_of_domain_.csv
```

## Best next step

Do not add more prompt variants yet.

A cleaner next step is to replicate the strongest candidates on a second model:
- `direct` as the general baseline
- `anchor` as the strongest in-domain challenger
- `checklist` as the strongest out-of-domain challenger

That will tell you whether the split reversal is a robust pattern or just a Chat 5.4-specific result.
