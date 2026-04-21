#!/usr/bin/env python3
"""
normalize.py — srijon-2.0 data normalization pipeline
=======================================================
Reads the original /srijon/data/ files, normalizes them into a clean
task/language/split directory layout, and writes:
  source/     — canonical source CSV (all original columns + item_id)
  inference/  — model-facing CSV (minimal schema only)
  full/       — scorer-ready CSV (source + empty prediction columns)
  results/    — placeholder directory (not written here)

Also writes:
  srijon-2.0/manifest.csv  — per-file summary for auditing

Usage:
    python3 srijon-2.0/scripts/normalize.py

Run from the repo root (cs329-group/).
The script is safe to re-run: it overwrites outputs deterministically.
"""

import csv
import os
import pathlib
import sys

import pandas as pd

# ── paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent   # cs329-group/
SRC_DATA  = REPO_ROOT / "srijon" / "data"
OUT_ROOT  = REPO_ROOT / "srijon-2.0"

# ── helpers ───────────────────────────────────────────────────────────────────

def fix_mojibake(s: str) -> str:
    """Repair UTF-8 bytes stored as Windows-1252 in Excel cells (common Excel artifact).

    Pattern: 'Ã©' -> 'é'  (UTF-8 bytes 0xC3 0xA9 stored as two cp1252 chars)
    Pattern: 'ÃŸ' -> 'ß'  (UTF-8 bytes 0xC3 0x9F; 0x9F maps to U+0178 in cp1252,
                            which is NOT representable in latin-1 — hence we use cp1252)
    """
    try:
        return s.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def fix_series(col: pd.Series) -> pd.Series:
    """Apply mojibake fix to every string in a Series."""
    return col.apply(lambda v: fix_mojibake(v) if isinstance(v, str) else v)


def make_ids(n: int, prefix: str) -> list[str]:
    """Generate zero-padded deterministic item IDs: prefix_000001, …"""
    width = max(6, len(str(n)))
    return [f"{prefix}_{str(i + 1).zfill(width)}" for i in range(n)]


