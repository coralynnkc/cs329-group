#!/usr/bin/env python3
"""
join_and_split.py
=================
Joins gold labels from answers/ into source/ and full/ master files,
then applies an 80/10/10 train/dev/test split to every task/language.

Safe to rerun — all outputs are overwritten deterministically.

Usage
-----
    # from repo root:
    python srijon-2.0/scripts/join_and_split.py

    # or from inside srijon-2.0/:
    python scripts/join_and_split.py

What is joined
--------------
  presuppositions/en   — gold_label (E/N/C) from CONFER xlsx, positional
  presuppositions/fr,de,hi,ru,vi — gold_label (E/N/C mapped from XNLI 0/1/2), positional
  pronoun_resolution/en — option_a, option_b, gold_answer (A/B) from WinoGrande xlsx, positional
  pronoun_resolution/de,fr,ru — gold_answer (A/B from answer=1/2), positional
  lemmatization/en     — gold_lemma from UniMorph xlsx, word-grouped positional

After joining, each master source file includes the gold column.
Full files have gold + empty model placeholder columns.
Inference files have NO gold columns (model-facing only).

Split parameters (docs/split_strategy.md)
------------------------------------------
  Fractions : 80% train / 10% dev / 10% test
  Seed      : 42
  Method    : simple random shuffle; row order preserved within each split
"""

