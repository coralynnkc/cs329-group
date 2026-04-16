## Results Summary

Our batch-size experiment shows that accuracy alone is not enough to evaluate LLM performance on structured pronoun-resolution annotation. Because this task requires the model to return a label for each specific `item_id`, failures can occur at two different levels: the model can make the wrong linguistic decision, or it can fail to execute the batch-formatting task reliably. For that reason, we evaluated not only accuracy, but also coverage, missing rate, and hallucinated IDs.

Coverage is especially useful here. In our setup, coverage reflects the proportion of gold items for which the model returned a usable prediction aligned to the correct `item_id`. This matters because a model can appear superficially competent if it gives plausible A/B answers, yet still fail to complete the task faithfully. When the model hallucinates or corrupts `item_id`s, that does **not necessarily prove** it is only guessing on the sentence task itself. The model may still be attempting to solve individual examples. However, hallucinated IDs do show that it has lost track of the structured annotation procedure. In other words, even if some local sentence-level reasoning is still happening, the run is no longer reliable as a batch-labeling output. This is important because pronoun resolution is a binary task: a model that guesses can still achieve non-trivial accuracy by chance, so accuracy by itself can hide serious execution failures. Measuring coverage, missing rate, and extra IDs gives a clearer picture of whether the model is actually functioning as a dependable annotator rather than just producing plausible-looking labels.

The results show a strong difference between models and reasoning modes. Chat 5.4 under standard settings performed well through medium-sized batches, achieving 96% accuracy at 25 items, 93% at 100 items, and 85.6% at 250 items, while maintaining full coverage and no hallucinated IDs in all three settings. This suggests that standard Chat 5.4 remained reliable up to 250 items, with only a gradual decline in sentence-level performance as batch size increased.

At 500 items, however, standard Chat 5.4 failed dramatically. Accuracy dropped to 25%, coverage fell to 29.6%, and the run contained 352 missing predictions and 352 extra IDs. This pattern indicates that the main problem at this batch size was not simply weaker pronoun resolution, but a broader breakdown in structured task execution: the model no longer reliably tracked row identities or completed the full output. In contrast, Chat 5.4 with extended thinking handled the 500-item batch successfully, reaching 93.4% accuracy with 100% coverage, no extra IDs, and only one refusal. This suggests that the 500-item setting is feasible for Chat 5.4 when given substantially more reasoning time, but not under standard inference conditions.

Chat 5.3 showed a different pattern. It performed perfectly on the 25-item batch, but became unstable at larger sizes. On 100-item runs, it frequently returned incomplete outputs, hallucinated row IDs, or produced low-quality patterned responses. Depending on the rerun, accuracy ranged from 11% to 64%, and coverage ranged from 19% to 100%, indicating large run-to-run instability. At 250 items, the model effectively failed the task altogether, with notes indicating broad refusal behavior and hallucinated IDs on reprompting. These results suggest that Chat 5.3 was not just less accurate than Chat 5.4, but substantially less reliable as a batch annotation system.

Overall, the experiment shows that larger batch sizes introduce two distinct risks: declining sentence-level accuracy and declining structured-output reliability. Standard Chat 5.4 remained robust up to 250 items, but collapsed at 500 without extended reasoning. Chat 5.4 extended thinking largely removed that failure, though at much higher latency. Chat 5.3, by contrast, became unstable well before 250 items. The main takeaway is that small-batch accuracy can overstate a model’s practical usefulness for bulk annotation. For this kind of workflow, coverage and ID integrity are essential alongside accuracy, because they reveal whether the model is truly completing the dataset faithfully rather than only generating plausible answers.

chat 5.4

batch size:
25 - [5 minute time out], 37 seconds

  "data_size": 25,
  "prediction_rows_raw": 25,
  "prediction_rows_after_dedup": 25,
  "correct": 24,
  "accuracy": 0.96,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 1,
  "refusal_rate": 0.04,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0
}

100 - 88 seconds

  "pred_file": "results/chat_5.4_100_en.csv",
  "data_size": 100,
  "prediction_rows_raw": 100,
  "prediction_rows_after_dedup": 100,
  "correct": 93,
  "accuracy": 0.93,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 3,
  "refusal_rate": 0.03,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0
}


250 - 172 seconds

  "pred_file": "results/chat_5.4_250_en.csv",
  "data_size": 250,
  "prediction_rows_raw": 250,
  "prediction_rows_after_dedup": 250,
  "correct": 214,
  "accuracy": 0.856,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 5,
  "refusal_rate": 0.02,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0
}

500 - 172 seconds
when thinking -- recognized winogrande style, says will use heuristics or label data manully. "I can do most labels manually"

  "pred_file": "results/chat_5.4_500_en.csv",
  "data_size": 500,
  "prediction_rows_raw": 500,
  "prediction_rows_after_dedup": 500,
  "correct": 125,
  "accuracy": 0.25,
  "missing_predictions": 352,
  "missing_rate": 0.704,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 352,
  "coverage": 0.296
}

chat 5.4 extended thinking

500 - 620 secoonds

  "pred_file": "results/chat_5.4_extended_500_en.csv",
  "data_size": 500,
  "prediction_rows_raw": 500,
  "prediction_rows_after_dedup": 500,
  "correct": 467,
  "accuracy": 0.934,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 1,
  "refusal_rate": 0.002,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0
}



chat 5.3

batch size:

25 - 32 seconds
  "accuracy": 1.0,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0
}


100 - 25 seconds [returned 83 rows, then 92 rows, but hallcuinated the IDs of that additiona 9 rows. Refused to output the 100 rows] [on redo, model thought for 22 second but hallucinated row IDs even more quickly. when further pressed, the model mirroed the task IDs properly (I had poitned out this hallucination) but still A/B'd every task]. It did not communicate that it had refused task. https://chatgpt.com/share/69e04ed9-1aec-83ea-b960-0f16638586ab

original:

  "pred_file": "results/chat_5.3_100_en.csv",
  "data_size": 100,
  "prediction_rows_raw": 92,
  "prediction_rows_after_dedup": 92,
  "correct": 57,
  "accuracy": 0.57,
  "missing_predictions": 15,
  "missing_rate": 0.15,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 7,
  "coverage": 0.85
}

redo [re-ran in new context]:
  "pred_file": "results/chat_5.3_100_en_redo.csv",
  "data_size": 100,
  "prediction_rows_raw": 94,
  "prediction_rows_after_dedup": 94,
  "correct": 11,
  "accuracy": 0.11,
  "missing_predictions": 81,
  "missing_rate": 0.81,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 75,
  "coverage": 0.19
}

forced recomplete from original:

  "data_size": 100,
  "prediction_rows_raw": 100,
  "prediction_rows_after_dedup": 100,
  "correct": 64,
  "accuracy": 0.64,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0
}

250 - 25 seconds [refused every query. on reprompt, hallucinated task IDs and answered A/B every other in a clear pattern]



claude:

sonnet 4.6

batch size
25 -- 11 seconds

  "pred_file": "sonnet_4.6_25_en.csv",
  "data_size": 25,
  "prediction_rows_raw": 25,
  "prediction_rows_after_dedup": 25,
  "correct": 24,
  "accuracy": 0.96,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0
}

100 -- 14 seconds

  "pred_file": "results/sonnet_4.6_100_en.csv",
  "data_size": 100,
  "prediction_rows_raw": 100,
  "prediction_rows_after_dedup": 100,
  "correct": 91,
  "accuracy": 0.91,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 2,
  "refusal_rate": 0.02,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0
}

250 - 78 seconds

{
  "gold_file": "data/batch_250_full.csv",
  "pred_file": "results/sonnet_4.6_250_en.csv",
  "data_size": 250,
  "prediction_rows_raw": 250,
  "prediction_rows_after_dedup": 250,
  "correct": 213,
  "accuracy": 0.852,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0
}

500 - 170 seconds

  "pred_file": "results/sonnet_4.6_500_en.csv",
  "data_size": 500,
  "prediction_rows_raw": 500,
  "prediction_rows_after_dedup": 500,
  "correct": 438,
  "accuracy": 0.876,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0
}


claude opus 4.6 (more advanced)

250 - 52 seconds

  "pred_file": "results/opus_4.6_250_en.csv",
  "data_size": 250,
  "prediction_rows_raw": 250,
  "prediction_rows_after_dedup": 250,
  "correct": 239,
  "accuracy": 0.956,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 1,
  "refusal_rate": 0.004,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0
}

500 - 286 seconds

  "pred_file": "results/opus_4.6_500_en.csv",
  "data_size": 500,
  "prediction_rows_raw": 500,
  "prediction_rows_after_dedup": 500,
  "correct": 463,
  "accuracy": 0.926,
  "missing_predictions": 0,
  "missing_rate": 0.0,
  "refusals": 0,
  "refusal_rate": 0.0,
  "invalid_predictions": 0,
  "invalid_rate": 0.0,
  "duplicate_prediction_rows": 0,
  "extra_prediction_ids": 0,
  "coverage": 1.0
}

