"""
Build unified pronoun-resolution benchmark dataset.

Steps:
1. Download XWinograd (EN, JP, ZH) and African WinoGrande (AM, IG, ZU)
2. Filter African WinoGrande to pronoun-only items using English source
3. Normalize to unified schema
4. Save results + print counts
"""

import re
import pandas as pd
from datasets import load_dataset

# ---------------------------------------------------------------------------
# Unified schema columns
# ---------------------------------------------------------------------------
COLS = ["language", "sentence_with_blank", "option1", "option2", "correct_answer", "source_dataset"]

# ---------------------------------------------------------------------------
# 1. XWinograd — EN, JA, ZH
# ---------------------------------------------------------------------------
# Format: sentence (with _ blank), option1, option2, answer (1 or 2)

XWINO_LANGS = {
    "en": "English",
    "jp": "Japanese",
    "zh": "Chinese",
}

xwino_frames = []

print("=== Downloading XWinograd ===")
for code, lang_name in XWINO_LANGS.items():
    print(f"  Loading {lang_name} ({code})...")
    ds = load_dataset("Muennighoff/xwinograd", code, split="test")
    df = ds.to_pandas()
    print(f"    Raw rows: {len(df)}  |  columns: {list(df.columns)}")
    # Normalise
    out = pd.DataFrame({
        "language": lang_name,
        "sentence_with_blank": df["sentence"],
        "option1": df["option1"],
        "option2": df["option2"],
        "correct_answer": df["answer"].astype(str),
        "source_id": "",   # XWinograd has no cross-language qID
        "source_dataset": "xwinograd",
    })
    xwino_frames.append(out)
    print(f"    Kept rows: {len(out)}")

xwino_df = pd.concat(xwino_frames, ignore_index=True)
print(f"\nXWinograd total: {len(xwino_df)}\n")

# ---------------------------------------------------------------------------
# 2. African WinoGrande — AM, IG, ZU  (pronoun filtering via English source)
# ---------------------------------------------------------------------------
# Dataset: Institute-Disease-Modeling/mmlu-winogrande-afr
# We need to figure out exact config names — let's inspect first.

print("=== Inspecting African WinoGrande dataset structure ===")
try:
    from datasets import get_dataset_config_names
    afr_configs = get_dataset_config_names("Institute-Disease-Modeling/mmlu-winogrande-afr")
    print(f"  Available configs: {afr_configs}")
except Exception as e:
    print(f"  Could not list configs: {e}")
    afr_configs = []

# ---------------------------------------------------------------------------
# 2a. Load English WinoGrande source to identify pronoun items
# ---------------------------------------------------------------------------
print("\n=== English WinoGrande will be loaded per-split for pronoun filtering (see below) ===")

# ---------------------------------------------------------------------------
# 2b. Pronoun filter heuristic
# ---------------------------------------------------------------------------
# WinoGrande sentences look like:  "The garage is bigger than the backyard because _ is renovated."
# Pronoun blanks: the _ is NOT immediately preceded by a determiner/article.
# Noun blanks:    the _ IS immediately preceded by "the", "a", "an", "The", "A", "An".
#
# More specifically, after tokenising on whitespace we check the token just before "_".
# Determiners: the, a, an (case-insensitive). Also possessive endings ('s) suggest noun.
#
# Secondary check: both options should be pronouns for the item to count.
# English pronouns (common in WinoGrande): he, she, they, it, him, her, them, his, hers, their, theirs
# If EITHER option is a pronoun, keep the item.

ENGLISH_PRONOUNS = {
    "he", "she", "they", "it", "him", "her", "them",
    "his", "hers", "their", "theirs", "himself", "herself",
    "themselves", "itself", "i", "me", "my", "mine", "we",
    "us", "our", "ours", "you", "your", "yours"
}

DETERMINERS = {"the", "a", "an"}


def token_before_blank(sentence: str) -> str:
    """Return the whitespace token immediately before '_' (lowercased)."""
    tokens = sentence.split()
    for i, tok in enumerate(tokens):
        if "_" in tok:  # handles "_" alone or "_." etc.
            if i > 0:
                # strip punctuation from preceding token
                return re.sub(r"[^a-zA-Z']+", "", tokens[i - 1]).lower()
            return ""
    return ""


def has_determiner_before_blank(sentence: str) -> bool:
    return token_before_blank(sentence) in DETERMINERS


def option_is_pronoun(option: str) -> bool:
    return option.strip().lower().rstrip(".,!?;:") in ENGLISH_PRONOUNS


def is_pronoun_item(row) -> bool:
    """True if this WinoGrande item is a pronoun-resolution item."""
    sentence = row["sentence"]
    opt1 = str(row.get("option1", ""))
    opt2 = str(row.get("option2", ""))

    # Primary: options are pronouns
    opts_are_pronouns = option_is_pronoun(opt1) or option_is_pronoun(opt2)
    # Secondary: no determiner immediately before blank
    no_det = not has_determiner_before_blank(sentence)

    return opts_are_pronouns or no_det


# ---------------------------------------------------------------------------
# 2b. Build per-split pronoun filter indices (alignment is by row index per split)
#
#  African split  |  English source
#  ─────────────────────────────────
#  train_s (640)  |  winogrande_s  train  (640)
#  dev     (1267) |  winogrande_xl validation (1267)
#  test    (1767) |  winogrande_xl test       (1767)
# ---------------------------------------------------------------------------

print("\n=== Building per-split pronoun filter indices ===")

EN_SPLIT_MAP = {
    # afr_split : (en_config, en_split)
    "train_s": ("winogrande_s",  "train"),
    "dev":     ("winogrande_xl", "validation"),
    "test":    ("winogrande_xl", "test"),
}

pronoun_indices_per_split = {}   # afr_split -> set of integer positions to keep

for afr_split, (en_config, en_split) in EN_SPLIT_MAP.items():
    print(f"\n  Loading English {en_config}/{en_split} ...")
    en_ds = load_dataset("winogrande", en_config, split=en_split)
    en_split_df = en_ds.to_pandas()
    mask = en_split_df.apply(is_pronoun_item, axis=1)
    keep_positions = sorted(mask[mask].index.tolist())
    pronoun_indices_per_split[afr_split] = keep_positions
    print(f"    {en_split}: {len(keep_positions)}/{len(en_split_df)} pronoun items ({100*len(keep_positions)/len(en_split_df):.1f}%)")

# Show heuristic quality on English train sample
en_xl_val = load_dataset("winogrande", "winogrande_xl", split="validation").to_pandas()
mask_xl = en_xl_val.apply(is_pronoun_item, axis=1)
print("\nSample pronoun items (English val):")
print(en_xl_val[mask_xl][["sentence","option1","option2"]].head(5).to_string())
print("\nSample noun items filtered out (English val):")
print(en_xl_val[~mask_xl][["sentence","option1","option2"]].head(5).to_string())

# ---------------------------------------------------------------------------
# 2c. Load African WinoGrande and filter by per-split pronoun indices
# ---------------------------------------------------------------------------
AFR_LANGS = {
    "winogrande_am": "Amharic",
    "winogrande_ig": "Igbo",
    "winogrande_zu": "Zulu",
}

afr_frames = []

print("\n=== Downloading African WinoGrande ===")
for config, lang_name in AFR_LANGS.items():
    print(f"\n  Loading {lang_name} ({config})...")
    lang_parts = []
    total_raw = 0

    for afr_split, keep_positions in pronoun_indices_per_split.items():
        ds = load_dataset("Institute-Disease-Modeling/mmlu-winogrande-afr", config, split=afr_split)
        df = ds.to_pandas()
        total_raw += len(df)
        df_filtered = df.iloc[keep_positions].copy().reset_index(drop=True)
        lang_parts.append(df_filtered)
        print(f"    {afr_split}: {len(df_filtered)}/{len(df)} rows kept")

    df_all = pd.concat(lang_parts, ignore_index=True)
    print(f"    Total raw: {total_raw}  |  After filter: {len(df_all)}")
    print(df_all.head(3).to_string())

    out = pd.DataFrame({
        "language": lang_name,
        "sentence_with_blank": df_all["Sentence"],
        "option1": df_all["Option1"],
        "option2": df_all["Option2"],
        "correct_answer": df_all["Answer"].astype(str),
        "source_dataset": "african_winogrande",
        "source_id": df_all["qID"].values,          # shared across languages for alignment
    })
    afr_frames.append(out)
    print(f"    Final rows added: {len(out)}")

# ---------------------------------------------------------------------------
# 3. Combine and save
# ---------------------------------------------------------------------------
print("\n=== Building unified dataset ===")

all_frames = [xwino_df]
if afr_frames:
    afr_df = pd.concat(afr_frames, ignore_index=True)
    all_frames.append(afr_df)

unified = pd.concat(all_frames, ignore_index=True)

print("\n--- Row counts by language ---")
print(unified["language"].value_counts().to_string())

print(f"\nTotal rows: {len(unified)}")
print(f"Columns: {list(unified.columns)}")
print("\nSample rows:")
print(unified.head(5).to_string())

# Save
out_path = "/Users/claireburkhardt/Documents/nlp_group/benchmark_winograde/unified_benchmark.csv"
unified.to_csv(out_path, index=False)
print(f"\nSaved to: {out_path}")
