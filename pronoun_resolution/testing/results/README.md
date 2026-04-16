**SONNET 4.6**

*Prompt 0*

| Language    |   N |  Accuracy |  Macro-F1 |    F1 (A) |    F1 (B) | Refusal Rate | Coverage |
| ----------- | --: | --------: | --------: | --------: | --------: | -----------: | -------: |
| **English** | 100 | **0.870** | **0.869** |     0.860 | **0.879** |        0.000 |    1.000 |
| **Amharic** |  90 | **0.778** | **0.777** |     0.762 | **0.792** |        0.000 |    1.000 |
| **Igbo**    |  90 | **0.578** | **0.578** |     0.578 | **0.578** |        0.000 |    1.000 |
| **Zulu**    |  90 | **0.556** | **0.558** | **0.571** |     0.546 |        0.011 |    1.000 |

| Language    | Precision (A) | Recall (A) | Precision (B) | Recall (B) |
| ----------- | ------------: | ---------: | ------------: | ---------: |
| **English** |     **0.930** |      0.800 |         0.825 |  **0.940** |
| **Amharic** |     **0.781** |      0.744 |         0.776 |  **0.809** |
| **Igbo**    |         0.553 |  **0.605** |     **0.605** |      0.553 |
| **Zulu**    |     **0.684** |      0.491 |         0.471 |  **0.649** |


EN DEV P0
{
  "gold_file": "pronoun_resolution/testing/en/full/en_dev_full.csv",
  "pred_file": "pronoun_resolution/testing/results/sonnet_4.6_dev_en_p0.csv",
  "data_size": 100,
  "prediction_rows_raw": 100,
  "prediction_rows_after_dedup": 100,
  "correct": 87,
  "accuracy": 0.87,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.9302,
  "recall_A": 0.8,
  "f1_A": 0.8602,
  "precision_B": 0.8246,
  "recall_B": 0.94,
  "f1_B": 0.8785,
  "macro_f1": 0.8694,
  "class_metrics": {
    "A": {
      "tp": 40,
      "fp": 3,
      "fn": 10,
      "support": 50,
      "precision": 0.9302,
      "recall": 0.8,
      "f1": 0.8602
    },
    "B": {
      "tp": 47,
      "fp": 10,
      "fn": 3,
      "support": 50,
      "precision": 0.8246,
      "recall": 0.94,
      "f1": 0.8785
    }
  }
}

AM DEV P0

      "f1": 0.8602
    },
    "B": {
      "tp": 47,
      "fp": 10,
      "fn": 3,
      "support": 50,
      "precision": 0.8246,
      "recall": 0.94,
      "f1": 0.8785
    }
  }
}
➜  cs329-group git:(main) ✗ /usr/bin/python3 /Users/claireburkhardt/Documents/cs329-group/pronoun_resolution/testing/scripts/cli_scorer_updated.py --gold pronoun_resolution/testing/am/full/am_dev_full.csv --pred pronoun_resolution/testing/results/sonnet_4.6_dev_am_p0.csv
{
  "gold_file": "pronoun_resolution/testing/am/full/am_dev_full.csv",
  "pred_file": "pronoun_resolution/testing/results/sonnet_4.6_dev_am_p0.csv",
  "data_size": 90,
  "prediction_rows_raw": 90,
  "prediction_rows_after_dedup": 90,
  "correct": 70,
  "accuracy": 0.7778,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.7805,
  "recall_A": 0.7442,
  "f1_A": 0.7619,
  "precision_B": 0.7755,
  "recall_B": 0.8085,
  "f1_B": 0.7917,
  "macro_f1": 0.7768,
  "class_metrics": {
    "A": {
      "tp": 32,
      "fp": 9,
      "fn": 11,
      "support": 43,
      "precision": 0.7805,
      "recall": 0.7442,
      "f1": 0.7619
    },
    "B": {
      "tp": 38,
      "fp": 11,
      "fn": 9,
      "support": 47,
      "precision": 0.7755,
      "recall": 0.8085,
      "f1": 0.7917
    }
  }
}

IG DEV P0

