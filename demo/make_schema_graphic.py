"""
Plain database-schema style graphic for the Narnia NER label schema.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AGENCY_ROWS = [
    ("ACTIVE_SPEAKER",   "Character is speaking or attributed to dialogue"),
    ("ACTIVE_PERFORMER", "Character performs a physical action"),
    ("ACTIVE_THOUGHT",   "Character thinks, feels, or has an internal state"),
    ("ADDRESSED",        "Character is spoken to or directly addressed"),
    ("MENTIONED_ONLY",   "Mentioned by narrator with no agency"),
    ("MISCELLANEOUS",    "Group/species label or role that doesn't fit above"),
]

CANONICAL_ROWS = [
    ("Lucy Pevensie",         "Lucy · Lu · Daughter of Eve (→ Lucy)"),
    ("Peter Pevensie",        "Peter · Son of Adam (→ Peter)"),
    ("Susan Pevensie",        "Susan · Su"),
    ("Edmund Pevensie",       "Edmund · Ed · Son of Adam (→ Edmund)"),
    ("Mrs. Pevensie",         "Mother"),
    ("Mr. Tumnus",            "Tumnus · Faun · the Faun"),
    ("Jadis",                 "the White Witch · the Queen · Her Imperial Majesty"),
    ("Aslan",                 "the Lion"),
    ("Prof. Digory Kirke",    "Professor · Professor Kirke"),
    ("Mrs. Macready",         "Mrs. Macready"),
    ("Father Christmas",      "Father Christmas"),
]

fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(16, 6))
fig.subplots_adjust(left=0.02, right=0.98, top=0.88, bottom=0.04, wspace=0.12)

for ax in (ax_l, ax_r):
    ax.axis("off")

def plain_table(ax, rows, col_labels, title):
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10, loc="left")
    tbl = ax.table(
        cellText=rows,
        colLabels=col_labels,
        loc="center",
        cellLoc="left",
        bbox=[0, 0, 1, 1],
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(11)
    tbl.auto_set_column_width([0, 1])

    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor("#cccccc")
        cell.set_linewidth(0.8)
        cell.set_facecolor("white")
        if row == 0:
            cell.set_text_props(fontweight="bold", color="#333333")
        else:
            if col == 0:
                cell.set_text_props(fontfamily="monospace", color="#111111", fontsize=10)
            else:
                cell.set_text_props(color="#444444")

plain_table(ax_l, AGENCY_ROWS,   ["Label", "Definition"],              "Agency Labels")
plain_table(ax_r, CANONICAL_ROWS, ["Canonical Name", "Surface Forms"],  "Canonical Characters")

out = "demo/narnia_schema.png"
plt.savefig(out, dpi=180, bbox_inches="tight", facecolor="white")
print(f"Saved → {out}")
