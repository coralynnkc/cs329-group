# English pronoun-resolution batch-size study: cleaned summary

## Canonical files for reporting
- `chat_5.4_25_en.csv`
- `chat_5.4_100_en.csv`
- `chat_5.4_250_en.csv`
- `chat_5.4_500_en.csv`
- `sonnet_4.6_25_en.csv`
- `sonnet_4.6_100_en.csv`
- `sonnet_4.6_250_en.csv`
- `sonnet_4.6_500_en.csv`
- `opus_4.6_250_en.csv`
- `opus_4.6_500_en.csv`

## Files to archive or label as exploratory
- `chat_5.3_25_en.csv` — valid legacy run.
- `chat_5.3_100_en.csv` — malformed coverage (missing intended items and includes extra IDs).
- `chat_5.3_100_en_redo.csv` — wrong item set; not directly comparable to the intended 100-item subset.
- `chat_5.3_100_en_forced_complete.csv` — valid shape, but should be labeled as a forced follow-up / repair run.
- `chat_5.4_extended_500_en.csv` — not part of the main 25/100/250/500 comparison.

## Cleaned metrics

| family     |   size |   correct |   n |   accuracy_pct |   macro_f1 |   refusals |   missing |   extra |
|:-----------|-------:|----------:|----:|---------------:|-----------:|-----------:|----------:|--------:|
| Chat 5.3   |     25 |        25 |  25 |          100   |      1     |          0 |         0 |       0 |
| Chat 5.3   |    100 |        57 | 100 |           57   |      0.616 |          0 |        15 |       7 |
| Chat 5.3   |    100 |        64 | 100 |           64   |      0.64  |          0 |         0 |       0 |
| Chat 5.3   |    100 |        11 | 100 |           11   |      0.185 |          0 |        81 |      75 |
| Chat 5.4   |     25 |        24 |  25 |           96   |      0.978 |          1 |         0 |       0 |
| Chat 5.4   |    100 |        93 | 100 |           93   |      0.944 |          3 |         0 |       0 |
| Chat 5.4   |    250 |       214 | 250 |           85.6 |      0.865 |          5 |         0 |       0 |
| Chat 5.4   |    500 |       418 | 500 |           83.6 |      0.84  |          5 |         0 |       0 |
| Opus 4.6   |    250 |       239 | 250 |           95.6 |      0.958 |          1 |         0 |       0 |
| Opus 4.6   |    500 |       463 | 500 |           92.6 |      0.926 |          0 |         0 |       0 |
| Sonnet 4.6 |     25 |        24 |  25 |           96   |      0.96  |          0 |         0 |       0 |
| Sonnet 4.6 |    100 |        91 | 100 |           91   |      0.919 |          2 |         0 |       0 |
| Sonnet 4.6 |    250 |       213 | 250 |           85.2 |      0.852 |          0 |         0 |       0 |
| Sonnet 4.6 |    500 |       438 | 500 |           87.6 |      0.876 |          0 |         0 |       0 |

## Interpretation
- Chat 5.4 shows a strong decline as batch size increases.
- Sonnet 4.6 also declines, though less monotonically.
- Opus 4.6 remains much more stable at larger batch sizes.
- The biggest practical conclusion is that very large batch prompts can reduce pronoun-resolution quality, and model choice changes how severe that tradeoff is.

## Nested subset comparisons

| family     |   smaller |   larger |   smaller_better |   larger_better |   discordant |   mcnemar_p |
|:-----------|----------:|---------:|-----------------:|----------------:|-------------:|------------:|
| Chat 5.4   |        25 |      100 |                0 |               1 |            1 |    1        |
| Chat 5.4   |       100 |      250 |                9 |               5 |           14 |    0.42395  |
| Chat 5.4   |       250 |      500 |               19 |              20 |           39 |    1        |
| Sonnet 4.6 |        25 |      100 |                0 |               0 |            0 |    1        |
| Sonnet 4.6 |       100 |      250 |                2 |               2 |            4 |    1        |
| Sonnet 4.6 |       250 |      500 |               13 |              17 |           30 |    0.584665 |
| Opus 4.6   |       250 |      500 |                8 |               2 |           10 |    0.109375 |