import csv
import sys

def parse_conllu_to_csv(input_path, output_path):
    rows = []

    with open(input_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Skip comments and blank lines
            if line.startswith("#") or line == "":
                continue

            cols = line.split("\t")

            # Skip MWE range rows (1-2) and empty nodes (1.1)
            token_id = cols[0]
            if "-" in token_id or "." in token_id:
                continue

            # Guard against malformed lines
            if len(cols) < 3:
                continue

            form  = cols[1]
            lemma = cols[2]

            # Skip tokens with no lemma
            if lemma == "_":
                continue

            rows.append((form, lemma))

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["form", "lemma"])  # header
        writer.writerows(rows)

    print(f"Done. {len(rows)} tokens written to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_lemmas.py input.conllu output.csv")
        sys.exit(1)

    parse_conllu_to_csv(sys.argv[1], sys.argv[2])