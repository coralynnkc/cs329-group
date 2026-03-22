"""
Generate evaluation split files for the pronoun resolution benchmark.

For each language, produces:
  - {lang}_items.csv         : 50 items with full info including correct answer (for scoring)
  - {lang}_prompt_zeroshot.txt  : Condition 1 prompt (paste into LLM)
  - {lang}_prompt_fewshot.txt   : Condition 2 prompt (paste into LLM)
  - {lang}_prompt_clarified.txt : Condition 3 prompt (paste into LLM)

Design:
  - Random seed fixed for reproducibility
  - For African languages (AM/IG/ZU): same 50 source items sampled, then pulled across all 3 languages
  - Few-shot examples excluded from test pool for English/JP/ZH; they don't appear in African data anyway
  - Options in prompts show the actual text (not "1"/"2"); correct_letter in answer key maps to A/B
"""

import os
import random
import pandas as pd

SEED = 42
N = 50
OUT_DIR = "/Users/claireburkhardt/Documents/nlp_group/benchmark_winograde/eval_splits"
UNIFIED_CSV = "/Users/claireburkhardt/Documents/nlp_group/benchmark_winograde/unified_benchmark.csv"

os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Few-shot examples (fixed; from English XWinograd; excluded from EN/JP/ZH test pool)
# ---------------------------------------------------------------------------
FEW_SHOT_SENTENCES_EN = {
    "The city councilmen refused the demonstrators a permit because _ feared violence.",
    "The trophy doesn't fit into the brown suitcase because _ is too large.",
    "Joan made sure to thank Susan for all the help _ had recieved.",   # note original typo
    "Joan made sure to thank Susan for all the help _ had received.",   # just in case
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
# Load data
# ---------------------------------------------------------------------------
df = pd.read_csv(UNIFIED_CSV)
print(f"Loaded {len(df)} rows from {UNIFIED_CSV}")
print(df["language"].value_counts().to_string())

# ---------------------------------------------------------------------------
# Helper: correct_answer ("1" or "2") → letter ("A" or "B")
# ---------------------------------------------------------------------------
def answer_to_letter(correct_answer):
    return "A" if str(correct_answer).strip() == "1" else "B"

# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------
def build_zeroshot_prompt(items_df, lang):
    lines = ["Fill in the blank for each sentence below. Just give me the number and your answer.", ""]
    for i, (_, row) in enumerate(items_df.iterrows(), 1):
        lines.append(f"{i}. {row['sentence_with_blank']}")
        lines.append(f"Options: {row['option1']}, {row['option2']}")
        lines.append("")
    return "\n".join(lines)


def build_fewshot_prompt(items_df, lang):
    lines = [
        "Fill in the blank for each sentence. Here are some examples:",
        "",
    ]
    for ex in FEW_SHOT_EXAMPLES:
        lines.append(f"Sentence: {ex['sentence']}")
        lines.append(f"Options: {ex['option1']}, {ex['option2']}")
        lines.append(f"Answer: {ex['answer']}")
        lines.append("")
    lines.append("Now do the same for these:")
    lines.append("")
    for i, (_, row) in enumerate(items_df.iterrows(), 1):
        lines.append(f"{i}. {row['sentence_with_blank']}")
        lines.append(f"Options: {row['option1']}, {row['option2']}")
        lines.append("")
    return "\n".join(lines)


def build_clarified_prompt(items_df, lang):
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
    for i, (_, row) in enumerate(items_df.iterrows(), 1):
        lines.append(f"{i}. {row['sentence_with_blank']}")
        lines.append(f"A) {row['option1']}")
        lines.append(f"B) {row['option2']}")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Sample and generate for XWinograd languages (EN, JP, ZH)
# ---------------------------------------------------------------------------
XWINO_LANGUAGES = ["English", "Japanese", "Chinese"]
LANG_CODES = {
    "English": "en",
    "Japanese": "jp",
    "Chinese": "zh",
    "Amharic":  "am",
    "Igbo":     "ig",
    "Zulu":     "zu",
}

random.seed(SEED)

for lang in XWINO_LANGUAGES:
    lang_df = df[df["language"] == lang].copy().reset_index(drop=True)

    # Exclude few-shot examples (only relevant for English; JP/ZH won't match anyway)
    pool = lang_df[~lang_df["sentence_with_blank"].isin(FEW_SHOT_SENTENCES_EN)].copy().reset_index(drop=True)

    sampled_idx = sorted(random.sample(range(len(pool)), N))
    sampled = pool.iloc[sampled_idx].copy().reset_index(drop=True)
    sampled.index = range(1, N + 1)  # 1-based item numbers

    code = LANG_CODES[lang]

    # Answer key CSV (includes everything)
    answer_key = pd.DataFrame({
        "item_num":     range(1, N + 1),
        "sentence":     sampled["sentence_with_blank"].values,
        "option1":      sampled["option1"].values,
        "option2":      sampled["option2"].values,
        "correct_answer_num": sampled["correct_answer"].values,
        "correct_letter": [answer_to_letter(a) for a in sampled["correct_answer"].values],
        "correct_text": [
            row["option1"] if str(row["correct_answer"]).strip() == "1" else row["option2"]
            for _, row in sampled.iterrows()
        ],
    })
    ak_path = os.path.join(OUT_DIR, f"{code}_answer_key.csv")
    answer_key.to_csv(ak_path, index=False)
    print(f"\n{lang}: answer key → {ak_path}")

    # Prompt files
    for condition, builder in [
        ("zeroshot",  build_zeroshot_prompt),
        ("fewshot",   build_fewshot_prompt),
        ("clarified", build_clarified_prompt),
    ]:
        prompt_text = builder(sampled, lang)
        p_path = os.path.join(OUT_DIR, f"{code}_prompt_{condition}.txt")
        with open(p_path, "w", encoding="utf-8") as f:
            f.write(prompt_text)
        print(f"  {condition} → {p_path}")

# ---------------------------------------------------------------------------
# Sample for African languages — align by qID (source_id) since row order differs
# ---------------------------------------------------------------------------

am_df = df[df["language"] == "Amharic"].copy()
ig_df = df[df["language"] == "Igbo"].copy()
zu_df = df[df["language"] == "Zulu"].copy()

# Find qIDs present in all three languages
common_ids = set(am_df["source_id"]) & set(ig_df["source_id"]) & set(zu_df["source_id"])
print(f"\nAfrican languages: {len(common_ids)} qIDs common across AM/IG/ZU")

random.seed(SEED)
sampled_ids = sorted(random.sample(sorted(common_ids), N))
print(f"  Sampled {N} qIDs. First 3: {sampled_ids[:3]}")

# Index each language df by source_id for fast lookup
am_idx = am_df.set_index("source_id")
ig_idx = ig_df.set_index("source_id")
zu_idx = zu_df.set_index("source_id")

AFR_INDEXED = {"Amharic": am_idx, "Igbo": ig_idx, "Zulu": zu_idx}

for lang, lang_indexed in AFR_INDEXED.items():
    sampled = lang_indexed.loc[sampled_ids].copy().reset_index()
    sampled.index = range(1, N + 1)
    code = LANG_CODES[lang]

    answer_key = pd.DataFrame({
        "item_num":     range(1, N + 1),
        "sentence":     sampled["sentence_with_blank"].values,
        "option1":      sampled["option1"].values,
        "option2":      sampled["option2"].values,
        "correct_answer_num": sampled["correct_answer"].values,
        "correct_letter": [answer_to_letter(a) for a in sampled["correct_answer"].values],
        "correct_text": [
            row["option1"] if str(row["correct_answer"]).strip() == "1" else row["option2"]
            for _, row in sampled.iterrows()
        ],
    })
    ak_path = os.path.join(OUT_DIR, f"{code}_answer_key.csv")
    answer_key.to_csv(ak_path, index=False)
    print(f"\n{lang}: answer key → {ak_path}")

    for condition, builder in [
        ("zeroshot",  build_zeroshot_prompt),
        ("fewshot",   build_fewshot_prompt),
        ("clarified", build_clarified_prompt),
    ]:
        prompt_text = builder(sampled, lang)
        p_path = os.path.join(OUT_DIR, f"{code}_prompt_{condition}.txt")
        with open(p_path, "w", encoding="utf-8") as f:
            f.write(prompt_text)
        print(f"  {condition} → {p_path}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n=== Files generated ===")
for f in sorted(os.listdir(OUT_DIR)):
    print(f"  {f}")
