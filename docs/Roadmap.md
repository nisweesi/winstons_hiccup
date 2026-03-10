# Objective

As someone deeply interested in the history of the World Wars, I have found it difficult to access reliable accounts of what people were actually reading and discussing during that era. Modern sources can be shaped by hindsight, interpretation, or misinformation, while firsthand perspectives are often fragmented and difficult to access. Historical newspapers offer a valuable window into that period: although they may contain bias or propaganda, they still preserve the language, events, and public narratives of the time.

The challenge is that historic newspapers exist at massive scale, spanning millions of scanned pages, which makes manual exploration impractical. This project addresses that problem by building a scalable search engine over OCR-extracted newspaper pages from the Library of Congress. Using an inverted index, the system makes it possible to search for a word or phrase and retrieve all relevant newspaper pages in which it appeared, enabling faster exploration of historical trends, narratives, and events.

---
# Scope of v1

- Build a local search engine over a selected slice of LOC OCR newspaper pages  
- Support document parsing, tokenization, positional inverted indexing, BM25 ranking, and phrase/proximity search  
- Store the index on disk using a lexicon, postings file, and document metadata file  
- Evaluate indexing performance, retrieval latency, and retrieval quality on a small judged query set

---
# Phase Plan

## **Phase 0: Setup**

**Estimated Time:** 1 day  

**Tasks:**
- Create a repository  
- Create the project structure  
- Set up a virtual environment   
- Choose coding standards  
- Create a config file for paths and experiment settings

**Deliverables:**
- Working repo  
- Config file  
- README file

**Success criteria:**
- Project runs locally   
- Paths and config are centralized
---
## Milestone 1 \- Dataset profiling
## **Phase 1: Dataset Profiling**

**Estimated Time:** 1 to 2 days  

**Tasks:**
- Parse metadata from OCR paths  
- Count files/pages  
- Inspect text quality  
- Compute token counts on a sample  
- Define the first corpus slice we are going to index

**Deliverables:**
- dataset\_manifest.csv  
- dataset\_stats.json  
- Sample\_docs.jsonl  
- dataset\_profile.md

**Success criteria:**
- Know exactly how many pages we have  
- We can extract the metadata (doc\_id, newspaper\_id, date, page)  
- Have a documented sample of OCR noise

## Milestone 2 \- Document parsing pipeline

## **Phase 2: Parser**

**Estimated Time:** 1 to 2 days  

**Tasks:**
- Read OCR text files  
- Extract metadata from path  
- Convert each page into a structured JSON record  
- Write JSONL output

**Deliverables:**
- Parsed\_documents.jsonl  
- Parser module  
- Validation script

Success criteria:
- every OCR page becomes one valid structured document

## **Phase 3: Tokenizer**

**Estimated Time:** 1 day  

**Tasks:**
- Lowercase  
- Strip punctuation  
- Normalize white space  
- Tokenize text  
- Remove stop words  
- Preserve positions

**Deliverables:**
- Tokenization module  
- Tokenized sample output  
- Unit tests on a few samples

**Success criteria:**
- same preprocessing is used for both documents and queries

## Milestone 3 \- MapReduce index pipeline

## **Phase 4: Mapper**

Estimated Time: 2 days  

Tasks:
- Transform each tokenized document into emitted tuple   
- The structure should be (term, doc\_id, position) 

Deliverables:
- Mapper module  
- Shard files

Success criteria:
- emitted records are correct and reproducible  
- output can be sorted/grouped downstream

### **Phase 5: Shuffle/Sort**

**Estimated Time:** 3 days  

**Tasks:**
- aggregate positions for each (term, doc\_id) pair  
- Group identical terms  
- Prepare for external sort if needed


**Deliverables:**
- Grouping module  
- Sorted intermediate files  
- Benchmark for sorting time

**Success criteria:**
- Same term occurrences are grouped together  
- The pipeline works on a dataset that’s larger than the memory size


## Milestone 4 \- Inverted index built
## **Phase 6: Reducer \+ Segment Writer**

**Estimated Time:** 3 days

**Tasks:**
- Aggregate grouped records into postings lists  
- Compute the df (document frequency) and tf (term frequency)  
- Preserve positions  
- Write postings to disk  
- Write lexicon and document metadata

**Deliverables:**
- lexicon.bin  
- postings.bin  
- docmetadata.bin

**Success criteria:**
- Each indexed term points to a valid posting  
- Lexicon offset resolves correctly

## Milestone 5 \- Search engine functional

## **Phase 7: Search \+ BM25**

**Estimated Time:** 3 days  

**Tasks:**
- Preprocess query  
- Lookup term in lexicon  
- Load postings  
- Generate candidate set  
- Compute BM25  
- Return top-k results

**Deliverables:**
- CLI interface  
- BM25 scorer  
- Top-k results output

**Success criteria:**
- Query returns ranked documents  
- Results show metadata and snippet

### **Phase 8: Phrase and Proximity Search**

**Estimated Time:** 2 days  

**Tasks:**
- Use positions in indexing  
- Implemented exact phrase matching  
- Add proximity window

**Deliverables:**
- Phrase query logic

**Success criteria:**
- Phrase query returns only true positional matches

## Milestone 6 \- Evaluation and optimization

### **Phase 9: Compression**

**Estimated Time:** 3 days  

