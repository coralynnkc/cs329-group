"""
Tight pronoun-resolution filter applied to English WinoGrande source data.

Four criteria (all must pass):
  C1: No determiner immediately before blank (rejects noun-fill items)
  C2: Both options are proper names (start uppercase) or pronouns
  C3: Both options appear in the text BEFORE the blank (both are antecedents)
  C4: Blank is preceded within 3 tokens by a discourse connective

English filter is applied first; surviving qIDs are used to pull
Amharic, Igbo, and Zulu translations.

Output: data/filtered_tight/{en,am,ig,zu}.csv
"""

import re
import os
import pandas as pd
from datasets import load_dataset

OUT_DIR = "/Users/claireburkhardt/Documents/nlp_group/data/filtered_tight"
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DETERMINERS = {"the", "a", "an"}

PRONOUNS = {
    "he", "she", "they", "it", "him", "her", "them",
    "his", "hers", "their", "theirs", "himself", "herself",
    "themselves", "itself",
}

CONNECTIVES = {
    "because", "so", "but", "since", "although", "when",
    "after", "before", "and", "yet", "while", "if",
    "until", "though", "as",
}

# ---------------------------------------------------------------------------
# Criterion helpers
# ---------------------------------------------------------------------------

def _token_before_blank(sentence: str) -> str:
    """Lowercased word token immediately before the blank."""
    tokens = sentence.split()
    for i, tok in enumerate(tokens):
        if "_" in tok:
            if i > 0:
                return re.sub(r"[^a-z']+", "", tokens[i - 1].lower())
            return ""
    return ""


def c1_no_determiner_before_blank(sentence: str) -> bool:
    return _token_before_blank(sentence) not in DETERMINERS


def c2_both_options_animate(opt1: str, opt2: str) -> bool:
    """Both options start with uppercase OR are pronouns."""
    def qualifies(opt):
        o = opt.strip()
        if not o:
            return False
        return o[0].isupper() or o.lower().rstrip(".,") in PRONOUNS
    return qualifies(opt1) and qualifies(opt2)


def c3_both_options_before_blank(sentence: str, opt1: str, opt2: str) -> bool:
    """Both options (case-insensitive, possessive-tolerant) appear BEFORE the blank."""
    if "_" not in sentence:
        return False
    before = sentence[: sentence.index("_")].lower()

    def found(opt):
        o = opt.strip().lower()
        # direct substring match
        if o in before:
            return True
        # option appears with possessive suffix in the text
        if o + "'s" in before:
            return True
        # option is a possessive form itself — strip 's and check
        o_base = re.sub(r"'s$", "", o)
        if o_base and o_base in before:
            return True
        return False

    return found(opt1) and found(opt2)


def c4_blank_follows_connective(sentence: str) -> bool:
    """A discourse connective appears within 3 tokens before the blank."""
    if "_" not in sentence:
        return False
    before = sentence[: sentence.index("_")]
    tokens = before.split()
    # Take the last 3 tokens; strip punctuation for matching
    recent = tokens[-3:] if len(tokens) >= 3 else tokens
    cleaned = [re.sub(r"[^a-z]", "", t.lower()) for t in recent]
    return any(t in CONNECTIVES for t in cleaned)


def passes_all(row) -> bool:
    s, o1, o2 = row["sentence"], str(row["option1"]), str(row["option2"])
    return (
        c1_no_determiner_before_blank(s)
        and c2_both_options_animate(o1, o2)
        and c3_both_options_before_blank(s, o1, o2)
        and c4_blank_follows_connective(s)
    )

# ---------------------------------------------------------------------------
# Load all English WinoGrande source splits and combine
# ---------------------------------------------------------------------------
EN_SPLITS = [
    ("winogrande_s",  "train"),
    ("winogrande_xl", "validation"),
    ("winogrande_xl", "test"),
]

print("=== Loading English WinoGrande ===")
en_parts = []
for cfg, spl in EN_SPLITS:
    ds = load_dataset("winogrande", cfg, split=spl)
    df = ds.to_pandas()
    df["_split"] = f"{cfg}/{spl}"
    en_parts.append(df)
    print(f"  {cfg}/{spl}: {len(df)} rows")

en_df = pd.concat(en_parts, ignore_index=True)
print(f"Total English rows: {len(en_df)}")

# ---------------------------------------------------------------------------
# Apply each criterion individually, then all four combined
# ---------------------------------------------------------------------------
print("\n=== Per-criterion survival counts ===")
masks = {}
masks["C1_no_det"]        = en_df["sentence"].apply(c1_no_determiner_before_blank)
masks["C2_animate"]       = en_df.apply(lambda r: c2_both_options_animate(str(r["option1"]), str(r["option2"])), axis=1)
masks["C3_both_before"]   = en_df.apply(lambda r: c3_both_options_before_blank(r["sentence"], str(r["option1"]), str(r["option2"])), axis=1)
masks["C4_connective"]    = en_df["sentence"].apply(c4_blank_follows_connective)
masks["ALL_FOUR"]         = masks["C1_no_det"] & masks["C2_animate"] & masks["C3_both_before"] & masks["C4_connective"]

for name, mask in masks.items():
    n = mask.sum()
    pct = 100 * n / len(en_df)
    print(f"  {name:20s}: {n:5d} / {len(en_df)}  ({pct:.1f}%)")

# ---------------------------------------------------------------------------
# Flag if outside expected range
# ---------------------------------------------------------------------------
n_survivors = masks["ALL_FOUR"].sum()
if n_survivors < 500:
    print(f"\n⚠️  WARNING: only {n_survivors} items survived — fewer than expected (500–2000). Check filter logic.")
