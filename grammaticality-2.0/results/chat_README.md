CHAT 5.4 (Thinking)

100 In Dev -- Direct

{
  "gold_file": "mini/cola_in_domain_dev_sample100_answers.csv",
  "pred_file": "data/CHAT_5.4_cola_100_direct.csv",
  "data_size": 100,
  "prediction_rows_raw": 100,
  "prediction_rows_after_dedup": 100,
  "correct": 88,
  "accuracy": 0.88,
  "mcc": 0.7252,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "valid_prediction_rate": 1.0,
  "precision_0": 0.7879,
  "recall_0": 0.8387,
  "f1_0": 0.8125,
  "precision_1": 0.9254,
  "recall_1": 0.8986,
  "f1_1": 0.9118,
  "macro_f1": 0.8621,
  "tp": 62,
  "tn": 26,
  "fp": 5,
  "fn": 7,
  "class_metrics": {
    "0": {
      "tp": 26,
      "fp": 7,
      "fn": 5,
      "support": 31,
      "precision": 0.7879,
      "recall": 0.8387,
      "f1": 0.8125
    },
    "1": {
      "tp": 62,
      "fp": 5,
      "fn": 7,
      "support": 69,
      "precision": 0.9254,
      "recall": 0.8986,
      "f1": 0.9118
    }
  }
}

CHECKLIST PROMPT

{
  "gold_file": "mini/cola_in_domain_dev_sample100_answers.csv",
  "pred_file": "data/CHAT_5.4_cola_100_checklist.csv",
  "data_size": 100,
  "prediction_rows_raw": 100,
  "prediction_rows_after_dedup": 100,
  "correct": 56,
  "accuracy": 0.56,
  "mcc": -0.0472,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "valid_prediction_rate": 1.0,
  "precision_0": 0.2759,
  "recall_0": 0.2581,
  "f1_0": 0.2667,
  "precision_1": 0.6761,
  "recall_1": 0.6957,
  "f1_1": 0.6857,
  "macro_f1": 0.4762,
  "tp": 48,
  "tn": 8,
  "fp": 23,
  "fn": 21,
  "class_metrics": {
    "0": {
      "tp": 8,
      "fp": 21,
      "fn": 23,
      "support": 31,
      "precision": 0.2759,
      "recall": 0.2581,
      "f1": 0.2667
    },
    "1": {
      "tp": 48,
      "fp": 23,
      "fn": 21,
      "support": 69,
      "precision": 0.6761,
      "recall": 0.6957,
      "f1": 0.6857
    }
  }
}


ANCHOR PROMPT

{
  "gold_file": "mini/cola_in_domain_dev_sample100_answers.csv",
  "pred_file": "data/CHAT_5.4_cola_100_anchor.csv",
  "data_size": 100,
  "prediction_rows_raw": 100,
  "prediction_rows_after_dedup": 100,
  "correct": 89,
  "accuracy": 0.89,
  "mcc": 0.7453,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "valid_prediction_rate": 1.0,
  "precision_0": 0.8125,
  "recall_0": 0.8387,
  "f1_0": 0.8254,
  "precision_1": 0.9265,
  "recall_1": 0.913,
  "f1_1": 0.9197,
  "macro_f1": 0.8726,
  "tp": 63,
  "tn": 26,
  "fp": 5,
  "fn": 6,
  "class_metrics": {
    "0": {
      "tp": 26,
      "fp": 6,
      "fn": 5,
      "support": 31,
      "precision": 0.8125,
      "recall": 0.8387,
      "f1": 0.8254
    },
    "1": {
      "tp": 63,
      "fp": 5,
      "fn": 6,
      "support": 69,
      "precision": 0.9265,
      "recall": 0.913,
      "f1": 0.9197
    }
  }
}


REPAIR PROMPT

{
  "gold_file": "mini/cola_in_domain_dev_sample100_answers.csv",
  "pred_file": "data/CHAT_5.4_cola_100_repair.csv",
  "data_size": 100,
  "prediction_rows_raw": 100,
  "prediction_rows_after_dedup": 100,
  "correct": 89,
  "accuracy": 0.89,
  "mcc": 0.7453,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "valid_prediction_rate": 1.0,
  "precision_0": 0.8125,
  "recall_0": 0.8387,
  "f1_0": 0.8254,
  "precision_1": 0.9265,
  "recall_1": 0.913,
  "f1_1": 0.9197,
  "macro_f1": 0.8726,
  "tp": 63,
  "tn": 26,
  "fp": 5,
  "fn": 6,
  "class_metrics": {
    "0": {
      "tp": 26,
      "fp": 6,
      "fn": 5,
      "support": 31,
      "precision": 0.8125,
      "recall": 0.8387,
      "f1": 0.8254
    },
    "1": {
      "tp": 63,
      "fp": 5,
      "fn": 6,
      "support": 69,
      "precision": 0.9265,
      "recall": 0.913,
      "f1": 0.9197
    }
  }
}