{
  "gold_file": "pronoun_resolution/testing/ig/full/ig_dev_full.csv",
  "pred_file": "pronoun_resolution/testing/results/sonnet_4.6_dev_ig_p0.csv",
  "data_size": 90,
  "prediction_rows_raw": 90,
  "prediction_rows_after_dedup": 90,
  "correct": 52,
  "accuracy": 0.5778,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.5532,
  "recall_A": 0.6047,
  "f1_A": 0.5778,
  "precision_B": 0.6047,
  "recall_B": 0.5532,
  "f1_B": 0.5778,
  "macro_f1": 0.5778,
  "class_metrics": {
    "A": {
      "tp": 26,
      "fp": 21,
      "fn": 17,
      "support": 43,
      "precision": 0.5532,
      "recall": 0.6047,
      "f1": 0.5778
    },
    "B": {
      "tp": 26,
      "fp": 17,
      "fn": 21,
      "support": 47,
      "precision": 0.6047,
      "recall": 0.5532,
      "f1": 0.5778
    }
  }
}

ZU DEV PO

{
  "gold_file": "pronoun_resolution/testing/zu/full/zu_dev_full.csv",
  "pred_file": "pronoun_resolution/testing/results/sonnet_4.6_dev_zu_p0.csv",
  "data_size": 90,
  "prediction_rows_raw": 90,
  "prediction_rows_after_dedup": 90,
  "correct": 50,
  "accuracy": 0.5556,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 1,
  "refusal_rate": 0.0111,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.6842,
  "recall_A": 0.4906,
  "f1_A": 0.5714,
  "precision_B": 0.4706,
  "recall_B": 0.6486,
  "f1_B": 0.5455,
  "macro_f1": 0.5584,
  "class_metrics": {
    "A": {
      "tp": 26,
      "fp": 12,
      "fn": 27,
      "support": 53,
      "precision": 0.6842,
      "recall": 0.4906,
      "f1": 0.5714
    },
    "B": {
      "tp": 24,
      "fp": 27,
      "fn": 13,
      "support": 37,
      "precision": 0.4706,
      "recall": 0.6486,
      "f1": 0.5455
    }
  }
}


*Prompt 1*

EN DEV P1

{
  "gold_file": "pronoun_resolution/testing/en/full/en_dev_full.csv",
  "pred_file": "pronoun_resolution/testing/results/sonnet_4.6_dev_en_p1.csv",
  "data_size": 100,
  "prediction_rows_raw": 100,
  "prediction_rows_after_dedup": 100,
  "correct": 91,
  "accuracy": 0.91,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.9184,
  "recall_A": 0.9,
  "f1_A": 0.9091,
  "precision_B": 0.902,
  "recall_B": 0.92,
  "f1_B": 0.9109,
  "macro_f1": 0.91,
  "class_metrics": {
    "A": {
      "tp": 45,
      "fp": 4,
      "fn": 5,
      "support": 50,
      "precision": 0.9184,
      "recall": 0.9,
      "f1": 0.9091
    },
    "B": {
      "tp": 46,
      "fp": 5,
      "fn": 4,
      "support": 50,
      "precision": 0.902,
      "recall": 0.92,
      "f1": 0.9109
    }
  }
}

AM DEV P1

{
  "gold_file": "pronoun_resolution/testing/am/full/am_dev_full.csv",
  "pred_file": "pronoun_resolution/testing/results/sonnet_4.6_dev_am_p1.csv",
  "data_size": 90,
  "prediction_rows_raw": 90,
  "prediction_rows_after_dedup": 90,
  "correct": 67,
  "accuracy": 0.7444,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.7381,
  "recall_A": 0.7209,
  "f1_A": 0.7294,
  "precision_B": 0.75,
  "recall_B": 0.766,
  "f1_B": 0.7579,
  "macro_f1": 0.7437,
  "class_metrics": {
    "A": {
      "tp": 31,
      "fp": 11,
      "fn": 12,
      "support": 43,
      "precision": 0.7381,
      "recall": 0.7209,
      "f1": 0.7294
    },
    "B": {
      "tp": 36,
      "fp": 12,
      "fn": 11,
      "support": 47,
      "precision": 0.75,
      "recall": 0.766,
      "f1": 0.7579
    }
  }
}

IG DEV P1

  "data_size": 90,
  "prediction_rows_raw": 90,
  "prediction_rows_after_dedup": 90,
  "correct": 51,
  "accuracy": 0.5667,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.5526,
  "recall_A": 0.4884,
  "f1_A": 0.5185,
  "precision_B": 0.5769,
  "recall_B": 0.6383,
  "f1_B": 0.6061,
  "macro_f1": 0.5623,
  "class_metrics": {
    "A": {
      "tp": 21,
      "fp": 17,
      "fn": 22,
      "support": 43,
      "precision": 0.5526,
      "recall": 0.4884,
      "f1": 0.5185
    },
    "B": {
      "tp": 30,
      "fp": 22,
      "fn": 17,
      "support": 47,
      "precision": 0.5769,
      "recall": 0.6383,
      "f1": 0.6061
    }
  }
}

