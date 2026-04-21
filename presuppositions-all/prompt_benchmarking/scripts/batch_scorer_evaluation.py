#!/usr/bin/env python3

import argparse
import csv
import io
import json
import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

LANGUAGES = ["de", "vi", "fr", "ru", "hi", "en"]
GOLD_LABELS = ["E", "N", "C"]
PROB_COLS = ["e_probability", "n_probability", "c_probability"]
LABEL_TO_COL = {
    "E": "e_probability",
    "N": "n_probability",
    "C": "c_probability",
}
COL_TO_LABEL = {
    "e_probability": "E",
    "n_probability": "N",
    "c_probability": "C",
}
NO_VALID_PRED = "__NO_VALID_PRED__"


def safe_div(num: float, denom: float) -> float:
    return num / denom if denom else 0.0


def round_or_none(value: Optional[float], digits: int = 4) -> Optional[float]:
    if value is None:
        return None
    return round(float(value), digits)


def normalize_header(name: str) -> str:
    return str(name).strip().lower().replace("\ufeff", "")


def extract_language_code(filename: str) -> Optional[str]:
    filename_lower = filename.lower()
    for lang in LANGUAGES:
        if re.search(rf"(?<![a-z]){lang}(?![a-z])", filename_lower):
            return lang
    return None


def parse_regular_csv(path: Path) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"{path.name} has no header row")
        rows = []
        for row in reader:
            normalized = {
                normalize_header(k): (v.strip() if isinstance(v, str) else v)
                for k, v in row.items()
            }
            rows.append(normalized)
        return rows


def parse_quoted_csv(path: Path) -> List[Dict[str, str]]:
    raw = path.read_text(encoding="utf-8-sig").strip()
    lines = raw.splitlines()
    cleaned = []
    for line in lines:
        line = line.strip()
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        cleaned.append(line)

    buffer = io.StringIO("\n".join(cleaned))
    reader = csv.DictReader(buffer)
    if reader.fieldnames is None:
        raise ValueError(f"{path.name} has no header row")
    rows = []
    for row in reader:
        normalized = {
            normalize_header(k): (v.strip() if isinstance(v, str) else v)
            for k, v in row.items()
        }
        rows.append(normalized)
    return rows


def read_gold(path: Path) -> List[Dict[str, str]]:
    rows = parse_regular_csv(path)

    required = {"item_id", "gold_label"}
    if not rows:
        return []

    header_keys = set(rows[0].keys())
    missing = required - header_keys
    if missing:
        raise ValueError(
            f"Gold file {path.name} is missing required columns: {sorted(missing)}. "
            f"Found columns: {sorted(header_keys)}"
        )

    cleaned = []
    for row in rows:
        item_id = str(row["item_id"]).strip()
        gold_label = str(row["gold_label"]).strip().upper()
        if gold_label not in GOLD_LABELS:
            raise ValueError(
                f"Gold file {path.name} contains unexpected label {gold_label!r}. "
                f"Expected one of {GOLD_LABELS}."
            )
        cleaned.append({"item_id": item_id, "gold_label": gold_label})

    return cleaned


def read_pred(path: Path) -> List[Dict[str, str]]:
    rows = []
    try:
        rows = parse_regular_csv(path)
        if rows and {"item_id", *PROB_COLS}.issubset(set(rows[0].keys())):
            return rows
    except Exception:
        pass

    rows = parse_quoted_csv(path)
    if rows and {"item_id", *PROB_COLS}.issubset(set(rows[0].keys())):
        return rows

    found_cols = sorted(rows[0].keys()) if rows else []
    raise ValueError(
        f"Prediction file {path.name} is missing required columns: {PROB_COLS}. "
        f"Found columns: {found_cols}"
    )


def dedup_predictions(pred_rows: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], int]:
    seen = set()
    deduped = []
    duplicate_count = 0

    for row in pred_rows:
        item_id = str(row.get("item_id", "")).strip()
        if item_id in seen:
            duplicate_count += 1
            continue
        seen.add(item_id)
        deduped.append(row)

    return deduped, duplicate_count


