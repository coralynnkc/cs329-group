"""
Generate evaluation split files from the tight-filtered benchmark.

Source: data/filtered_tight/{en,am,ig,zu}.csv
Output: benchmark_winograde/eval_splits_tight/

Per language:
  {lang}_answer_key.csv        — 100 items with correct_letter (A/B) and correct_text
  {lang}_prompt_zeroshot.txt   — Condition 1 prompt
  {lang}_prompt_fewshot.txt    — Condition 2 prompt
  {lang}_prompt_clarified.txt  — Condition 3 prompt

African languages (AM/IG/ZU) are aligned via shared qID so item N is the
same source sentence across all three languages.
"""

import os
import random
import pandas as pd

SEED = 42
N = 100
DATA_DIR = "/Users/claireburkhardt/Documents/nlp_group/data/filtered_tight"
OUT_DIR  = "/Users/claireburkhardt/Documents/nlp_group/benchmark_winograde/eval_splits_tight"

os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Few-shot examples (from original Winograd Schema / XWinograd — won't appear
# in WinoGrande-based tight data, but we still exclude by sentence string)
# ---------------------------------------------------------------------------
FEW_SHOT_SENTENCES = {
    "The city councilmen refused the demonstrators a permit because _ feared violence.",
    "The trophy doesn't fit into the brown suitcase because _ is too large.",
    "Joan made sure to thank Susan for all the help _ had recieved.",
    "Joan made sure to thank Susan for all the help _ had received.",
}

FEW_SHOT_EXAMPLES = [
    {
        "sentence": "The city councilmen refused the demonstrators a permit because _ feared violence.",
        "option1":  "The city councilmen",
        "option2":  "The demonstrators",
        "answer":   "The city councilmen",
    },
    {
        "sentence": "The trophy doesn't fit into the brown suitcase because _ is too large.",
        "option1":  "The trophy",
        "option2":  "suitcase",
        "answer":   "The trophy",
    },
    {
        "sentence": "Joan made sure to thank Susan for all the help _ had received.",
        "option1":  "Joan",
        "option2":  "Susan",
        "answer":   "Joan",
    },
]

# ---------------------------------------------------------------------------
# Load tight-filtered CSVs
# ---------------------------------------------------------------------------
en_df = pd.read_csv(os.path.join(DATA_DIR, "en.csv"))
am_df = pd.read_csv(os.path.join(DATA_DIR, "am.csv"))
ig_df = pd.read_csv(os.path.join(DATA_DIR, "ig.csv"))
zu_df = pd.read_csv(os.path.join(DATA_DIR, "zu.csv"))

print("Loaded tight-filtered data:")
for name, df in [("English", en_df), ("Amharic", am_df), ("Igbo", ig_df), ("Zulu", zu_df)]:
    print(f"  {name}: {len(df)} rows")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def answer_to_letter(val):
    """Return 'A' for option-1 answers, 'B' for option-2.
    Handles floats (1.0/2.0) that arise when pandas reads numeric CSVs."""
    try:
        return "A" if int(float(val)) == 1 else "B"
    except (ValueError, TypeError):
        return ""


def build_answer_key(sampled, item_col="sentence"):
    return pd.DataFrame({
        "item_num":          range(1, len(sampled) + 1),
        "sentence":          sampled[item_col].values,
        "option1":           sampled["option1"].values,
        "option2":           sampled["option2"].values,
        "correct_answer_num": sampled["answer"].values,
        "correct_letter":    [answer_to_letter(a) for a in sampled["answer"].values],
        "correct_text": [
            row["option1"] if answer_to_letter(row["answer"]) == "A" else row["option2"]
            for _, row in sampled.iterrows()
        ],
    })


def build_zeroshot(sampled, item_col="sentence"):
    lines = ["Fill in the blank for each sentence below. Just give me the number and your answer.", ""]
    for i, (_, row) in enumerate(sampled.iterrows(), 1):
        lines.append(f"{i}. {row[item_col]}")
        lines.append(f"Options: {row['option1']}, {row['option2']}")
        lines.append("")
    return "\n".join(lines)


def build_fewshot(sampled, item_col="sentence"):
    lines = ["Fill in the blank for each sentence. Here are some examples:", ""]
    for ex in FEW_SHOT_EXAMPLES:
        lines.append(f"Sentence: {ex['sentence']}")
        lines.append(f"Options: {ex['option1']}, {ex['option2']}")
        lines.append(f"Answer: {ex['answer']}")
        lines.append("")
    lines.append("Now do the same for these:")
    lines.append("")
    for i, (_, row) in enumerate(sampled.iterrows(), 1):
        lines.append(f"{i}. {row[item_col]}")
        lines.append(f"Options: {row['option1']}, {row['option2']}")
        lines.append("")
    return "\n".join(lines)


def build_clarified(sampled, item_col="sentence"):
    lines = [
        "You are performing a pronoun resolution task. In each sentence below, the blank (_) represents "
        "a pronoun that has been removed. Your job is to determine which of the two provided options "
        "the pronoun originally referred to.",
        "",
        "Use commonsense reasoning about the context to decide which entity is the correct referent "
        "of the missing pronoun.",
        "",
        "For each item, respond with ONLY the number and the letter (A or B). Do not explain your reasoning.",
        "",
    ]
    for i, (_, row) in enumerate(sampled.iterrows(), 1):
        lines.append(f"{i}. {row[item_col]}")
        lines.append(f"A) {row['option1']}")
        lines.append(f"B) {row['option2']}")
        lines.append("")
    return "\n".join(lines)


def write_splits(code, sampled, item_col="sentence"):
    ak = build_answer_key(sampled, item_col)
    ak.to_csv(os.path.join(OUT_DIR, f"{code}_answer_key.csv"), index=False)

    for condition, builder in [
        ("zeroshot",  build_zeroshot),
        ("fewshot",   build_fewshot),
        ("clarified", build_clarified),
    ]:
        text = builder(sampled, item_col)
        with open(os.path.join(OUT_DIR, f"{code}_prompt_{condition}.txt"), "w", encoding="utf-8") as f:
            f.write(text)
    print(f"  {code}: {len(sampled)} items written")

# ---------------------------------------------------------------------------
# English — sample N from tight-filtered set (WinoGrande source)
# ---------------------------------------------------------------------------
random.seed(SEED)
# Exclude few-shot sentences and rows with no answer label (winogrande_xl/test
# labels are withheld by AllenAI — 811 rows dropped, 826 labeled items remain).
en_pool = en_df[
    en_df["answer"].notna() &
    ~en_df["sentence"].isin(FEW_SHOT_SENTENCES)
].copy().reset_index(drop=True)
en_idx  = sorted(random.sample(range(len(en_pool)), N))
en_sampled = en_pool.iloc[en_idx].copy().reset_index(drop=True)

print(f"\nEnglish: sampled {len(en_sampled)} from {len(en_pool)} (pool after few-shot exclusion)")
write_splits("en", en_sampled, item_col="sentence")

# ---------------------------------------------------------------------------
# African languages — align by shared qID across AM/IG/ZU
# ---------------------------------------------------------------------------
common_ids = sorted(set(am_df["id"]) & set(ig_df["id"]) & set(zu_df["id"]))
print(f"\nAfrican: {len(common_ids)} qIDs common across AM/IG/ZU")

random.seed(SEED)
sampled_ids = sorted(random.sample(common_ids, N))

am_idx_map = am_df.set_index("id")
ig_idx_map = ig_df.set_index("id")
zu_idx_map = zu_df.set_index("id")

for code, lang_map in [("am", am_idx_map), ("ig", ig_idx_map), ("zu", zu_idx_map)]:
    sampled = lang_map.loc[sampled_ids].copy().reset_index()
    sampled = sampled.reset_index(drop=True)
    write_splits(code, sampled, item_col="sentence")

# ---------------------------------------------------------------------------
# Verify African item 1 is the same source sentence across all three languages
# ---------------------------------------------------------------------------
print("\n=== Alignment check: item 1 across AM/IG/ZU ===")
for code, lang_map in [("am", am_idx_map), ("ig", ig_idx_map), ("zu", zu_idx_map)]:
    row = lang_map.loc[sampled_ids[0]]
    print(f"  {code}: {row['sentence'][:80]}  (opt: {row['option1']} / {row['option2']})")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print(f"\n=== Files written to {OUT_DIR} ===")
for f in sorted(os.listdir(OUT_DIR)):
    print(f"  {f}")