elif n_survivors > 2000:
    print(f"\n⚠️  WARNING: {n_survivors} items survived — more than expected (500–2000). Filter may be too loose.")
else:
    print(f"\n✓ {n_survivors} items survived all four criteria (within expected range 500–2000).")

# ---------------------------------------------------------------------------
# Surviving English items
# ---------------------------------------------------------------------------
en_tight = en_df[masks["ALL_FOUR"]].copy().reset_index(drop=True)

print("\n=== 10 items that PASS all four criteria ===")
print(en_tight[["sentence", "option1", "option2", "answer"]].head(10).to_string())

# ---------------------------------------------------------------------------
# Items that passed OLD filter (C1 only) but fail NEW filter
# ---------------------------------------------------------------------------
old_filter_mask = masks["C1_no_det"]  # old = just no-determiner
old_only = en_df[old_filter_mask & ~masks["ALL_FOUR"]].copy().reset_index(drop=True)

print("\n=== 5 items in OLD filter but removed by NEW (showing why) ===")
for i, row in old_only.head(5).iterrows():
    s, o1, o2 = row["sentence"], str(row["option1"]), str(row["option2"])
    reasons = []
    if not c2_both_options_animate(o1, o2):
        reasons.append(f"C2 fail: options='{o1}'/'{o2}' not both animate")
    if not c3_both_options_before_blank(s, o1, o2):
        reasons.append(f"C3 fail: not both options found before blank")
    if not c4_blank_follows_connective(s):
        reasons.append(f"C4 fail: no connective within 3 tokens before blank")
    print(f"\n  Sentence : {s}")
    print(f"  Options  : {o1} / {o2}")
    print(f"  Removed  : {'; '.join(reasons)}")

# ---------------------------------------------------------------------------
# Save English tight CSV
# ---------------------------------------------------------------------------
en_out = pd.DataFrame({
    "id":             en_tight.apply(lambda r: f"{r['_split']}_{r.name}", axis=1),
    "language":       "English",
    "sentence":       en_tight["sentence"],
    "option1":        en_tight["option1"],
    "option2":        en_tight["option2"],
    "answer":         en_tight["answer"],
    "source_dataset": "winogrande_tight",
})
en_path = os.path.join(OUT_DIR, "en.csv")
en_out.to_csv(en_path, index=False)
print(f"\nSaved English tight: {en_path}  ({len(en_out)} rows)")

# ---------------------------------------------------------------------------
# Load African languages and pull matching rows by qID
# ---------------------------------------------------------------------------
AFR_SPLIT_MAP = {
    # afr_split : (en_config, en_split_label_used_above)
    "train_s": "winogrande_s/train",
    "dev":     "winogrande_xl/validation",
    "test":    "winogrande_xl/test",
}

# Build a set of (split_label, row_position) for surviving English rows
# We need to map back from en_tight to split + position
en_df["_pos"] = en_df.groupby("_split").cumcount()  # 0-based position within each split
surviving_per_split = (
    en_df[masks["ALL_FOUR"]][["_split", "_pos"]]
    .groupby("_split")["_pos"]
    .apply(set)
    .to_dict()
)
for spl, positions in surviving_per_split.items():
    print(f"  Surviving in {spl}: {len(positions)} rows")

AFR_CONFIGS = {
    "winogrande_am": "Amharic",
    "winogrande_ig": "Igbo",
    "winogrande_zu": "Zulu",
}
AFR_LANG_CODES = {"Amharic": "am", "Igbo": "ig", "Zulu": "zu"}

print("\n=== Loading and filtering African languages ===")

# First collect all African data with qIDs so we can align
# For each split, load all three African languages and keep rows at surviving positions
afr_by_lang = {lang: [] for lang in AFR_CONFIGS.values()}

for afr_split, en_split_label in AFR_SPLIT_MAP.items():
    if en_split_label not in surviving_per_split:
        continue
    keep_positions = sorted(surviving_per_split[en_split_label])

    for afr_config, lang_name in AFR_CONFIGS.items():
        ds = load_dataset(
            "Institute-Disease-Modeling/mmlu-winogrande-afr",
            afr_config,
            split=afr_split,
        )
        df = ds.to_pandas()
        df_filtered = df.iloc[keep_positions].copy()
        df_filtered["_afr_split"] = afr_split
        afr_by_lang[lang_name].append(df_filtered)
        print(f"  {lang_name} {afr_split}: {len(df_filtered)}/{len(df)} rows kept")

for lang_name, parts in afr_by_lang.items():
    lang_df = pd.concat(parts, ignore_index=True)
    out = pd.DataFrame({
        "id":             lang_df["qID"],
        "language":       lang_name,
        "sentence":       lang_df["Sentence"],
        "option1":        lang_df["Option1"],
        "option2":        lang_df["Option2"],
        "answer":         lang_df["Answer"].astype(str),
        "source_dataset": "winogrande_tight",
    })
    code = AFR_LANG_CODES[lang_name]
    path = os.path.join(OUT_DIR, f"{code}.csv")
    out.to_csv(path, index=False)
    print(f"  Saved {lang_name}: {path}  ({len(out)} rows)")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n=== Files in output directory ===")
for f in sorted(os.listdir(OUT_DIR)):
    rows = len(pd.read_csv(os.path.join(OUT_DIR, f)))
    print(f"  {f}  ({rows} rows)")