ZU DEV P1

    "pred_file": "pronoun_resolution/testing/results/sonnet_4.6_dev_zu_p1.csv",
  "data_size": 90,
  "prediction_rows_raw": 90,
  "prediction_rows_after_dedup": 90,
  "correct": 54,
  "accuracy": 0.6,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.7297,
  "recall_A": 0.5094,
  "f1_A": 0.6,
  "precision_B": 0.5094,
  "recall_B": 0.7297,
  "f1_B": 0.6,
  "macro_f1": 0.6,
  "class_metrics": {
    "A": {
      "tp": 27,
      "fp": 10,
      "fn": 26,
      "support": 53,
      "precision": 0.7297,
      "recall": 0.5094,
      "f1": 0.6
    },
    "B": {
      "tp": 27,
      "fp": 26,
      "fn": 10,
      "support": 37,
      "precision": 0.5094,
      "recall": 0.7297,
      "f1": 0.6
    }
  }
}
*Prompt 2*

EN DEV P2

{
  "gold_file": "pronoun_resolution/testing/en/full/en_dev_full.csv",
  "pred_file": "pronoun_resolution/testing/results/sonnet_4.6_dev_en_p2.csv",
  "data_size": 100,
  "prediction_rows_raw": 100,
  "prediction_rows_after_dedup": 100,
  "correct": 89,
  "accuracy": 0.89,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.9333,
  "recall_A": 0.84,
  "f1_A": 0.8842,
  "precision_B": 0.8545,
  "recall_B": 0.94,
  "f1_B": 0.8952,
  "macro_f1": 0.8897,
  "class_metrics": {
    "A": {
      "tp": 42,
      "fp": 3,
      "fn": 8,
      "support": 50,
      "precision": 0.9333,
      "recall": 0.84,
      "f1": 0.8842
    },
    "B": {
      "tp": 47,
      "fp": 8,
      "fn": 3,
      "support": 50,
      "precision": 0.8545,
      "recall": 0.94,
      "f1": 0.8952
    }
  }
}

AM DEV P2

{
  "gold_file": "pronoun_resolution/testing/am/full/am_dev_full.csv",
  "pred_file": "pronoun_resolution/testing/results/sonnet_4.6_dev_am_p2.csv",
  "data_size": 90,
  "prediction_rows_raw": 90,
  "prediction_rows_after_dedup": 90,
  "correct": 71,
  "accuracy": 0.7889,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.8529,
  "recall_A": 0.6744,
  "f1_A": 0.7532,
  "precision_B": 0.75,
  "recall_B": 0.8936,
  "f1_B": 0.8155,
  "macro_f1": 0.7844,
  "class_metrics": {
    "A": {
      "tp": 29,
      "fp": 5,
      "fn": 14,
      "support": 43,
      "precision": 0.8529,
      "recall": 0.6744,
      "f1": 0.7532
    },
    "B": {
      "tp": 42,
      "fp": 14,
      "fn": 5,
      "support": 47,
      "precision": 0.75,
      "recall": 0.8936,
      "f1": 0.8155
    }
  }
}

IG DEV P2

{
  "gold_file": "testing/ig/full/ig_dev_full.csv",
  "pred_file": "testing/results/sonnet_4.6_dev_ig_p2.csv",
  "data_size": 90,
  "prediction_rows_raw": 90,
  "prediction_rows_after_dedup": 90,
  "correct": 53,
  "accuracy": 0.5889,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.5882,
  "recall_A": 0.4651,
  "f1_A": 0.5195,
  "precision_B": 0.5893,
  "recall_B": 0.7021,
  "f1_B": 0.6408,
  "macro_f1": 0.5801,
  "class_metrics": {
    "A": {
      "tp": 20,
      "fp": 14,
      "fn": 23,
      "support": 43,
      "precision": 0.5882,
      "recall": 0.4651,
      "f1": 0.5195
    },
    "B": {
      "tp": 33,
      "fp": 23,
      "fn": 14,
      "support": 47,
      "precision": 0.5893,
      "recall": 0.7021,
      "f1": 0.6408
    }
  }
}

ZU DEV P2

