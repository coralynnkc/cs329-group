# European MLM Baseline

This directory contains the imported multilingual pronoun-resolution baseline copied from `srijon-2.0`.

It is kept as a self-contained subtree because it represents a **different benchmark family** from the main `pronoun_resolution/mlm_african/` workflow.

## What this baseline is

According to the imported `srijon-2.0` documentation, this pronoun-resolution baseline uses:

- **WinoGrande** for English
- **Wino-X** for French, German, and Russian

Languages present:

- `en`
- `fr`
- `de`
- `ru`

This makes it the second multilingual benchmark line in the main project.

## Why it lives separately

The main `pronoun_resolution/mlm_african/` workflow uses a different benchmark family and different language set:

- `en`
- `am`
- `ig`
- `zu`

So while both subtrees are pronoun-resolution prompt-engineering work, they should not be collapsed into one undifferentiated dataset folder.

## Layout

- `pronoun_resolution/` -> imported normalized benchmark data and results tree
- `answers/pronoun_resolution/` -> imported answer/match artifacts from `srijon-2.0/answers/pronoun_resolution/`
- `scripts/` -> imported normalization, split, and scoring scripts
- `docs/` -> imported notes on assumptions, splits, schemas, and task inventory
- `prompts/` -> imported generic prompt template
- `SRIJON_2_0_README.md` -> preserved top-level source overview

## Included answer artifacts

The unified baseline now also includes the separate answer and match files that were stored in `srijon-2.0/answers/pronoun_resolution/`.

These include:

- `english_with_match.xlsx`
- `lm_wino_x_en-de_only_with_match.xlsx`
- `lm_wino_x_en-fr_only_with_match.xlsx`
- `lm_wino_x_en-ru_only_with_match.xlsx`
- `challenge_and_miss_answers/`

These files are useful when you want the explicit answer-aligned artifacts in addition to the normalized benchmark CSVs that already contain `gold_answer`.

## Included documentation

The unified baseline also includes the relevant `srijon-2.0/docs/` materials because they contain important provenance and pipeline notes for this benchmark.

In particular:

- `docs/task_inventory.md` explains dataset origin, language coverage, schemas, and row counts
- `docs/assumptions.md` records normalization decisions and known gaps
- `docs/label_normalization.md` explains scoring conventions
- `docs/split_strategy.md` records the documented split policy
- `docs/README.md` summarizes which of those files matter most for pronoun resolution

Some of these docs are cross-task rather than pronoun-resolution-only. They were kept intentionally, since trimming them would lose useful context about how the imported baseline was constructed.

## Important path note

The imported scripts are preserved close to their original assumptions.

For example, scripts in `scripts/` expect the benchmark tree to live at:

```text
mlm_european/pronoun_resolution/
```

That relationship has been kept intact on purpose so the imported infrastructure does not silently break.

## Best starting points

- [SRIJON_2_0_README.md](SRIJON_2_0_README.md)
- [docs/README.md](docs/README.md)
- [answers/pronoun_resolution/readme.md](answers/pronoun_resolution/readme.md)
- [docs/task_inventory.md](docs/task_inventory.md)
- [docs/assumptions.md](docs/assumptions.md)
- [docs/split_strategy.md](docs/split_strategy.md)

## Results Snapshot

The compact scored summaries for this subtree live in:

- `pronoun_resolution/results/results_summary_sonnet_4.6.json`
- `pronoun_resolution/results/results_summary_gpt_5.4.json`

Those summaries cover `20` dev-sample100 runs per model
(`4` languages × `5` prompts).

From the saved numbers:

- Sonnet 4.6 is strongest on Russian, where the saved runs are `0.95` to `0.97` accuracy.
- Sonnet 4.6 is also strong on French (`0.88` to `0.91`) and English (`0.89` across prompts), with German somewhat lower (`0.86` to `0.88`).
- Chat 5.4 is competitive on German (`0.88` to `0.89`) and French (`0.90` to `0.93`), but weaker on English in this benchmark (`0.84` to `0.86`).
- Chat 5.4 Russian remains strong as well (`0.90` to `0.93`), though below the saved Sonnet Russian scores.
- Refusal rates are generally negligible in these summaries (`0.00` to `0.01`).

## Current Conclusions

- In this European benchmark family, language differences are larger than prompt differences.
- Sonnet 4.6 is the strongest overall saved baseline here, especially on Russian.
- Chat 5.4 remains competitive, particularly on German and French, but is noticeably weaker on English in the current saved runs.
