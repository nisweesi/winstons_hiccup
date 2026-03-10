# Problem Statement

As someone deeply interested in the history of the World Wars, I have found it difficult to access reliable accounts of what people were actually reading and discussing during that era. Modern sources can be shaped by hindsight, interpretation, or misinformation, while firsthand perspectives are often fragmented and difficult to access. Historical newspapers offer a valuable window into that period: although they may contain bias or propaganda, they still preserve the language, events, and public narratives of the time.

The challenge is that historic newspapers exist at massive scale, spanning millions of scanned pages, which makes manual exploration impractical. This project addresses that problem by building a scalable search engine over OCR-extracted newspaper pages from the Library of Congress1. Using an inverted index, the system makes it possible to search for a word or phrase and retrieve all relevant newspaper pages in which it appeared, enabling faster exploration of historical trends, narratives, and events.

---
# Dataset Description

**Library of Congress (LOC):** the choice of the Library of Congress was set because of the amount of available records with high quality and in large amounts.

The Library of Congress was chosen for this project because of:

- the large scale of available historical records  
- the high-quality digitization process used for archival preservation  
- the public accessibility of many datasets through open programs

These characteristics make LOC collections an excellent foundation for building large-scale text processing and search systems.

**Chronicling America dataset (CAD)**2: is a special dataset that offers access to historical newspapers that’s fully available to the public. The dataset includes newspapers spanning the late 18th century through the early 20th century.

Chronicling America provides access to its data in two primary ways:

- Bulk dataset downloads, which allow researchers to download large portions of the archive for local processing.  
- Public APIs, which allow programmatic access to individual newspaper pages and metadata.

For this project, the bulk OCR dataset is used so the indexing pipeline can operate locally on large amounts of historical text.

**Dataset Structure**: each newspaper page in the dataset is organized using a hierarchical directory structure.

A typical path to a page looks like the following:

```bash
sn82015761/1914/12/24/ed-1/seq-5
```

This structure encodes metadata about the document:

| Component | Meaning |
| :---- | :---- |
| sn82015761 | Unique newspaper identifier |
| 1914 | Publication year |
| 12 | Publication month |
| 24 | Publication day |
| ed-1 | Edition number |
| seq-5 | Page number within the issue |

**OCR extraction**: the newspaper pages were originally preserved as scanned images. To make the content searchable, the images were processed using Optical Character Recognition (OCR).

OCR is the process of converting scanned documents or images of text into machine-readable text. This allows large archives of printed material to be indexed and searched using computational systems.

However, OCR is not perfectly accurate. Historical documents often contain challenges such as:

- degraded paper quality  
- unusual fonts  
- scanning artifacts  
- complex page layouts

## Example:


`Kiany ~> Many`
`NewYear ~> New Year`

These errors occur when the OCR system incorrectly interprets characters or spacing in the scanned image. As a result, any search system built on OCR data must account for potential noise and inconsistencies in the text.

---
# System Overview

**Goal of the System**  
The goal of this system is to build a searchable archive of historical newspapers published between 1890 and 1950.
The dataset contains a large collection of OCR-extracted newspaper pages, which requires efficient processing and indexing techniques.

To enable fast retrieval, the system constructs a scalable inverted index over the OCR text. This allows users to search for words or phrases and quickly retrieve the newspaper pages in which those terms appear. Because the dataset can contain hundreds of thousands or millions of documents, the indexing pipeline must be designed to handle large-scale text processing efficiently.

---
## High-level Architecture

The system is composed of several components that transform raw OCR data into a searchable index.

### Dataset

The dataset consists of historical newspaper pages obtained from the Library of Congress Chronicling America dataset. Each page is stored in a structured directory that encodes metadata such as newspaper identifier, publication date, edition, and page number.

These pages contain OCR-extracted text, which becomes the input for the indexing pipeline.

### Document Parser

The Document Parser is responsible for ingesting the dataset and converting each OCR file into a structured document format.

During this stage the system

- reads OCR text files  
- extracts metadata from the file path (date, newspaper ID, page number)  
- converts each page into a structured JSON document  
- performs basic normalization of the text


