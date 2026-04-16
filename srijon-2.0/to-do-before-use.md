Join gold labels — use XNLI test split for FR/DE/HI/RU/VI presuppositions; CONFER for EN; WinoGrande for EN pronoun resolution; UniMorph for lemmatization.
Run a split — follow docs/split_strategy.md when ready for train/dev/test evaluation.
Source Hindi/Vietnamese pronoun resolution — those languages are missing entirely from the pronoun resolution task.
Verify XNLI label mapping — confirm the {0→E, 1→N, 2→C} mapping against the specific XNLI split you use (see docs/label_normalization.md).
Re-run normalize.py any time — it is safe and idempotent.