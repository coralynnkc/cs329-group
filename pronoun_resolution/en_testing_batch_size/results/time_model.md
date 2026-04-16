chat 5.4
batch size:
25 - [5 minute time out], 37 seconds
100 - 88 seconds
250 - 172 seconds
500 - 172 seconds
when thinking -- recognized winogrande style, says will use heuristics or label data manully. "I can do most labels manually"

chat 5.3

batch size:
25 - 32 seconds
100 - 25 seconds [returned 83 rows, then 92 rows, but hallcuinated the IDs of that additiona 9 rows. Refused to output the 100 rows] [on redo, model thought for 22 second but hallucinated row IDs even more quickly. when further pressed, the model mirroed the task IDs properly (I had poitned out this hallucination) but still A/B'd every task]. It did not communicate that it had refused task. https://chatgpt.com/share/69e04ed9-1aec-83ea-b960-0f16638586ab
250 - 25 seconds [refused every query. on reprompt, hallucinated task IDs and answered A/B every other in a clear mirror]