``` json
{

"doc_id": "sn82015761_1914_12_24_seq5",

"newspaper_id": "sn82015761",

"date": "1914-12-24",

"page": 5,

"text": "IT ISN'T DIFFICULT TO TELL that Santa has paid the children a visit..."

}
```

### Text Processing

The text processing stage prepares the raw text for indexing. This includes several normalization steps that reduce noise and standardize the data.

- Typical preprocessing steps include:  
- converting text to lowercase  
- removing punctuation  
- splitting text into tokens (words)  
- optionally removing common stopwords

The result of this stage is a stream of tokens associated with their document identifiers, which will be used to construct the index.

### MapReduce Index Builder

The Index Builder constructs the inverted index using a MapReduce3-style pipeline.

The indexing process consists of three main stages:

**Map Stage**  
Each document is processed and converted into a sequence of tokens associated with the document identifier.

Example output:

`(war, doc1, position)`

`(begins, doc1, position)`

`(today, doc1, position)`

**Shuffle Stage**  
The system groups identical tokens together so that all occurrences of the same term are processed collectively.

Example:

`War ~> [(doc1, 1), (doc4, 4), (doc19, 2)]`

**Reduce Stage**  
The reduce stage constructs the postings lists for each term. These lists contain the identifiers of all documents in which the term appears.
```text
war ~> [

(doc1, [1]),

(doc4, [4,17])

]
```
The resulting index structures are then written to disk for later use by the search engin

**Inverted Index (data structure):** 

A naive approach to storing documents would use a key-value structure such as:

```text
doc_id ~> document_text
```

However, searching this structure would require scanning every document to determine whether it contains a given term. This approach becomes extremely inefficient for large datasets.

Instead, search engines use an inverted index.  
An inverted index maps each term to the list of documents in which the term appears.

Example documents:

```text
doc1: I went hiking every weekend this year

doc2: I play football last weekend

doc3: The best part of last year was watching football every weekend
```

The inverted index representation becomes:

`hiking   ~> [doc1]`

`weekend  ~> [doc1, doc2, doc3]`

`football ~> [doc2, doc3]`

`year     ~> [doc1, doc3]`

This structure allows the search engine to quickly locate all documents containing a given term without scanning the entire corpus.

**Index Storage on Disk**  
Once the inverted index is constructed, it must be stored efficiently on disk so that the search engine can access it quickly during query execution.

The index is typically divided into several components.

**Lexicon**  
The lexicon is a dictionary that maps each term to the location of its postings list within the postings file.

Example:

`war ~> offset 10234`

`clifton ~>  offset 20451`

The offset points to the position in the postings file where the list of documents for that term is stored.

**Postings Lists**  
The postings lists store the document identifiers associated with each term.

Example:

`I → [doc1, doc2, doc13]`

These lists may also store additional information such as term frequency or positional data.

**Document Metadata**

The system also stores metadata about each document, such as:

- document identifier  
- publication date  
- newspaper title  
- page number

This metadata allows the search engine to return meaningful results to the user.

**Search Engine**  
The search engine component processes user queries and retrieves the most relevant documents from the index.

1. Load the index into memory  
2. Tokenize the user query  
3. Retrieve postings lists for query terms  
4. Score documents using a ranking algorithm  
5. Return the top-k results

For ranking, the system uses the BM25 scoring algorithm, which is widely used in modern search engines to estimate the relevance of documents with respect to a query.

The final output is a ranked list of newspaper pages that contain the queried terms.

---
# Index Construction Pipeline

## Purpose of the Pipeline

The purpose of the index construction pipeline is to process large volumes of newspaper documents and convert them into a structure that can be searched efficiently. The dataset may contain hundreds of thousands or even millions of OCR-extracted pages, making it impractical to perform direct text scanning for each query.

Instead, the pipeline constructs an inverted index, which maps each term to the set of documents in which that term appears.

The pipeline follows a MapReduce-style architecture, transforming raw documents into index structures through several stages:

documents ~> tokens ~> grouped terms ~> postings lists  
This transformation enables fast lookup of documents containing specific words or phrases.

## Documents Input

The documents entering the pipeline are produced by the Document Parser described earlier. Each document corresponds to a single newspaper page extracted from the dataset.

