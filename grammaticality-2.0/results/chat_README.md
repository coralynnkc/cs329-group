CHAT 5.4 (Thinking)

| Prompt    | In-Domain Acc | In-Domain MCC | In-Domain Macro-F1 | Out-of-Domain Acc | Out-of-Domain MCC | Out-of-Domain Macro-F1 |   Avg Acc |    Avg MCC | Avg Macro-F1 |
| --------- | ------------: | ------------: | -----------------: | ----------------: | ----------------: | ---------------------: | --------: | ---------: | -----------: |
| Direct    |          0.88 |        0.7252 |             0.8621 |              0.86 |            0.6638 |                 0.8300 |      0.87 |     0.6945 |       0.8461 |
| Anchor    |      **0.89** |    **0.7453** |         **0.8726** |              0.86 |            0.6616 |                 0.8264 |     0.875 |     0.7035 |       0.8495 |
| Repair    |      **0.89** |    **0.7453** |         **0.8726** |              0.86 |            0.6638 |                 0.8300 | **0.875** | **0.7046** |   **0.8513** |
| Checklist |          0.56 |       -0.0472 |             0.4762 |          **0.90** |        **0.7615** |             **0.8760** |      0.73 |     0.3571 |       0.6761 |

| Prompt    | In-Domain F1_0 | In-Domain F1_1 | Out-of-Domain F1_0 | Out-of-Domain F1_1 |
| --------- | -------------: | -------------: | -----------------: | -----------------: |
| Direct    |         0.8125 |         0.9118 |             0.7586 |             0.9014 |
| Anchor    |     **0.8254** |     **0.9197** |             0.7500 |             0.9028 |
| Repair    |     **0.8254** |     **0.9197** |             0.7586 |             0.9014 |
| Checklist |         0.2667 |         0.6857 |         **0.8214** |         **0.9306** |


**Conclusions from comparing these prompts **
On the 100-example in-domain CoLA sample, prompt formulation had a substantial effect on Chat 5.4’s grammaticality judgments. The strongest results came from the anchor and repair prompts, which tied across all major metrics, achieving 89% accuracy, 0.745 MCC, and 0.873 macro-F1. The direct prompt also performed well, but slightly below the top tier at 88% accuracy and 0.725 MCC. In contrast, the checklist prompt performed dramatically worse, reaching only 56% accuracy and a slightly negative MCC (-0.047), indicating that this framing disrupted the model’s classification behavior rather than helping it.
Because the dataset is label-imbalanced (69 acceptable vs. 31 unacceptable), MCC and macro-F1 are more informative than accuracy alone. On those metrics, the ranking is unchanged: anchor/repair > direct >>> checklist. The top prompts also show stronger performance on the acceptable class than the unacceptable class, suggesting that future prompt improvements should focus specifically on improving recall and F1 for ungrammatical sentences.
Overall, these results suggest that for Chat 5.4, simple direct prompting is already strong, but carefully chosen prompt framing can yield modest additional gains. However, not all added structure is beneficial: the checklist-style prompt appears to overconstrain or distract the model, leading to a severe drop in performance.


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

Direct [Out of Domain]

{
  "gold_file": "mini/cola_out_of_domain_dev_sample100_answers.csv",
  "pred_file": "results/CHAT_5.4_cola_100_direct_out_of_domain_.csv",
  "data_size": 100,
  "prediction_rows_raw": 100,
  "prediction_rows_after_dedup": 100,
  "correct": 86,
  "accuracy": 0.86,
  "mcc": 0.6638,
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
  "precision_0": 0.8148,
  "recall_0": 0.7097,
  "f1_0": 0.7586,
  "precision_1": 0.8767,
  "recall_1": 0.9275,
  "f1_1": 0.9014,
  "macro_f1": 0.83,
  "tp": 64,
  "tn": 22,
  "fp": 9,
  "fn": 5,
  "class_metrics": {
    "0": {
      "tp": 22,
      "fp": 5,
      "fn": 9,
      "support": 31,
      "precision": 0.8148,
      "recall": 0.7097,
      "f1": 0.7586
    },
    "1": {
      "tp": 64,
      "fp": 9,
      "fn": 5,
      "support": 69,
      "precision": 0.8767,
      "recall": 0.9275,
      "f1": 0.9014
    }
  }
}

Anchor [Out of Domain]

{
  "gold_file": "mini/cola_out_of_domain_dev_sample100_answers.csv",
  "pred_file": "results/CHAT_5.4_cola_100_anchor_out_of_domain_.csv",
  "data_size": 100,
  "prediction_rows_raw": 100,
  "prediction_rows_after_dedup": 100,
  "correct": 86,
  "accuracy": 0.86,
  "mcc": 0.6616,
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
  "precision_0": 0.84,
  "recall_0": 0.6774,
  "f1_0": 0.75,
  "precision_1": 0.8667,
  "recall_1": 0.942,
  "f1_1": 0.9028,
  "macro_f1": 0.8264,
  "tp": 65,
  "tn": 21,
  "fp": 10,
  "fn": 4,
  "class_metrics": {
    "0": {
      "tp": 21,
      "fp": 4,
      "fn": 10,
      "support": 31,
      "precision": 0.84,
      "recall": 0.6774,
      "f1": 0.75
    },
    "1": {
      "tp": 65,
      "fp": 10,
      "fn": 4,
      "support": 69,
      "precision": 0.8667,
      "recall": 0.942,
      "f1": 0.9028
    }
  }
}

Checklist [Out of Domain]

{
  "gold_file": "mini/cola_out_of_domain_dev_sample100_answers.csv",
  "pred_file": "results/CHAT_5.4_cola_100_checklist_out_of_domain_.csv",
  "data_size": 100,
  "prediction_rows_raw": 100,
  "prediction_rows_after_dedup": 100,
  "correct": 90,
  "accuracy": 0.9,
  "mcc": 0.7615,
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
  "precision_0": 0.92,
  "recall_0": 0.7419,
  "f1_0": 0.8214,
  "precision_1": 0.8933,
  "recall_1": 0.971,
  "f1_1": 0.9306,
  "macro_f1": 0.876,
  "tp": 67,
  "tn": 23,
  "fp": 8,
  "fn": 2,
  "class_metrics": {
    "0": {
      "tp": 23,
      "fp": 2,
      "fn": 8,
      "support": 31,
      "precision": 0.92,
      "recall": 0.7419,
      "f1": 0.8214
    },
    "1": {
      "tp": 67,
      "fp": 8,
      "fn": 2,
      "support": 69,
      "precision": 0.8933,
      "recall": 0.971,
      "f1": 0.9306
    }
  }
}

Repair [Out of Domain]

{
  "gold_file": "mini/cola_out_of_domain_dev_sample100_answers.csv",
  "pred_file": "results/CHAT_5.4_cola_100_repair_out_of_domain_.csv",
  "data_size": 100,
  "prediction_rows_raw": 100,
  "prediction_rows_after_dedup": 100,
  "correct": 86,
  "accuracy": 0.86,
  "mcc": 0.6638,
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
  "precision_0": 0.8148,
  "recall_0": 0.7097,
  "f1_0": 0.7586,
  "precision_1": 0.8767,
  "recall_1": 0.9275,
  "f1_1": 0.9014,
  "macro_f1": 0.83,
  "tp": 64,
  "tn": 22,
  "fp": 9,
  "fn": 5,
  "class_metrics": {
    "0": {
      "tp": 22,
      "fp": 5,
      "fn": 9,
      "support": 31,
      "precision": 0.8148,
      "recall": 0.7097,
      "f1": 0.7586
    },
    "1": {
      "tp": 64,
      "fp": 9,
      "fn": 5,
      "support": 69,
      "precision": 0.8767,
      "recall": 0.9275,
      "f1": 0.9014
    }
  }
}

FINETUNED - IN DOMAIN

{
  "gold_file": "mini/cola_in_domain_dev_sample100_answers.csv",
  "pred_file": "results/CHAT_5.4_cola_100_finetuned.csv",
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

FINETUNED - OUT OF DOMAIN

{
  "gold_file": "mini/cola_out_of_domain_dev_sample100_answers.csv",
  "pred_file": "results/CHAT_5.4_cola_100_finetuned_out_of_domain_.csv",
  "data_size": 100,
  "prediction_rows_raw": 100,
  "prediction_rows_after_dedup": 100,
  "correct": 85,
  "accuracy": 0.85,
  "mcc": 0.6357,
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
  "precision_0": 0.8636,
  "recall_0": 0.6129,
  "f1_0": 0.717,
  "precision_1": 0.8462,
  "recall_1": 0.9565,
  "f1_1": 0.898,
  "macro_f1": 0.8075,
  "tp": 66,
  "tn": 19,
  "fp": 12,
  "fn": 3,
  "class_metrics": {
    "0": {
      "tp": 19,
      "fp": 3,
      "fn": 12,
      "support": 31,
      "precision": 0.8636,
      "recall": 0.6129,
      "f1": 0.717
    },
    "1": {
      "tp": 66,
      "fp": 12,
      "fn": 3,
      "support": 69,
      "precision": 0.8462,
      "recall": 0.9565,
      "f1": 0.898
    }
  }
}