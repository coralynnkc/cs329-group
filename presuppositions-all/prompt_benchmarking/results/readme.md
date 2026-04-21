# Results Directory

This folder stores prediction files and summary outputs for the presupposition prompt-benchmarking experiments.

## What lives here

- per-model or per-prompt prediction folders such as `chat_5.4_p0/`, `chat_5.4_p2/`, or `CONFER-chat-5.4/`
- JSON summary files written by the batch scorers
- CSV outputs that preserve the original model probability distributions

## Output format

Most prediction files in this experiment family use probabilistic three-way labeling:

```csv
item_id,e_probability,n_probability,c_probability
```

The scorers then:

1. match rows by `item_id`
2. normalize probabilities when needed
3. derive hard labels by argmax
4. compute metrics such as accuracy, macro-F1, log loss, and multiclass Brier score
5. compute centroid-style diagnostics over the probability simplex

## Centroid note

In these experiments, "centroid" refers to the average predicted probability vector for each gold label class:

- gold `E`: average of `(E, N, C)` probabilities over all gold-`E` items
- gold `N`: average over all gold-`N` items
- gold `C`: average over all gold-`C` items

This is a descriptive diagnostic of class geometry and separability, not a primary success metric.

## Which scorer to use

- multilingual prompt benchmarking:

```bash
python3 scripts/batch_scorer_evaluation.py --presup-dir . --results results/<folder> --output results/<folder>/results_summary.json
```

- CONFER English prompt benchmarking:

```bash
python3 scripts/batch_scorer_CONFER.py --gold confer_en/presupposition_answers.csv --results results/<folder> --output results/<folder>/results_summary.json
```