Each document contains structured information such as:

```text
doc_id
newspaper_id
date
page
text
```

- doc_id: uniquely identifies the page  
- newspaper_id: identifies the publication  
- date: represents the publication date  
- page: represents the page number within the issue  
- text: contains the OCR-extracted content of the page

These documents become the input for the indexing pipeline.

## Map Stage

The Map stage is the first step in building the inverted index. The goal of this stage is to extract searchable terms from documents and associate them with their corresponding document identifiers.

During this stage, the system performs the following steps:

- read document text  
- tokenize words  
- normalize tokens  
- emit (term, doc_id, position) pairs

Document:

`doc1: "war begins today"`

Map output:

`(war, doc1, 1)`

`(begins, doc1, 2)`

`(today, doc1, 3)`

Each token extracted from the document produces a key-value pair linking the word to the document in which it appears.

## Shuffle Stage

The Shuffle stage groups identical terms together across all documents. Since the same word may appear in many different pages, this stage collects all occurrences of the same term and aggregates them into a single group. Also, we store the position of the word to add the ability of phrase search.

`war ~> [(doc1,1), (doc4,5), (doc4,17)]`

This stage is often the most computationally expensive step in large-scale systems because it requires processing and grouping terms from all documents in the dataset.

By organizing identical terms together, the shuffle stage prepares the data for constructing the final postings lists.

## Reduce Stage

The Reduce stage converts grouped terms into postings lists, which form the core of the inverted index.

- For each term, the reduce stage:  
- processes the grouped document identifiers  
- constructs a list of documents containing that term  
- optionally records additional statistics such as term frequency

Example output:
```text
war ~> [

    (doc1, [1]),

    (doc4, [5,17]),

    (doc19, [10]),

 ]
```
These posting lists allow the search engine to quickly retrieve all documents containing a specific word.

## Index Segment Creation

After the MapReduce stages are completed, the resulting postings lists are written to disk.

The index is typically stored in structured files such as:

```bash
postings.bin
```

Additional structures, such as lexicons or metadata files, may also be created to allow efficient lookup of terms within the postings file.  
Persisting the index to disk allows the search engine to load and query the index without rebuilding it each time the system starts.

## Scalability Considerations

Processing millions of documents can exceed the memory limits of a single machine. Therefore, the indexing pipeline must consider techniques that allow the system to scale Possible approaches include:

- external sorting5, which allows large datasets to be processed using disk-based sorting  
- segment merging6, where smaller index segments are combined into larger ones  
- distributed processing7, which enables multiple machines to process different portions of the dataset

These techniques allow the system to handle large document collections while maintaining efficient indexing performance.
---
# Query Processing Pipeline

## Purpose of Query Processing

The purpose of the Query Processing Pipeline is to transform a user query into a ranked list of relevant documents. When a user submits a query, the system must process the query, retrieve candidate documents from the index, rank those documents by relevance, and return the most relevant results.

The overall query processing workflow can be summarized as follows:

`user query ~> processed query ~> index lookup ~> ranking ~> results`

This pipeline enables fast retrieval of documents containing the requested terms without scanning the entire dataset.

## Query Input

The query entering the pipeline undergoes the same preprocessing steps that were applied to the documents during indexing. This ensures consistency between query terms and indexed tokens.

The query processing stage performs the following steps:

- convert text to lowercase  
- remove punctuation  
- tokenize the query into words  
- optionally remove stopwords

Example Query:

`"War in Europe 1914" ~> ["war", "europe", "1914"]`

Normalizing the query in this way improves matching accuracy and ensures that the query terms correspond directly to the tokens stored in the index.

## Term Lookup

After preprocessing the query, each term is looked up in the lexicon, which maps terms to their corresponding postings lists in the index.

The lexicon returns the offset location of the postings list for the requested term. Using this offset, the system loads the postings list from disk.  
Example:  

`war ~> [doc1, doc5, doc19]`

`europe ~> [doc2, doc5]`

The engine will look up as the following to achieve the phrase lookup

```bash
war_position = i

europe_position = i + 1

1914 = i + 2
```