def parse_float(value) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_probability_row(row: Dict[str, str]) -> Dict[str, object]:
    probs = {col: parse_float(row.get(col)) for col in PROB_COLS}

    is_missing = all(v is None for v in probs.values())
    has_any_nan = any(v is None for v in probs.values())
    has_out_of_range = any((v is not None and (v < 0 or v > 1)) for v in probs.values())

    raw_sum = None if has_any_nan else sum(probs.values())

    is_valid = (
        (not is_missing)
        and (not has_any_nan)
        and (not has_out_of_range)
        and raw_sum is not None
        and raw_sum > 0
    )

    normalized_probs = {}
    pred_label = None

    if is_valid:
        for col in PROB_COLS:
            normalized_probs[col] = probs[col] / raw_sum
        pred_label = COL_TO_LABEL[max(normalized_probs, key=normalized_probs.get)]
    else:
        for col in PROB_COLS:
            normalized_probs[col] = probs[col]

    return {
        "item_id": str(row.get("item_id", "")).strip(),
        "is_missing": is_missing,
        "has_any_nan_prob": has_any_nan,
        "has_out_of_range_prob": has_out_of_range,
        "prob_sum_raw": raw_sum,
        "is_valid_probability_row": is_valid,
        "pred_label": pred_label,
        "pred_for_metrics": pred_label if pred_label in GOLD_LABELS else NO_VALID_PRED,
        **normalized_probs,
    }


def compute_one_vs_rest_metrics(y_true: List[str], y_pred: List[str], label: str) -> Dict[str, float]:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)
    support = sum(1 for t in y_true if t == label)

    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn)
    f1 = safe_div(2 * precision * recall, precision + recall)

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "support": support,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def compute_multiclass_log_loss(rows: List[Dict[str, object]], eps: float = 1e-15) -> Optional[float]:
    if not rows:
        return None

    losses = []
    for row in rows:
        gold = row["gold_label"]
        true_prob = row[LABEL_TO_COL[gold]]
        true_prob = min(max(float(true_prob), eps), 1.0 - eps)
        losses.append(-math.log(true_prob))

    return sum(losses) / len(losses)


def compute_multiclass_brier_score(rows: List[Dict[str, object]]) -> Optional[float]:
    if not rows:
        return None

    row_scores = []
    for row in rows:
        gold = row["gold_label"]
        score = 0.0
        for label, col in LABEL_TO_COL.items():
            y = 1.0 if gold == label else 0.0
            p = float(row[col])
            score += (p - y) ** 2
        row_scores.append(score)

    return sum(row_scores) / len(row_scores)


def compute_centroids(rows: List[Dict[str, object]]) -> Dict[str, Dict[str, Optional[float]]]:
    by_gold = {}
    for label in GOLD_LABELS:
        subset = [row for row in rows if row["gold_label"] == label]
        if not subset:
            by_gold[label] = {
                "count": 0,
                "avg_e_probability": None,
                "avg_n_probability": None,
                "avg_c_probability": None,
            }
            continue

        by_gold[label] = {
            "count": len(subset),
            "avg_e_probability": sum(float(row["e_probability"]) for row in subset) / len(subset),
            "avg_n_probability": sum(float(row["n_probability"]) for row in subset) / len(subset),
            "avg_c_probability": sum(float(row["c_probability"]) for row in subset) / len(subset),
        }
    return by_gold


def vector_from_row(row: Dict[str, object]) -> Tuple[float, float, float]:
    return (
        float(row["e_probability"]),
        float(row["n_probability"]),
        float(row["c_probability"]),
    )


def vector_from_centroid(centroid: Dict[str, Optional[float]]) -> Optional[Tuple[float, float, float]]:
    if centroid["avg_e_probability"] is None:
        return None
    return (
        float(centroid["avg_e_probability"]),
        float(centroid["avg_n_probability"]),
        float(centroid["avg_c_probability"]),
    )


