"""
Generate master-list CSVs for every language using all filtered items
(not a random N=100 sample).

Source:  data/filtered_tight/{en,am,ig,zu}.csv
Output:  benchmark_winograde/master_lists/{en,am,ig,zu}_master.csv

English  — all rows with a valid answer (drops the winogrande_xl/test rows
           that have no ground-truth label).
African  — all rows whose qID appears in every one of AM / IG / ZU
           (same alignment rule as the eval splits).

Fixes the answer_to_letter bug from generate_eval_splits_tight.py:
  answer column is float (1.0/2.0) when read back from CSV, so the old
  str(val) == "1" check always failed → every item was labeled "B".
"""

import os
import pandas as pd

DATA_DIR = "/Users/claireburkhardt/Documents/nlp_group/data/filtered_tight"
OUT_DIR  = "/Users/claireburkhardt/Documents/nlp_group/benchmark_winograde/master_lists"

os.makedirs(OUT_DIR, exist_ok=True)


def answer_to_letter(val):
    """Return 'A' for option-1 answers, 'B' for option-2. Handles float or string."""
    try:
        return "A" if int(float(val)) == 1 else "B"
    except (ValueError, TypeError):
        return ""


def build_master(df, item_col="sentence"):
    out = pd.DataFrame({
        "item_num":           range(1, len(df) + 1),
        "sentence":           df[item_col].values,
        "option1":            df["option1"].values,
        "option2":            df["option2"].values,
        "correct_answer_num": df["answer"].values,
        "correct_letter":     [answer_to_letter(a) for a in df["answer"].values],
        "correct_text": [
            row["option1"] if answer_to_letter(row["answer"]) == "A" else row["option2"]
            for _, row in df.iterrows()
        ],
    })
    return out


# ---------------------------------------------------------------------------
# English
# ---------------------------------------------------------------------------
en_df = pd.read_csv(os.path.join(DATA_DIR, "en.csv"))
en_valid = en_df[en_df["answer"].notna()].copy().reset_index(drop=True)

en_master = build_master(en_valid)
en_path = os.path.join(OUT_DIR, "en_master.csv")
en_master.to_csv(en_path, index=False)
print(f"English : {len(en_master):>5} items  (dropped {len(en_df) - len(en_valid)} unlabeled test-split rows)")

# ---------------------------------------------------------------------------
# African — align by shared qID across all three languages
# ---------------------------------------------------------------------------
am_df = pd.read_csv(os.path.join(DATA_DIR, "am.csv"))
ig_df = pd.read_csv(os.path.join(DATA_DIR, "ig.csv"))
zu_df = pd.read_csv(os.path.join(DATA_DIR, "zu.csv"))

common_ids = sorted(set(am_df["id"]) & set(ig_df["id"]) & set(zu_df["id"]))
print(f"\nAfrican : {len(common_ids)} qIDs shared across AM / IG / ZU")

for code, df in [("am", am_df), ("ig", ig_df), ("zu", zu_df)]:
    sampled = df[df["id"].isin(common_ids)].copy().reset_index(drop=True)
    master  = build_master(sampled)
    path    = os.path.join(OUT_DIR, f"{code}_master.csv")
    master.to_csv(path, index=False)
    print(f"  {code.upper()}    : {len(master):>5} items")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print(f"\nFiles written to {OUT_DIR}/")
for f in sorted(os.listdir(OUT_DIR)):
    n = len(pd.read_csv(os.path.join(OUT_DIR, f)))
    print(f"  {f:<25}  {n} rows")