That way we  can look for exact phrases and proximity phrases as well to return more relevant results.

These posting lists represent the documents that contain the queried terms and form the basis for further ranking.

## Candidate Document Retrieval

After retrieving the postings lists, the system constructs a candidate document set containing all potential documents that may satisfy the query.

Example query:  
War europe 

Postings lists:

`war ~> [(doc1, 1), (doc5, 4), (doc19, 5)]`

`europe ~> [(doc2, 4), (doc5, 15)]`

Candidate document set:

`(doc1, doc2, doc5, doc19)`

This candidate set represents the pool of documents that will be evaluated during the ranking stage.

## Ranking (BM25)

Not all candidate documents are equally relevant to the query. Therefore, the system must rank documents according to their estimated relevance.

This system uses the BM25 ranking algorithm, a widely used scoring function in modern search engines.

BM25 evaluates document relevance using several factors:

- term frequency (how often the term appears in the document)  
- document length (to avoid favoring excessively long documents)  
- inverse document frequency (how rare or informative a term is within the corpus)

For example, some documents may repeat certain words excessively in order to appear more relevant. BM25 reduces the impact of such repetition while giving more weight to informative terms that better represent the content of the document.

By combining these signals, BM25 assigns a relevance score to each candidate document.

## Top-K Selection

After scoring all candidate documents, the system selects the top-k results with the highest relevance scores.

The process involves:

- scoring each candidate document  
- sorting documents by score  
- returning the top-k highest scoring documents

Example output:

Top 5 results
```text
doc5 (score: 8.2)

doc1 (score: 6.7)

doc19 (score: 5.4)

doc110 (score: 5.2)

doc121 (score: 5.0)
```

Returning only the top-k results ensures efficient query processing while presenting the most relevant documents to the user.

## Result presentation

Once the top-ranked documents are selected, the system retrieves the corresponding metadata and displays the results to the user.

Each result may include information such as:

- newspaper title  
- publication date  
- page number  
- a short text snippet  
- a link to the OCR page

Example result:
```text
 page link

 Arizona Cholla

 Dec 24 1914

 "...the war in Europe continues..."
```
This presentation allows users to quickly identify relevant newspaper pages and access the original content.

---
# Future Improvements

## OCR Noise Handling

OCR errors can reduce search quality and limit users from retrieving the desired documents. Since the dataset is derived from scanned historical newspapers, the OCR process sometimes misinterprets characters or spacing.

For example, one of the documents contained the following OCR errors:

`Kiany ~> Many`

`NewYear ~> New Year`

Such errors can prevent queries from matching the correct terms in the index. Future improvements to address these issues may include:

- fuzzy search, allowing approximate matches for misspelled terms  
- spelling correction, to normalize incorrectly recognized words  
- edit-distance matching, to retrieve words that are similar to the query

These techniques can improve recall when searching noisy OCR datasets.

## Compression

Postings lists can become very large as the number of indexed documents increases. Without compression, storing the inverted index may require significant disk space and memory.  
To reduce index size and improve performance, compression techniques can be applied to the postings lists. Possible approaches include:

- gap encoding, which stores differences between sorted document identifiers instead of the full values  
- variable integer encoding, which represents small numbers using fewer bytes

These techniques reduce storage requirements and can improve query performance by reducing disk I/O.

## Distributed Indexing

As the dataset grows, indexing and querying may exceed the capacity of a single machine. Large-scale search systems often address this challenge through distributed architectures.

Future improvements could include:

- distributed indexing, allowing multiple machines to build the index in parallel  
- sharded index segments, where different parts of the index are stored across multiple nodes  
- parallel query processing, enabling queries to be executed across multiple shards simultaneously

These approaches allow the system to scale to much larger datasets.

## Ranking improvements

While BM25 provides strong baseline performance for document ranking, more advanced techniques can further improve retrieval quality.

Potential improvements include:

- learning-to-rank models, which use machine learning to optimize ranking based on training data  
- query expansion, which adds related terms to improve recall  
- semantic search, which captures the meaning of queries rather than relying solely on keyword matching  
- hybrid retrieval, combining traditional lexical search with vector-based semantic retrieval

These enhancements could improve result relevance, especially for complex or ambiguous queries.

These improvements highlight several directions in which the system could evolve to support larger datasets, improve search quality, and approach the capabilities of modern production search engines.

---
# Evaluation and Benchmarking

## Purpose of Evaluation

The evaluation process measures how efficiently the system constructs the index and how quickly it retrieves relevant documents in response to user queries. Evaluating system performance is essential for understanding whether the search engine operates efficiently and whether the retrieved results are useful.

Through evaluation, we can monitor the system’s behavior, identify performance bottlenecks, and determine potential areas for improvement.

The evaluation focuses on several key aspects:

- Indexing performance, including indexing time, number of documents processed, and memory usage  
- Query performance, including query latency, top-k retrieval speed, and average response time  
- System correctness, ensuring that queries return the expected documents  
- Retrieval quality, measuring how accurately the system retrieves relevant historical documents  
- These metrics provide a comprehensive view of the system’s efficiency and effectiveness.

## Dataset Size

The dataset size will be monitored and updated as the project evolves. Because the system is designed to handle large collections of historical newspapers, the initial target is to index approximately one million documents.

As the dataset grows, the following metrics will be tracked:

- total number of indexed documents  
- average number of tokens per document  
- total number of processed tokens  
- total index size on disk

Example metrics:
```text
documents indexed: 1.2 million

average tokens per document: 1,100

total tokens processed: ~1 billion
```
## Indexing Performance

Indexing performance measures how efficiently the system constructs the inverted index from the dataset.

Key metrics include:

- total indexing time, representing how long it takes to build the index  
- documents processed per second, indicating the throughput of the indexing pipeline  
- memory usage, measuring the system’s resource consumption during indexing


Monitoring these metrics helps evaluate whether the indexing pipeline can scale efficiently when processing large document collections.

## Query Latency

Query latency measures how long it takes for the search engine to process a user query and return results.

Important metrics include:

- average query response time, representing the typical query execution time  
- worst-case response time, measuring performance under less favorable conditions  
- top-k retrieval speed, indicating how quickly the system can identify the highest ranked results

Example performance:
```text
average query time: 40 ms

top-10 results retrieval

Low query latency is essential for providing a responsive search experience.
```
## Retrieval Quality 

In addition to system performance, it is important to evaluate the quality of the search results.

Retrieval quality measures how accurately the search engine returns relevant documents for a given query. For this project, Mean Average Precision (MAP) will be used as a primary evaluation metric.

MAP evaluates how well the ranking algorithm orders relevant documents near the top of the result list across multiple queries.

By measuring retrieval quality, we can assess whether the search engine successfully retrieves meaningful historical newspaper pages in response to user queries.

## 

## Conclusion

This project presents the design and implementation of a searchable archive for historical newspapers using a scalable indexing architecture. Historical newspaper collections contain valuable insights into past events, public discourse, and societal perspectives. However, the large volume of available documents makes manual exploration extremely difficult. The system described in this document addresses this challenge by enabling efficient search over large collections of OCR-extracted newspaper pages.

The proposed architecture processes historical newspaper datasets from the Library of Congress and transforms raw OCR text into a searchable inverted index. Through a structured pipeline consisting of document parsing, text preprocessing, index construction, and query processing, the system enables fast retrieval of relevant documents based on user queries. The MapReduce-style indexing pipeline efficiently converts large volumes of text into posting lists, while the query processing pipeline retrieves and ranks candidate documents using the BM25 ranking algorithm.

The system demonstrates how large-scale textual datasets can be processed and indexed using well-established information retrieval techniques. By leveraging inverted indexing, efficient query processing, and scalable data structures, the system is capable of supporting fast lookups across large historical corpora.

Although the system provides a functional search engine for historical newspaper archives, several areas for improvement remain. Future work may include enhanced OCR error handling, improved ranking models, index compression techniques, and distributed indexing architectures. These improvements would allow the system to scale further and improve the accuracy and usability of the search results.

Overall, this project illustrates how modern information retrieval techniques can be applied to historical datasets, enabling researchers, historians, and the public to explore archival newspaper collections more efficiently.  
