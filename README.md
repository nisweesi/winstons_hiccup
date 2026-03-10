# Winston's Hiccup

A scalable search engine for historical newspapers based on OCR data from the Library of Congress Chronicling America dataset.

The project builds a local information retrieval system capable of indexing large collections of OCR‑extracted newspaper pages and retrieving relevant documents using classical search engine techniques such as inverted indexing and BM25 ranking.

---

## Project Goal

Historical newspapers provide a direct view into how people experienced major events such as the World Wars. However, exploring millions of scanned pages manually is impractical.

This project builds a search system that allows users to:

- index large collections of OCR newspaper pages
- search for words and phrases efficiently
- retrieve ranked results using BM25
- perform phrase and proximity search

---

## Core Features

- OCR document parsing
- Text preprocessing and tokenization
- Positional inverted index
- MapReduce‑style indexing pipeline
- Disk‑based index storage
- BM25 ranking
- Phrase and proximity search
- Retrieval evaluation using precision/recall metrics

---

## System Pipeline

```
                 OCR Dataset
                     |
                     v
               Document Parser
                     |
                     v
              Text Preprocessing
                     |
                     v
            MapReduce Index Builder
                     |
                     v
            Inverted Index (lexicon)
                     |
                     v
               Query Processing
                     |
                     v
                 BM25 Ranking
                     |
                     v
                 Top‑k Results
```

---

## Repository Structure

```
.
├── config.yaml
├── data/                # datasets and intermediate processing outputs
├── docs/                # technical documentation and engineering roadmap
├── index/               # generated index files
├── results/             # experiment outputs and evaluation results
├── scripts/             # runnable pipeline scripts
├── src/                 # core implementation modules
├── tests/               # unit tests
└── README.md
```

---

## Running the Pipeline

Example commands:

```
python scripts/run_parser.py
python scripts/run_indexer.py
python scripts/run_evaluation.py
```

Configuration settings such as dataset paths and experiment parameters are defined in `config.yaml`.

---

## Documentation

Detailed documentation is available in the `docs/` directory:

- `docs/Technical_overview.md` – system architecture and design
- `docs/Roadmap.md` – development milestones and engineering plan

More will be included during the implementation....

---

## Evaluation

The system records metrics for:

- dataset statistics
- indexing performance
- index size
- query latency
- retrieval quality (Precision, Recall, MAP)

Experimental outputs are stored in:

```
results/
```

---

## Future Improvements

Planned improvements include:

- index compression (gap encoding + varint)
- fuzzy matching for OCR errors
- distributed indexing
- semantic retrieval and hybrid search

---

## License

This project is licensed under the MIT License.
See the LICENSE file for details.