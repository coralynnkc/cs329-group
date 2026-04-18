## REVISED PROMPT TO IMRPOVE CHATGPT SCORES
for each row, identify all named entities in the sentence. 

Return ONLY a CSV saved as ner_predictions_[model].csv with columns: sample_id,sentence_id,predicted_entities where predicted_entities is a JSON list of {"text": "...", "label": "..."} objects. 
Do not skip rows. 
Do not add any extra text. 

Rules: - Valid labels: PER, ORG, LOC, MISC - Extract ONLY entities explicitly in the sentence - Copy entity text EXACTLY as it appears (no rephrasing, no shortening, no expanding) - Do NOT guess or infer entities - Each entity must be an exact substring of the sentence - If no entities, return [] 


Example: Input: 1,1,London is the capital of England . Output: 1,1,"[{""text"": ""London"", ""label"": ""LOC""}, {""text"": ""England"", ""label"": ""LOC""}]" Data:
