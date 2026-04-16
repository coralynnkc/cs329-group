# State-of-the-Art Validation Metrics

## TLDR:

1. Grammaticality with finding MUC  
   a. Can also use accuracy as secondary metric  

2. Redo Lemmatization with Exact Match and Edit Distance  

3. POS Tagging with F1  
   a. Can use also token level accuracy  

4. Redo Coreference with given 3 metrics  

5. Pronoun Resolution with F1  

6. Presupposition with Macro-F1  

---

## Quick Summary Table

| Task | Top Metrics | Description |
|------|------------|-------------|
| Grammaticality | MCC, Accuracy, F1 | MCC handles imbalance; accuracy/F1 simpler classification measures |
| Lemmatization | Exact Match, Edit Distance | Exact correctness vs partial string similarity |
| POS Tagging | Token Accuracy, F1 | Token-level correctness; F1 for class balance |
| Coreference | MUC, B³, CEAF (CoNLL F1) | Link-, mention-, and cluster-based evaluation |
| Pronoun Resolution | Accuracy, F1 | Correct antecedent selection |
| Presupposition / NLI | Accuracy, Macro F1 | Multi-class classification performance |


##Research Link

https://docs.google.com/document/d/1c9ZgO-knxeuYvzDs0v5cZyaB-2a2ZOYyKEoYY3utQbs/edit?usp=sharing 