**Tasks:**
- Add gap encoding to doc\_id and positions  
- Add varint encoding  
- Compare before and after size  
- Compare latency impact

**Deliverables:**
- Compressed index format  
- Index size comparison report

**Success criteria:**
- Measurable reduction in disk usage  
- Search results remain correct

### **Phase 10: Evaluation** 

**Estimated Time:** 3 days  

**Tasks:**
- Measure build time  
- Measure index size  
- Measure memory use  
- create a small query set  
- create relevance judgments (qrels) for those queries  
- compute precision@k, recall@k, and latency metrics  
- Measure precision, recall, and latency

**Deliverables:**
- Benchmark\_results.csv  
- Retrieval\_eval.csv  
- Charts and summary table

**Success criteria:**
- We can state quantitative results clearly

---
# Measurement Plan

The measurement plan defines the metrics used to evaluate the dataset, indexing pipeline, and retrieval performance.  
All experiments will log results in structured files to ensure reproducibility and enable comparison between indexing configurations.

The measurements are divided into three categories:

## **Dataset statistics**

Dataset statistics describe the size and quality of the corpus being indexed.  
These measurements help estimate system scalability and storage requirements.

### Metrics collected
**Corpus Size**

- Number of documents  
- Number of newspapers  
- Number of pages  
- Date Range covered  

**Token Statistics**  
- Total token count  
- Average tokens per documents  
- Median tokens per documents  
- Minimum tokens per documents  
- Maximum tokens per documents

**OCR quality estimate**
- Number of samples pages  
- Estimated OCR error rate  
- Common OCR error patterns

Output files:  

```bash
results/dataset/dataset_stats.json  
results/dataset/dataset_profile.md
```

Example:  
```json
{  
  "num_documents": 50213,  
  "avg_tokens_per_doc": 1102,  
  "median_tokens_per_doc": 987,  
  "total_tokens": 55300000,  
  "ocr_error_rate_estimate": 0.038  
}
```

## **Index metrics**

Index metrics evaluate how efficiently the system constructs the inverted index.

These measurements capture the performance of the indexing pipeline and the storage footprint of the resulting index.

### Metrics collected

**Index construction performance**

- Total indexing time  
- Documents processed per second  
- Token processed per second

**Resources Usage**

- Peak memory usage under indexing  
- CPU usage

**Index Storage Size**

- Total index size on disk  
- Postings file size  
- Lexicon file size  
- Document metadata file size

**Compression Impact**

- Index size before compression  
- Index size after compression  
- Compression ratio

Output files:  
```bash
results/indexing/build_runs.csv  
results/indexing/index_size_comparison.csv  
Example:  
run_id,documents, index_time_sec, docs_per_sec, index_size, mb  
run_01,50000,380,131,780  
run_02,50000,390,128,430
```
## **Retrieval metrics**

Retrieval quality measures how accurately the system returns relevant documents.

Evaluation will be performed using a small manually judged query set.

### Metrics collected
- Precision@k  
- Recall@k  
- Mean Average Precision (MAP)

Example:  
```text
Precision@10: 0.72  
Recall@10: 0.63  
MAP: 0.68
```
## **Query evaluation files**
```bash
results/retrieval/queries.csv  
results/retrieval/qrels.csv  
results/retrieval/retrieval_eval.csv
```
Example:

`bash queries.csv  `

| query_id | query_text            |
|----------|-----------------------|
| q1       | war europe 1914       |
| q2       | mining strike arizona |


`qrels.csv`

| query_id  | doc_id  | relevance |
|-----------|---------|----------|
| q1        | doc42   | 1        |
| q1        | doc108  | 1        |
---

# Reporting

At the end of each milestone, a summary report will be generated containing:

- dataset statistics  
- indexing performance  
- index size comparison  
- retrieval latency results  
- retrieval quality results

Example:  
`Milestone 3 - MapReduce Pipeline`
```text
Records generated: 52 million  
Sorting time: 4 minutes  
Peak memory: 1.3 GB
```
Observations:  
Sorting dominates pipeline runtime.

Next step:  
Implement reducer and build final postings lists.

These results will be used to evaluate whether the system meets the project objectives.

---

# Experiment Logging Format

Each run should record:

* run\_id  
* corpus slice  
* preprocessing settings  
* indexing settings  
* compression settings  
* build time  
* index size  
* memory usage  
* retrieval metrics

Example:  
```text
run_id: run_2026_03_10_v1  
corpus: loc_1914_slice  
compression: gap+varint  
docs: 50000  
index_size_mb: 430  
avg_latency_ms: 42  
precision_at_10: 0.72
```

---
# Risks and mitigation

**OCR noise may reduce retrieval quality**  
**Mitigation**: start with baseline lexical retrieval and evaluate future fuzzy matching later

**Dataset scale may exceed memory limits**  
**Mitigation**: prepare for external sort and segment-based indexing

**Phrase search increases storage cost**  
**Mitigation**: preserve positions only once in the base postings design

**Evaluation data may be limited**  
**Mitigation**: create a small judged query set for v1

---

# Exit criteria for v1

V1 should be done if we achieve all of the following:

- corpus can be parsed into structured documents  
- index can be built end-to-end  
- BM25 search returns ranked results  
- phrase search works  
- metrics are logged automatically  
- at least one benchmark report exists  
- at least one small relevance set has precision/recall results