def euclidean_distance(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def compute_centroid_diagnostics(rows: List[Dict[str, object]]) -> Dict[str, object]:
    if not rows:
        return {
            "centroid_method": "within-run class centroids computed from valid probability rows",
            "centroid_note": "Descriptive diagnostic of cluster structure, not a primary evaluation metric.",
            "nearest_centroid_accuracy": None,
            "avg_distance_to_gold_centroid": None,
            "avg_distance_to_predicted_centroid": None,
            "avg_margin_gold_vs_best_other": None,
            "centroid_confusion": {},
        }

    centroids = compute_centroids(rows)
    centroid_vectors = {
        label: vector_from_centroid(centroid)
        for label, centroid in centroids.items()
    }

    confusion = {gold: {pred: 0 for pred in GOLD_LABELS} for gold in GOLD_LABELS}
    nearest_correct = 0
    distances_to_gold = []
    distances_to_nearest = []
    margins = []

    for row in rows:
        row_vec = vector_from_row(row)
        dists = {}
        for label in GOLD_LABELS:
            centroid_vec = centroid_vectors[label]
            if centroid_vec is None:
                continue
            dists[label] = euclidean_distance(row_vec, centroid_vec)

        if not dists:
            continue

        nearest_label = min(dists, key=dists.get)
        gold_label = row["gold_label"]
        confusion[gold_label][nearest_label] += 1
        if nearest_label == gold_label:
            nearest_correct += 1

        gold_dist = dists[gold_label]
        best_other = min(dist for label, dist in dists.items() if label != gold_label)
        distances_to_gold.append(gold_dist)
        distances_to_nearest.append(dists[nearest_label])
        margins.append(best_other - gold_dist)

    return {
        "centroid_method": "within-run class centroids computed from valid probability rows",
        "centroid_note": (
            "Measures how tightly each gold class clusters in probability space and whether an item sits closest "
            "to the centroid of its own gold class. Useful as a descriptive geometry/separability diagnostic, "
            "but not a substitute for accuracy, F1, log loss, or Brier score."
        ),
        "nearest_centroid_accuracy": safe_div(nearest_correct, len(rows)),
        "avg_distance_to_gold_centroid": sum(distances_to_gold) / len(distances_to_gold) if distances_to_gold else None,
        "avg_distance_to_predicted_centroid": sum(distances_to_nearest) / len(distances_to_nearest) if distances_to_nearest else None,
        "avg_margin_gold_vs_best_other": sum(margins) / len(margins) if margins else None,
        "centroid_confusion": confusion,
    }


def merge_gold_and_pred(gold_rows: List[Dict[str, str]], pred_rows: List[Dict[str, str]]) -> List[Dict[str, object]]:
    pred_map = {}
    for row in pred_rows:
        pred_map[str(row.get("item_id", "")).strip()] = row

    merged = []
    for gold in gold_rows:
        item_id = gold["item_id"]
        pred_row = pred_map.get(item_id, {"item_id": item_id})
        pred_info = normalize_probability_row(pred_row)
        merged.append({
            "item_id": item_id,
            "gold_label": gold["gold_label"],
            **pred_info,
        })

    return merged


def score_pair(gold_path: Path, pred_path: Path) -> dict:
    gold_rows = read_gold(gold_path)
    pred_rows_raw = read_pred(pred_path)

    pred_rows_after_dedup, duplicate_prediction_rows = dedup_predictions(pred_rows_raw)

    gold_ids = {row["item_id"] for row in gold_rows}
    pred_ids = {str(row.get("item_id", "")).strip() for row in pred_rows_after_dedup}
    extra_prediction_ids = sorted(pred_ids - gold_ids)
    missing_prediction_ids = sorted(gold_ids - pred_ids)

    merged = merge_gold_and_pred(gold_rows, pred_rows_after_dedup)

    data_size = len(gold_rows)
    missing_predictions = sum(1 for row in merged if row["is_missing"])
    invalid_predictions = sum(
        1 for row in merged if (not row["is_missing"]) and (not row["is_valid_probability_row"])
    )
    scored_rows = [row for row in merged if row["is_valid_probability_row"]]
    correct = sum(1 for row in merged if row["pred_label"] == row["gold_label"])

    accuracy = safe_div(correct, data_size)
    missing_rate = safe_div(missing_predictions, data_size)
    invalid_rate = safe_div(invalid_predictions, data_size)
    coverage = safe_div(data_size - missing_predictions, data_size)
    valid_prediction_rate = safe_div(len(scored_rows), data_size)

    y_true = [row["gold_label"] for row in merged]
    y_pred = [row["pred_for_metrics"] for row in merged]

    class_metrics = {
        label: compute_one_vs_rest_metrics(y_true, y_pred, label)
        for label in GOLD_LABELS
    }
    macro_f1 = sum(class_metrics[label]["f1"] for label in GOLD_LABELS) / len(GOLD_LABELS)

    log_loss = compute_multiclass_log_loss(scored_rows)
    multiclass_brier = compute_multiclass_brier_score(scored_rows)

    by_gold_raw = compute_centroids(scored_rows)
    by_gold = {
        label: {
            "count": stats["count"],
            "avg_e_probability": round_or_none(stats["avg_e_probability"]),
            "avg_n_probability": round_or_none(stats["avg_n_probability"]),
            "avg_c_probability": round_or_none(stats["avg_c_probability"]),
        }
        for label, stats in by_gold_raw.items()
    }

    centroid_diag_raw = compute_centroid_diagnostics(scored_rows)
    centroid_diag = {
        "centroid_method": centroid_diag_raw["centroid_method"],
        "centroid_note": centroid_diag_raw["centroid_note"],
        "nearest_centroid_accuracy": round_or_none(centroid_diag_raw["nearest_centroid_accuracy"]),
        "avg_distance_to_gold_centroid": round_or_none(centroid_diag_raw["avg_distance_to_gold_centroid"]),
        "avg_distance_to_predicted_centroid": round_or_none(centroid_diag_raw["avg_distance_to_predicted_centroid"]),
        "avg_margin_gold_vs_best_other": round_or_none(centroid_diag_raw["avg_margin_gold_vs_best_other"]),
        "centroid_confusion": centroid_diag_raw["centroid_confusion"],
    }

    return {
        "gold_file": gold_path.name,
        "pred_file": pred_path.name,
        "data_size": data_size,
        "prediction_rows_raw": len(pred_rows_raw),
        "prediction_rows_after_dedup": len(pred_rows_after_dedup),
        "correct": correct,
        "accuracy": round_or_none(accuracy),
        "missing_predictions": missing_predictions,
        "missing_rate": round_or_none(missing_rate),
        "invalid_predictions": invalid_predictions,
        "invalid_rate": round_or_none(invalid_rate),
        "duplicate_prediction_rows": duplicate_prediction_rows,
        "extra_prediction_ids": len(extra_prediction_ids),
        "extra_prediction_id_examples": extra_prediction_ids[:10],
        "missing_prediction_id_examples": missing_prediction_ids[:10],
        "coverage": round_or_none(coverage),
        "valid_prediction_rate": round_or_none(valid_prediction_rate),
        "scored_rows_for_probability_metrics": len(scored_rows),
        "macro_f1": round_or_none(macro_f1),
        "log_loss": round_or_none(log_loss),
        "multiclass_brier_score": round_or_none(multiclass_brier),
        "precision_E": round_or_none(class_metrics["E"]["precision"]),
        "recall_E": round_or_none(class_metrics["E"]["recall"]),
        "f1_E": round_or_none(class_metrics["E"]["f1"]),
        "precision_N": round_or_none(class_metrics["N"]["precision"]),
        "recall_N": round_or_none(class_metrics["N"]["recall"]),
        "f1_N": round_or_none(class_metrics["N"]["f1"]),
        "precision_C": round_or_none(class_metrics["C"]["precision"]),
        "recall_C": round_or_none(class_metrics["C"]["recall"]),
        "f1_C": round_or_none(class_metrics["C"]["f1"]),
        "class_metrics": {
            label: {
                "tp": class_metrics[label]["tp"],
                "fp": class_metrics[label]["fp"],
                "fn": class_metrics[label]["fn"],
                "support": class_metrics[label]["support"],
                "precision": round_or_none(class_metrics[label]["precision"]),
                "recall": round_or_none(class_metrics[label]["recall"]),
                "f1": round_or_none(class_metrics[label]["f1"]),
            }
            for label in GOLD_LABELS
        },
        "avg_probabilities_by_gold_label": by_gold,
        "centroid_diagnostics": centroid_diag,
    }


def choose_gold_file_for_language(presup_dir: Path, lang: str) -> Path:
    full_dir = presup_dir / lang / "full"
    if not full_dir.exists():
        raise ValueError(f"Missing expected gold directory: {full_dir}")

    gold_files = sorted(full_dir.glob("*.csv"))
    if not gold_files:
        raise ValueError(f"No gold CSV files found in {full_dir}")

    exact_candidates = [p for p in gold_files if p.name.lower() == f"{lang}_sample100_full.csv"]
    if len(exact_candidates) == 1:
        return exact_candidates[0]
    if len(exact_candidates) > 1:
        raise ValueError(f"Multiple exact gold matches found for language {lang}: {[p.name for p in exact_candidates]}")

    preferred = [p for p in gold_files if "sample100" in p.name.lower() and "full" in p.name.lower()]
    if len(preferred) == 1:
        return preferred[0]
    if len(preferred) > 1:
        raise ValueError(
            f"Ambiguous gold file for language {lang}. Multiple sample100/full candidates found: "
            f"{[p.name for p in preferred]}"
        )

    full_candidates = [p for p in gold_files if "full" in p.name.lower()]
    if len(full_candidates) == 1:
        return full_candidates[0]
    if len(full_candidates) > 1:
        raise ValueError(
            f"Ambiguous gold file for language {lang}. Multiple full candidates found: "
            f"{[p.name for p in full_candidates]}"
        )

    raise ValueError(
        f"Could not determine a single gold file for language {lang}. Found: {[p.name for p in gold_files]}"
    )


def validate_prediction_file_language(pred_file: Path, lang: str) -> None:
    detected = extract_language_code(pred_file.name)
    if detected != lang:
        raise ValueError(
            f"Prediction file {pred_file.name} does not cleanly match expected language {lang!r}; "
            f"detected {detected!r}."
        )


def find_matching_files(presup_dir: Path, results_dir: Path) -> List[Tuple[Path, Path, str]]:
    matches = []
    pred_files = sorted(results_dir.glob("*.csv"))

    if not pred_files:
        raise ValueError(f"No prediction CSV files found in {results_dir}")

    for pred_file in pred_files:
        lang = extract_language_code(pred_file.name)
        if not lang:
            raise ValueError(
                f"Could not infer language from prediction filename: {pred_file.name}. "
                f"Expected one of {LANGUAGES} to appear as a standalone code."
            )
        validate_prediction_file_language(pred_file, lang)
        gold_file = choose_gold_file_for_language(presup_dir, lang)
        matches.append((gold_file, pred_file, lang))

    return matches


def print_result_summary(result: dict) -> None:
    print(
        f"  accuracy={result['accuracy']} | "
        f"macro_f1={result['macro_f1']} | "
        f"log_loss={result['log_loss']} | "
        f"multiclass_brier_score={result['multiclass_brier_score']}"
    )
    print(
        f"  nearest_centroid_accuracy={result['centroid_diagnostics']['nearest_centroid_accuracy']} | "
        f"avg_distance_to_gold_centroid={result['centroid_diagnostics']['avg_distance_to_gold_centroid']} | "
        f"avg_margin_gold_vs_best_other={result['centroid_diagnostics']['avg_margin_gold_vs_best_other']}"
    )
    print(
        f"  matched={result['data_size'] - result['missing_predictions']}/{result['data_size']} | "
        f"missing={result['missing_predictions']} | invalid={result['invalid_predictions']} | "
        f"extra_pred_ids={result['extra_prediction_ids']} | duplicate_pred_rows={result['duplicate_prediction_rows']}"
    )

    for lbl, stats in result["avg_probabilities_by_gold_label"].items():
        if stats["count"] > 0:
            print(
                f"    Gold={lbl} (n={stats['count']}): "
                f"avg_E={stats['avg_e_probability']}, "
                f"avg_N={stats['avg_n_probability']}, "
                f"avg_C={stats['avg_c_probability']}"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Strict batch scorer for presupposition probability outputs."
    )
    parser.add_argument(
        "--presup-dir",
        required=True,
        help="Path to presuppositions root directory.",
    )
    parser.add_argument(
        "--results",
        required=True,
        help="Path to results directory containing prediction CSVs.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to save JSON output.",
    )
    args = parser.parse_args()

    presup_dir = Path(args.presup_dir)
    results_dir = Path(args.results)

    if not presup_dir.exists():
        raise ValueError(f"Presuppositions directory does not exist: {presup_dir}")
    if not results_dir.exists():
        raise ValueError(f"Results directory does not exist: {results_dir}")

    matches = find_matching_files(presup_dir, results_dir)

    print(f"Found {len(matches)} file pairs to process:")
    for gold_file, pred_file, lang in matches:
        print(f"  [{lang}] {gold_file.name} <-> {pred_file.name}")
    print()

    all_results = {}

    for gold_file, pred_file, lang in matches:
        print(f"Processing: {pred_file.name}")
        try:
            result = score_pair(gold_file, pred_file)
            all_results[pred_file.name] = result
            print_result_summary(result)
        except Exception as e:
            print(f"  ✗ Error: {e}")
            all_results[pred_file.name] = {"error": str(e)}
        print()

    output_data = {
        "summary": {
            "total_files_processed": len(matches),
            "successful": sum(1 for v in all_results.values() if "error" not in v),
            "failed": sum(1 for v in all_results.values() if "error" in v),
        },
        "results": all_results,
    }

    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(json.dumps(output_data, indent=2, ensure_ascii=False))

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
