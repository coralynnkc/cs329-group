# Data expectations

## CoLA
This folder reuses the CoLA files already present in the sibling folder:

- `../grammatical/in_domain_train.tsv`
- `../grammatical/in_domain_dev.tsv`
- `../grammatical/out_of_domain_dev.tsv`

You do **not** need to duplicate those files here.

## BLiMP
Place BLiMP files inside:

```text
data/blimp/
```

The scripts accept a directory of `.jsonl`, `.csv`, or `.tsv` files.

### Supported field names

The loader tries to detect common pairwise columns automatically.

For the **good / acceptable** sentence, it looks for one of:
- `sentence_good`
- `good_sentence`
- `good`
- `acceptable`
- `sentence1_good`
- `grammatical`
- `sentence_a_good`

For the **bad / unacceptable** sentence, it looks for one of:
- `sentence_bad`
- `bad_sentence`
- `bad`
- `unacceptable`
- `sentence1_bad`
- `ungrammatical`
- `sentence_b_bad`

If your files use different names, edit the key lists near the top of `scripts/make_blimp_eval.py`.

### Recommended structure
The easiest setup is one file per BLiMP subdataset, for example:

```text
data/blimp/
├── anaphor_gender_agreement.jsonl
├── animate_subject_passive.jsonl
├── coordinate_structure_constraint_complex_left_branch.jsonl
└── ...
```

The scorer will use the filename stem as the dataset name if no dataset column is present.