import csv
import random
import sys
from collections import defaultdict
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("[ERROR] openpyxl not found. Run: pip install --user openpyxl")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE = Path(__file__).resolve().parents[1]   # srijon-2.0/
SEED = 42
XNLI_MAP = {"0": "E", "1": "N", "2": "C"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_csv_file(path: Path) -> tuple[list[str], list[dict]]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    return fieldnames, rows


def write_csv_file(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_xlsx_rows(path: Path) -> list[dict]:
    """Return list of dicts from Sheet1/active sheet of xlsx (header row → keys)."""
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    raw = list(ws.iter_rows(values_only=True))
    if not raw:
        return []
    header = [str(c) if c is not None else f"_col{i}" for i, c in enumerate(raw[0])]
    return [dict(zip(header, row)) for row in raw[1:]]


def to_ab(val) -> str:
    """Convert answer value 1/2 (int, float, or string) to 'A'/'B'."""
    s = str(val).strip().rstrip(".0")  # handle '1', '1.0', 2, 2.0
    return "A" if s == "1" else "B"


def split_rows(rows: list[dict]) -> tuple[list, list, list]:
    """
    Shuffle row indices with SEED and split 80/10/10.
    Rows within each split are returned in their original relative order.
    """
    n = len(rows)
    indices = list(range(n))
    rng = random.Random(SEED)
    rng.shuffle(indices)
    n_train = round(n * 0.80)
    n_dev   = round(n * 0.10)
    train_idx = sorted(indices[:n_train])
    dev_idx   = sorted(indices[n_train : n_train + n_dev])
    test_idx  = sorted(indices[n_train + n_dev :])
    return (
        [rows[i] for i in train_idx],
        [rows[i] for i in dev_idx],
        [rows[i] for i in test_idx],
    )


def write_split_trio(
    base_dir: Path,
    lang: str,
    src_fields: list[str],
    inf_fields: list[str],
    full_extra: list[str],
    train: list, dev: list, test: list,
) -> None:
    """Write source / inference / full CSV for each of train, dev, test."""
    full_fields = src_fields + full_extra
    for split_name, split_rows_list in [("train", train), ("dev", dev), ("test", test)]:
        # source
        write_csv_file(
            base_dir / "source" / f"{lang}_{split_name}.csv",
            src_fields, split_rows_list,
        )
        # inference (no gold)
        write_csv_file(
            base_dir / "inference" / f"{lang}_{split_name}_inference.csv",
            inf_fields,
            [{c: r[c] for c in inf_fields} for r in split_rows_list],
        )
        # full (gold + empty model columns)
        empty = {c: "" for c in full_extra}
        write_csv_file(
            base_dir / "full" / f"{lang}_{split_name}_full.csv",
            full_fields,
            [{**r, **empty} for r in split_rows_list],
        )


# ---------------------------------------------------------------------------
# 1.  Presuppositions
# ---------------------------------------------------------------------------

PRESUPP_ANSWER_SPECS = {
    # lang: (answer_path, file_type, gold_col, label_map)
    "en": ("answers/presupp/english_presuppositions_with_match.xlsx", "xlsx", "gold_label",  None),
    "fr": ("answers/presupp/fr_test_with_match.csv",                  "csv",  "label_theory", XNLI_MAP),
    "de": ("answers/presupp/de_test_with_match.csv",                  "csv",  "label_theory", XNLI_MAP),
    "hi": ("answers/presupp/hi_test_with_match.csv",                  "csv",  "label",        XNLI_MAP),
    "ru": ("answers/presupp/ru_test_with_match.csv",                  "csv",  "label_theory", XNLI_MAP),
    "vi": ("answers/presupp/vi_test_with_match.csv",                  "csv",  "label_theory", XNLI_MAP),
}

PS_INF_COLS  = ["item_id", "premise", "hypothesis"]
PS_FULL_EXTRA = ["model_label", "correct"]

print("=== Presuppositions ===")
for lang, (ans_rel, ftype, gold_col, label_map) in PRESUPP_ANSWER_SPECS.items():
    ans_path = BASE / ans_rel
    if ftype == "xlsx":
        ans_rows = read_xlsx_rows(ans_path)
    else:
        _, ans_rows = read_csv_file(ans_path)

    gold_labels = []
    for r in ans_rows:
        raw = str(r.get(gold_col, "") or "").strip()
        gold_labels.append(label_map[raw] if label_map else raw)

    src_path = BASE / f"presuppositions/{lang}/source/{lang}_master.csv"
    _, src_rows = read_csv_file(src_path)

    if len(src_rows) != len(gold_labels):
        n = min(len(src_rows), len(gold_labels))
        print(f"  [WARN] {lang}: row count mismatch ({len(src_rows)} vs {len(gold_labels)}) — using first {n}")
        src_rows, gold_labels = src_rows[:n], gold_labels[:n]

    for row, gl in zip(src_rows, gold_labels):
        row["gold_label"] = gl

    src_fields = ["item_id", "premise", "hypothesis", "gold_label"]

    # Write master source / inference / full
    write_csv_file(src_path, src_fields, src_rows)
    write_csv_file(
        BASE / f"presuppositions/{lang}/inference/{lang}_master_inference.csv",
        PS_INF_COLS,
        [{c: r[c] for c in PS_INF_COLS} for r in src_rows],
    )
    full_fields = src_fields + PS_FULL_EXTRA
    write_csv_file(
        BASE / f"presuppositions/{lang}/full/{lang}_master_full.csv",
        full_fields,
        [{**r, "model_label": "", "correct": ""} for r in src_rows],
    )

    # Split
    train, dev, test = split_rows(src_rows)
    write_split_trio(
        BASE / f"presuppositions/{lang}", lang,
        src_fields, PS_INF_COLS, PS_FULL_EXTRA,
        train, dev, test,
    )

    print(
        f"  {lang}: {len(src_rows)} rows  "
        f"gold_label joined  "
        f"→ train={len(train)} dev={len(dev)} test={len(test)}"
    )


# ---------------------------------------------------------------------------
# 2.  Pronoun Resolution — English
# ---------------------------------------------------------------------------

print("\n=== Pronoun Resolution / EN ===")

en_pr_ans = read_xlsx_rows(BASE / "answers/pronoun_resolution/english_with_match.xlsx")
en_pr_src_path = BASE / "pronoun_resolution/en/source/en_master.csv"
_, en_pr_src = read_csv_file(en_pr_src_path)

if len(en_pr_src) != len(en_pr_ans):
    n = min(len(en_pr_src), len(en_pr_ans))
    print(f"  [WARN] EN PR row mismatch ({len(en_pr_src)} vs {len(en_pr_ans)}) — using first {n}")
    en_pr_src, en_pr_ans = en_pr_src[:n], en_pr_ans[:n]

for row, ans in zip(en_pr_src, en_pr_ans):
    row["option_a"]    = str(ans.get("option1") or "").strip()
    row["option_b"]    = str(ans.get("option2") or "").strip()
    row["gold_answer"] = to_ab(ans.get("answer", ""))

en_pr_src_fields = ["item_id", "sentence", "option_a", "option_b", "gold_answer"]
en_pr_inf_fields = ["item_id", "sentence", "option_a", "option_b"]
en_pr_full_extra = ["model_prediction", "correct"]

write_csv_file(en_pr_src_path, en_pr_src_fields, en_pr_src)
write_csv_file(
    BASE / "pronoun_resolution/en/inference/en_master_inference.csv",
    en_pr_inf_fields,
    [{c: r[c] for c in en_pr_inf_fields} for r in en_pr_src],
)
write_csv_file(
    BASE / "pronoun_resolution/en/full/en_master_full.csv",
    en_pr_src_fields + en_pr_full_extra,
    [{**r, "model_prediction": "", "correct": ""} for r in en_pr_src],
)

train, dev, test = split_rows(en_pr_src)
write_split_trio(
    BASE / "pronoun_resolution/en", "en",
    en_pr_src_fields, en_pr_inf_fields, en_pr_full_extra,
    train, dev, test,
)
print(f"  en: {len(en_pr_src)} rows  option_a/b + gold_answer added  → train={len(train)} dev={len(dev)} test={len(test)}")


# ---------------------------------------------------------------------------
# 3.  Pronoun Resolution — DE / FR / RU
# ---------------------------------------------------------------------------

print("\n=== Pronoun Resolution / DE FR RU ===")

PR_NONENG_SPECS = {
    "de": "answers/pronoun_resolution/lm_wino_x_en-de_only_with_match.xlsx",
    "fr": "answers/pronoun_resolution/lm_wino_x_en-fr_only_with_match.xlsx",
    "ru": "answers/pronoun_resolution/lm_wino_x_en-ru_only_with_match.xlsx",
}
PR_INF_COLS  = ["item_id", "sentence", "option_a", "option_b"]
PR_FULL_EXTRA = ["model_prediction", "correct"]

for lang, ans_rel in PR_NONENG_SPECS.items():
    ans_rows = read_xlsx_rows(BASE / ans_rel)
    src_path = BASE / f"pronoun_resolution/{lang}/source/{lang}_master.csv"
    _, src_rows = read_csv_file(src_path)

    if len(src_rows) != len(ans_rows):
        n = min(len(src_rows), len(ans_rows))
        print(f"  [WARN] PR {lang}: row mismatch ({len(src_rows)} vs {len(ans_rows)}) — using first {n}")
        src_rows, ans_rows = src_rows[:n], ans_rows[:n]

    for row, ans in zip(src_rows, ans_rows):
        row["gold_answer"] = to_ab(ans.get("answer", ""))

    src_fields = ["item_id", "sentence", "option_a", "option_b", "gold_answer"]
    write_csv_file(src_path, src_fields, src_rows)
    write_csv_file(
        BASE / f"pronoun_resolution/{lang}/inference/{lang}_master_inference.csv",
        PR_INF_COLS,
        [{c: r[c] for c in PR_INF_COLS} for r in src_rows],
    )
    write_csv_file(
        BASE / f"pronoun_resolution/{lang}/full/{lang}_master_full.csv",
        src_fields + PR_FULL_EXTRA,
        [{**r, "model_prediction": "", "correct": ""} for r in src_rows],
    )

    train, dev, test = split_rows(src_rows)
    write_split_trio(
        BASE / f"pronoun_resolution/{lang}", lang,
        src_fields, PR_INF_COLS, PR_FULL_EXTRA,
        train, dev, test,
    )
    print(f"  {lang}: {len(src_rows)} rows  gold_answer joined  → train={len(train)} dev={len(dev)} test={len(test)}")


# ---------------------------------------------------------------------------
# 4.  Lemmatization — English
# ---------------------------------------------------------------------------

print("\n=== Lemmatization / EN ===")

lm_ans_rows = read_xlsx_rows(BASE / "answers/english_lemmas_with_match.xlsx")
lm_src_path = BASE / "lemmatization/en/source/en_master.csv"
_, lm_src = read_csv_file(lm_src_path)

# Build word → [gold_lemma, ...] from answer rows (preserving order within each word group)
ans_by_word: dict[str, list[str]] = defaultdict(list)
for r in lm_ans_rows:
    word = str(r.get("word") or "").strip()
    lemma = str(r.get("unimorph_lemma") or "").strip()
    ans_by_word[word].append(lemma)

consumed: dict[str, int] = defaultdict(int)
joined_count = 0
unmatched_count = 0

for row in lm_src:
    word = str(row.get("word") or "").strip()
    bucket = ans_by_word.get(word, [])
    idx = consumed[word]
    if idx < len(bucket):
        row["gold_lemma"] = bucket[idx]
        consumed[word] += 1
        joined_count += 1
    else:
        row["gold_lemma"] = ""
        unmatched_count += 1

lm_src_fields  = ["item_id", "word", "gold_lemma"]
lm_inf_fields  = ["item_id", "word"]
lm_full_extra  = ["model_lemma", "correct"]

write_csv_file(lm_src_path, lm_src_fields, lm_src)
write_csv_file(
    BASE / "lemmatization/en/inference/en_master_inference.csv",
    lm_inf_fields,
    [{c: r[c] for c in lm_inf_fields} for r in lm_src],
)
write_csv_file(
    BASE / "lemmatization/en/full/en_master_full.csv",
    lm_src_fields + lm_full_extra,
    [{**r, "model_lemma": "", "correct": ""} for r in lm_src],
)

train, dev, test = split_rows(lm_src)
write_split_trio(
    BASE / "lemmatization/en", "en",
    lm_src_fields, lm_inf_fields, lm_full_extra,
    train, dev, test,
)
print(
    f"  en: {len(lm_src)} rows  "
    f"gold_lemma joined for {joined_count} rows  "
    f"({unmatched_count} unmatched → empty)  "
    f"→ train={len(train)} dev={len(dev)} test={len(test)}"
)


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print("\n=== Done ===")
print(
    "All gold labels joined and 80/10/10 splits written.\n"
    "Master files (_master.*) preserved alongside train/dev/test splits.\n"
    "Inference files contain no gold labels.\n"
    "Full files contain gold + empty model_* placeholder columns."
)