def write_csv(df: pd.DataFrame, path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")


def report(msg: str) -> None:
    print(msg, flush=True)


# ── manifest accumulator ──────────────────────────────────────────────────────
manifest_rows: list[dict] = []

def record_manifest(
    *,
    original_file: str,
    task: str,
    language: str,
    source_out: str,
    inference_out: str,
    full_out: str,
    row_count: int,
    notes: str = "",
) -> None:
    manifest_rows.append(
        dict(
            original_file=original_file,
            task=task,
            language=language,
            source_out=source_out,
            inference_out=inference_out,
            full_out=full_out,
            row_count=row_count,
            notes=notes,
        )
    )


# ══════════════════════════════════════════════════════════════════════════════
# A. PRONOUN RESOLUTION
# ══════════════════════════════════════════════════════════════════════════════

def process_pronoun_resolution_english() -> None:
    """
    Source file: Pronoun Resolution English.xlsx
    Schema found: single column 'sentence' (WinoGrande sentences with '_' placeholder)
    No option columns exist in this file.
    Inference schema: item_id, sentence
    """
    src = SRC_DATA / "Pronoun Resolution English.xlsx"
    report(f"\n[PR-EN] Reading {src.name}")
    df = pd.read_excel(src, header=0)                  # column: 'sentence'
    n = len(df)
    report(f"  rows={n}, columns={list(df.columns)}")

    ids = make_ids(n, "pr_en")
    df.insert(0, "item_id", ids)

    # source — all original columns
    source_path = OUT_ROOT / "pronoun_resolution/en/source/en_master.csv"
    write_csv(df, source_path)

    # inference — model-facing: item_id + sentence
    inf_df = df[["item_id", "sentence"]].copy()
    inf_path = OUT_ROOT / "pronoun_resolution/en/inference/en_master_inference.csv"
    write_csv(inf_df, inf_path)

    # full — source + empty prediction column
    full_df = df.copy()
    full_df["model_prediction"] = ""
    full_df["correct"] = ""
    full_path = OUT_ROOT / "pronoun_resolution/en/full/en_master_full.csv"
    write_csv(full_df, full_path)

    record_manifest(
        original_file=str(src.relative_to(REPO_ROOT)),
        task="pronoun_resolution",
        language="en",
        source_out=str(source_path.relative_to(REPO_ROOT)),
        inference_out=str(inf_path.relative_to(REPO_ROOT)),
        full_out=str(full_path.relative_to(REPO_ROOT)),
        row_count=n,
        notes=(
            "WinoGrande English. Single 'sentence' column only — "
            "no option1/option2 in source file. "
            "Inference schema: item_id, sentence. "
            "Gold labels not present; model_prediction column added as placeholder."
        ),
    )
    report(f"  -> wrote source/inference/full ({n} rows)")


def process_pronoun_resolution_multilingual(lang_code: str, lang_label: str) -> None:
    """
    Source files: Pronoun Resolution {lang_label}.xlsx
    Schema: context_{lc}, option1_{lc}, option2_{lc}   (with possible trailing colon)
    Inference schema: item_id, sentence, option_a, option_b
    Encoding: mojibake repair needed for FR and DE.
    """
    src = SRC_DATA / f"Pronoun Resolution {lang_label}.xlsx"
    report(f"\n[PR-{lang_code.upper()}] Reading {src.name}")
    df = pd.read_excel(src, header=0)
    n = len(df)
    report(f"  rows={n}, columns={list(df.columns)}")

    # Strip trailing colons from column names (DE artifact)
    df.columns = [c.rstrip(":").strip() for c in df.columns]
    lc = lang_code

    # Standardise column names: context_{lc} → sentence, option1_{lc} → option_a …
    col_map = {}
    for c in df.columns:
        cl = c.lower()
        if cl.startswith("context"):
            col_map[c] = "sentence"
        elif "option1" in cl:
            col_map[c] = "option_a"
        elif "option2" in cl:
            col_map[c] = "option_b"
    df.rename(columns=col_map, inplace=True)
    report(f"  columns after rename: {list(df.columns)}")

    # Fix mojibake (FR, DE)
    if lang_code in ("fr", "de"):
        for col in ["sentence", "option_a", "option_b"]:
            if col in df.columns:
                df[col] = fix_series(df[col])

    ids = make_ids(n, f"pr_{lc}")
    df.insert(0, "item_id", ids)

    source_path   = OUT_ROOT / f"pronoun_resolution/{lc}/source/{lc}_master.csv"
    inf_path      = OUT_ROOT / f"pronoun_resolution/{lc}/inference/{lc}_master_inference.csv"
    full_path     = OUT_ROOT / f"pronoun_resolution/{lc}/full/{lc}_master_full.csv"

    write_csv(df, source_path)

    inf_cols = ["item_id", "sentence", "option_a", "option_b"]
    write_csv(df[inf_cols], inf_path)

    full_df = df.copy()
    full_df["model_prediction"] = ""
    full_df["correct"] = ""
    write_csv(full_df, full_path)

    record_manifest(
        original_file=str(src.relative_to(REPO_ROOT)),
        task="pronoun_resolution",
        language=lc,
        source_out=str(source_path.relative_to(REPO_ROOT)),
        inference_out=str(inf_path.relative_to(REPO_ROOT)),
        full_out=str(full_path.relative_to(REPO_ROOT)),
        row_count=n,
        notes=(
            f"Wino-X {lang_label}. "
            f"Columns renamed: context→sentence, option1→option_a, option2→option_b. "
            + ("Mojibake repair applied (latin-1→utf-8). " if lang_code in ("fr","de") else "")
            + "No gold labels in source. model_prediction placeholder added."
        ),
    )
    report(f"  -> wrote source/inference/full ({n} rows)")


# ══════════════════════════════════════════════════════════════════════════════
# B. PRESUPPOSITIONS
# ══════════════════════════════════════════════════════════════════════════════

def process_presuppositions(lang_code: str, lang_label: str, is_excel: bool) -> None:
    """
    Source files:
      Presuppositions English.xlsx  → columns: premise, hypothesis
      Presuppositions {lang}.csv    → columns: premise, hypothesis
    All languages share the same 2-column schema (no gold labels in source files).
    Inference schema: item_id, premise, hypothesis
    """
    if is_excel:
        src = SRC_DATA / f"Presuppositions {lang_label}.xlsx"
        report(f"\n[PS-{lang_code.upper()}] Reading {src.name}")
        df = pd.read_excel(src, header=0)
    else:
        src = SRC_DATA / f"Presuppositions {lang_label}.csv"
        report(f"\n[PS-{lang_code.upper()}] Reading {src.name}")
        df = pd.read_csv(src, encoding="utf-8")

    n = len(df)
    report(f"  rows={n}, columns={list(df.columns)}")

    # Validate expected columns
    for req in ("premise", "hypothesis"):
        if req not in df.columns:
            report(f"  WARNING: expected column '{req}' not found in {src.name}")

    ids = make_ids(n, f"ps_{lang_code}")
    df.insert(0, "item_id", ids)

    source_path = OUT_ROOT / f"presuppositions/{lang_code}/source/{lang_code}_master.csv"
    inf_path    = OUT_ROOT / f"presuppositions/{lang_code}/inference/{lang_code}_master_inference.csv"
    full_path   = OUT_ROOT / f"presuppositions/{lang_code}/full/{lang_code}_master_full.csv"

    write_csv(df, source_path)

    inf_cols = ["item_id", "premise", "hypothesis"]
    write_csv(df[inf_cols], inf_path)

    full_df = df.copy()
    full_df["gold_label"] = ""          # to be filled from XNLI / CONFER gold sets
    full_df["model_label"] = ""
    full_df["correct"] = ""
    write_csv(full_df, full_path)

    src_type = "xlsx→csv" if is_excel else "csv"
    record_manifest(
        original_file=str(src.relative_to(REPO_ROOT)),
        task="presuppositions",
        language=lang_code,
        source_out=str(source_path.relative_to(REPO_ROOT)),
        inference_out=str(inf_path.relative_to(REPO_ROOT)),
        full_out=str(full_path.relative_to(REPO_ROOT)),
        row_count=n,
        notes=(
            f"Source format: {src_type}. "
            "Columns: premise, hypothesis. "
            "No gold labels in source file — gold_label column added as placeholder. "
            "Label scheme when populated: E=Entailment, N=Neutral, C=Contradiction "
            "(XNLI: 0/1/2; CONFER: E/N/C)."
        ),
    )
    report(f"  -> wrote source/inference/full ({n} rows)")


# ══════════════════════════════════════════════════════════════════════════════
# C. LEMMATIZATION
# ══════════════════════════════════════════════════════════════════════════════

def process_lemmatization_english() -> None:
    """
    Source file: Lemmas English.xlsx
    Schema found: single column named '3rded' (first data value treated as header).
    The file contains 115,523 inflected word forms total.
    We read with header=None to recover all rows.
    Inference schema: item_id, word
    No gold lemma column exists in this file.
    """
    src = SRC_DATA / "Lemmas English.xlsx"
    report(f"\n[LM-EN] Reading {src.name}")

    # header=None so that '3rded' row 0 is not swallowed as column name
    df = pd.read_excel(src, header=None, names=["word"])
    n = len(df)
    report(f"  rows={n} (includes row that would have been misread as header)")
    report(f"  first 3 values: {list(df['word'].head(3))}")

    ids = make_ids(n, "lm_en")
    df.insert(0, "item_id", ids)

    source_path = OUT_ROOT / "lemmatization/en/source/en_master.csv"
    inf_path    = OUT_ROOT / "lemmatization/en/inference/en_master_inference.csv"
    full_path   = OUT_ROOT / "lemmatization/en/full/en_master_full.csv"

    write_csv(df, source_path)

    write_csv(df[["item_id", "word"]], inf_path)

    full_df = df.copy()
    full_df["gold_lemma"] = ""        # to be joined from UniMorph source
    full_df["model_lemma"] = ""
    full_df["correct"] = ""
    write_csv(full_df, full_path)

    record_manifest(
        original_file=str(src.relative_to(REPO_ROOT)),
        task="lemmatization",
        language="en",
        source_out=str(source_path.relative_to(REPO_ROOT)),
        inference_out=str(inf_path.relative_to(REPO_ROOT)),
        full_out=str(full_path.relative_to(REPO_ROOT)),
        row_count=n,
        notes=(
            "UniMorph English inflections. "
            "Original file had first data row ('3rded') misread as column header; "
            "fixed by reading with header=None. "
            "Single 'word' column — no gold lemma in file. "
            "gold_lemma must be joined from the full UniMorph corpus externally. "
            "model_lemma placeholder added."
        ),
    )
    report(f"  -> wrote source/inference/full ({n} rows)")


# ══════════════════════════════════════════════════════════════════════════════
# MANIFEST
# ══════════════════════════════════════════════════════════════════════════════

def write_manifest() -> None:
    manifest_path = OUT_ROOT / "manifest.csv"
    fieldnames = [
        "original_file", "task", "language",
        "source_out", "inference_out", "full_out",
        "row_count", "notes",
    ]
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest_rows)
    report(f"\n[MANIFEST] Written → {manifest_path.relative_to(REPO_ROOT)}")
    report(f"  {len(manifest_rows)} entries")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    report("=" * 70)
    report("srijon-2.0 normalization pipeline")
    report(f"  source : {SRC_DATA}")
    report(f"  output : {OUT_ROOT}")
    report("=" * 70)

    # Pronoun resolution
    process_pronoun_resolution_english()
    process_pronoun_resolution_multilingual("fr", "French")
    process_pronoun_resolution_multilingual("de", "German")
    process_pronoun_resolution_multilingual("ru", "Russian")

    # Presuppositions
    process_presuppositions("en", "English", is_excel=True)
    process_presuppositions("fr", "French",     is_excel=False)
    process_presuppositions("de", "German",     is_excel=False)
    process_presuppositions("hi", "Hindi",      is_excel=False)
    process_presuppositions("ru", "Russian",    is_excel=False)
    process_presuppositions("vi", "Vietnamese", is_excel=False)

    # Lemmatization
    process_lemmatization_english()

    # Manifest
    write_manifest()

    report("\n" + "=" * 70)
    report("Done. Summary:")
    total_rows = sum(r["row_count"] for r in manifest_rows)
    report(f"  files processed : {len(manifest_rows)}")
    report(f"  total rows      : {total_rows:,}")
    report("=" * 70)


if __name__ == "__main__":
    main()
