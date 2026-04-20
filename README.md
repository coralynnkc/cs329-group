# LLMs for Linguistic Annotation

**Thesis:** LLMs can serve as general-purpose linguistic annotation tools via prompt engineering alone — no fine-tuning, no labeled training data, no task-specific pipelines.

---

## Results

| Task | Dataset | SOTA | Key Finding |
|------|---------|------|-------------|
| Lemmatization | UniMorph English | spaCy/stanza ~95–99% | Sonnet/Opus match SOTA (~96–97%); prompting alone is sufficient |
| Grammaticality | CoLA | Human ~80% | Opus 88%, Sonnet 84% — both exceed human ceiling; ChatGPT collapses to ~49% |
| POS tagging | UD English EWT | spaCy/udpipe ~97–98% | Opus 94% in-domain; competitive without any dependency parsing pipeline |
| NER | CoNLL-2003 | spaCy/stanza F1 ~91% | Opus F1 0.95, exceeds SOTA; ChatGPT F1 0.26 (catastrophic over-prediction failure) |
| Agency-based NER | Narnia (manual, 200 sentences) | No supervised baseline | Zero-shot Opus F1 0.78; few-shot Sonnet F1 0.82 — novel schema with no prior art |
| Character-cluster NER | Narnia chapters | No supervised baseline | Opus F1 0.88 zero-shot; epithet resolution ("the Faun" → Mr. Tumnus) works reliably |
| Pronoun resolution | African WinoGrande + XWinograd | Chance = 50% | EN/FR/DE/RU: 86–97%; Igbo/Zulu near chance — low-resource degradation is real |
| Presuppositions | XNLI (6 languages) | — | EN Neutral collapses in all models; prompt framing shifts class boundaries cross-linguistically |

---

## Narnia Methodology

The Narnia task combines two traditionally separate NLP challenges — entity recognition and agency classification — into a single inference call, with no post-processing.

### Task

Given a sentence from *The Lion, the Witch and the Wardrobe*, identify every character mention and classify its narrative role. Surface mentions must be resolved to canonical identities (e.g., "the Faun", "Tumnus", and "Mr. Tumnus" all map to the same character).

### Agency Labels

| Label | Meaning |
|-------|---------|
| `ACTIVE_SPEAKER` | Character speaks |
| `ACTIVE_PERFORMER` | Character performs a physical action |
| `ACTIVE_THOUGHT` | Internal state or feeling |
| `ADDRESSED` | Spoken to directly |
| `MENTIONED_ONLY` | Third-person reference, no active role |
| `MISCELLANEOUS` | Species or group reference |

The critical difficulty is that labels require nuanced judgment: *"Lucy was tired"* is `ACTIVE_THOUGHT`, not `ACTIVE_PERFORMER`.

### Data

200 sentences manually annotated by the project team. 159 sentences used for training context (few-shot examples); 40 held out for evaluation. Annotations are in `narnia/man_annotated_narnia200 - Sheet1.csv`.

### Prompting

The final prompt submits entire chapters as a single inference call, returning structured CSV output. Few-shot prompting (9 examples) gave the largest gains for weaker models: ChatGPT F1 0.59 → 0.80 (+21 pp), suggesting few-shot examples fix output-format failures more than genuine label understanding.

### Why no supervised baseline

The agency schema is novel — no pre-existing model or labeled corpus exists for this label set. This makes it a clean test of LLM generality: the only way to do this task is to understand the labels from description alone.

---

## Repository Structure

```
cs329-group/
├── grammatical/          # Binary grammaticality (CoLA)
├── grammaticality-2.0/   # CoLA + pairwise BLiMP; stronger metrics (MCC, F1)
├── lemmatization/        # Lemmatization + morpheme segmentation (UniMorph)
├── pos/                  # Universal Dependencies POS tagging (UD English EWT)
├── ner/                  # Standard NER (CoNLL-2003; PER/ORG/LOC/MISC)
├── narnia/               # Agency-based NER on 200 annotated Narnia sentences
├── narnia-large/         # Chapter-level agency NER + character clustering (WIP)
├── coref/                # Character-cluster coreference NER (Narnia chapters)
├── pronoun_resolution/   # Pronoun resolution — EN, AM, IG, ZU
├── srijon-2.0/           # Multilingual pronoun resolution + presuppositions (scripted)
├── srijon/               # Original notebook-based multilingual benchmarks
├── claire/               # Dataset builder: unified pronoun benchmark (XWinograd + African WinoGrande)
├── background/           # Research notes and prompting papers (PDFs/Typst)
├── demo/                 # Task description writeup for agency-based NER
├── val_metrics/          # Validation metrics documentation
└── archive/              # Old baseline scripts
```

Each module follows the same pipeline:

1. `scripts/make_mini.py` — generate stratified eval CSV
2. Paste into model, save predictions to `mini/predictions_<model>.csv`
3. `scripts/score_baseline.py --model <name>` — score predictions
4. `scripts/update_readme.py` — update result table in module README

See `CLAUDE.md` for full command reference.