{
  "gold_file": "testing/zu/full/zu_dev_full.csv",
  "pred_file": "testing/results/sonnet_4.6_dev_zu_p2.csv",
  "data_size": 90,
  "prediction_rows_raw": 90,
  "prediction_rows_after_dedup": 90,
  "correct": 54,
  "accuracy": 0.6,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.7429,
  "recall_A": 0.4906,
  "f1_A": 0.5909,
  "precision_B": 0.5091,
  "recall_B": 0.7568,
  "f1_B": 0.6087,
  "macro_f1": 0.5998,
  "class_metrics": {
    "A": {
      "tp": 26,
      "fp": 9,
      "fn": 27,
      "support": 53,
      "precision": 0.7429,
      "recall": 0.4906,
      "f1": 0.5909
    },
    "B": {
      "tp": 28,
      "fp": 27,
      "fn": 9,
      "support": 37,
      "precision": 0.5091,
      "recall": 0.7568,
      "f1": 0.6087
    }
  }
}

*Prompt 3*

EN DEV P3

{
  "gold_file": "pronoun_resolution/testing/en/full/en_dev_full.csv",
  "pred_file": "pronoun_resolution/testing/results/sonnet_4.6_dev_en_p3.csv",
  "data_size": 100,
  "prediction_rows_raw": 100,
  "prediction_rows_after_dedup": 100,
  "correct": 89,
  "accuracy": 0.89,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 2,
  "refusal_rate": 0.02,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.9767,
  "recall_A": 0.84,
  "f1_A": 0.9032,
  "precision_B": 0.8545,
  "recall_B": 0.94,
  "f1_B": 0.8952,
  "macro_f1": 0.8992,
  "class_metrics": {
    "A": {
      "tp": 42,
      "fp": 1,
      "fn": 8,
      "support": 50,
      "precision": 0.9767,
      "recall": 0.84,
      "f1": 0.9032
    },
    "B": {
      "tp": 47,
      "fp": 8,
      "fn": 3,
      "support": 50,
      "precision": 0.8545,
      "recall": 0.94,
      "f1": 0.8952
    }
  }
}

AM DEV P3

{
  "gold_file": "pronoun_resolution/testing/am/full/am_dev_full.csv",
  "pred_file": "pronoun_resolution/testing/results/sonnet_4.6_dev_am_p3.csv",
  "data_size": 90,
  "prediction_rows_raw": 90,
  "prediction_rows_after_dedup": 90,
  "correct": 70,
  "accuracy": 0.7778,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.7949,
  "recall_A": 0.7209,
  "f1_A": 0.7561,
  "precision_B": 0.7647,
  "recall_B": 0.8298,
  "f1_B": 0.7959,
  "macro_f1": 0.776,
  "class_metrics": {
    "A": {
      "tp": 31,
      "fp": 8,
      "fn": 12,
      "support": 43,
      "precision": 0.7949,
      "recall": 0.7209,
      "f1": 0.7561
    },
    "B": {
      "tp": 39,
      "fp": 12,
      "fn": 8,
      "support": 47,
      "precision": 0.7647,
      "recall": 0.8298,
      "f1": 0.7959
    }
  }
}

IG DEV P3

{
  "gold_file": "testing/ig/full/ig_dev_full.csv",
  "pred_file": "testing/results/sonnet_4.6_dev_ig_p3.csv",
  "data_size": 90,
  "prediction_rows_raw": 90,
  "prediction_rows_after_dedup": 90,
  "correct": 48,
  "accuracy": 0.5333,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 1,
  "refusal_rate": 0.0111,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.5128,
  "recall_A": 0.4651,
  "f1_A": 0.4878,
  "precision_B": 0.56,
  "recall_B": 0.5957,
  "f1_B": 0.5773,
  "macro_f1": 0.5326,
  "class_metrics": {
    "A": {
      "tp": 20,
      "fp": 19,
      "fn": 23,
      "support": 43,
      "precision": 0.5128,
      "recall": 0.4651,
      "f1": 0.4878
    },
    "B": {
      "tp": 28,
      "fp": 22,
      "fn": 19,
      "support": 47,
      "precision": 0.56,
      "recall": 0.5957,
      "f1": 0.5773
    }
  }
}

ZU DEV P3

{
  "gold_file": "testing/zu/full/zu_dev_full.csv",
  "pred_file": "testing/results/sonnet_4.6_dev_zu_p3.csv",
  "data_size": 90,
  "prediction_rows_raw": 90,
  "prediction_rows_after_dedup": 90,
  "correct": 50,
  "accuracy": 0.5556,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 1,
  "refusal_rate": 0.0111,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.6842,
  "recall_A": 0.4906,
  "f1_A": 0.5714,
  "precision_B": 0.4706,
  "recall_B": 0.6486,
  "f1_B": 0.5455,
  "macro_f1": 0.5584,
  "class_metrics": {
    "A": {
      "tp": 26,
      "fp": 12,
      "fn": 27,
      "support": 53,
      "precision": 0.6842,
      "recall": 0.4906,
      "f1": 0.5714
    },
    "B": {
      "tp": 24,
      "fp": 27,
      "fn": 13,
      "support": 37,
      "precision": 0.4706,
      "recall": 0.6486,
      "f1": 0.5455
    }
  }
}

*Prompt 4*

EN DEV P4

{
  "gold_file": "pronoun_resolution/testing/en/full/en_dev_full.csv",
  "pred_file": "pronoun_resolution/testing/results/sonnet_4.6_dev_en_p4.csv",
  "data_size": 100,
  "prediction_rows_raw": 100,
  "prediction_rows_after_dedup": 100,
  "correct": 89,
  "accuracy": 0.89,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.9535,
  "recall_A": 0.82,
  "f1_A": 0.8817,
  "precision_B": 0.8421,
  "recall_B": 0.96,
  "f1_B": 0.8972,
  "macro_f1": 0.8895,
  "class_metrics": {
    "A": {
      "tp": 41,
      "fp": 2,
      "fn": 9,
      "support": 50,
      "precision": 0.9535,
      "recall": 0.82,
      "f1": 0.8817
    },
    "B": {
      "tp": 48,
      "fp": 9,
      "fn": 2,
      "support": 50,
      "precision": 0.8421,
      "recall": 0.96,
      "f1": 0.8972
    }
  }
}

AM DEV P4

{
  "gold_file": "pronoun_resolution/testing/am/full/am_dev_full.csv",
  "pred_file": "pronoun_resolution/testing/results/sonnet_4.6_dev_am_p4.csv",
  "data_size": 90,
  "prediction_rows_raw": 90,
  "prediction_rows_after_dedup": 90,
  "correct": 70,
  "accuracy": 0.7778,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.8108,
  "recall_A": 0.6977,
  "f1_A": 0.75,
  "precision_B": 0.7547,
  "recall_B": 0.8511,
  "f1_B": 0.8,
  "macro_f1": 0.775,
  "class_metrics": {
    "A": {
      "tp": 30,
      "fp": 7,
      "fn": 13,
      "support": 43,
      "precision": 0.8108,
      "recall": 0.6977,
      "f1": 0.75
    },
    "B": {
      "tp": 40,
      "fp": 13,
      "fn": 7,
      "support": 47,
      "precision": 0.7547,
      "recall": 0.8511,
      "f1": 0.8
    }
  }
}

IG DEV P4

{
  "gold_file": "testing/ig/full/ig_dev_full.csv",
  "pred_file": "testing/results/sonnet_4.6_dev_ig_p4.csv",
  "data_size": 90,
  "prediction_rows_raw": 90,
  "prediction_rows_after_dedup": 90,
  "correct": 46,
  "accuracy": 0.5111,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 1,
  "refusal_rate": 0.0111,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.4865,
  "recall_A": 0.4186,
  "f1_A": 0.45,
  "precision_B": 0.5385,
  "recall_B": 0.5957,
  "f1_B": 0.5657,
  "macro_f1": 0.5078,
  "class_metrics": {
    "A": {
      "tp": 18,
      "fp": 19,
      "fn": 25,
      "support": 43,
      "precision": 0.4865,
      "recall": 0.4186,
      "f1": 0.45
    },
    "B": {
      "tp": 28,
      "fp": 24,
      "fn": 19,
      "support": 47,
      "precision": 0.5385,
      "recall": 0.5957,
      "f1": 0.5657
    }
  }
}

ZU DEV P4

{
  "gold_file": "testing/zu/full/zu_dev_full.csv",
  "pred_file": "testing/results/sonnet_4.6_dev_zu_p4.csv",
  "data_size": 90,
  "prediction_rows_raw": 90,
  "prediction_rows_after_dedup": 90,
  "correct": 50,
  "accuracy": 0.5556,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 1,
  "refusal_rate": 0.0111,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0,
  "precision_A": 0.6944,
  "recall_A": 0.4717,
  "f1_A": 0.5618,
  "precision_B": 0.4717,
  "recall_B": 0.6757,
  "f1_B": 0.5556,
  "macro_f1": 0.5587,
  "class_metrics": {
    "A": {
      "tp": 25,
      "fp": 11,
      "fn": 28,
      "support": 53,
      "precision": 0.6944,
      "recall": 0.4717,
      "f1": 0.5618
    },
    "B": {
      "tp": 25,
      "fp": 28,
      "fn": 12,
      "support": 37,
      "precision": 0.4717,
      "recall": 0.6757,
      "f1": 0.5556
    }
  }
}