# src/parser/document_parser.py

import json
from pathlib import Path


DEFAULT_PATH = "data/processed"


# get the doc idea and the metadata
def parse_ocr_document(path: Path) -> dict:
    """
    expected path
    data/raw/sn82015761/1914/12/24/ed-1/seq-5/ocr.txt
    """
    parts = path.parts
    newspaper_id = parts[-7]
    year = parts[-6]
    month = parts[-5]
    day = parts[-4]
    edition = parts[-3]
    seq = parts[-2]

    page = int(seq.replace("seq-", ""))

    doc_id = f"{newspaper_id}_{year}_{month}_{day}_{edition}_{seq}"

    return {
        "doc_id": doc_id,
        "newspaper_id": newspaper_id,
        "date": f"{year}-{month}-{day}",
        "edition": edition,
        "page": page,
    }


# parse on ocr.txt file
def parse_ocr_file(path: Path) -> dict:
    metadata = parse_ocr_document(path)
    text = path.read_text(encoding="utf-8", errors="replace")

    return {
        **metadata,  # unpack the dict here
        "text": text,
    }


# store the files in JSON Lines format
def write_jsonl(records: list[dict], output_path: Path = DEFAULT_PATH) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


# parse a whole folder
def parse_corpus(input_dir: Path, output_path: Path = DEFAULT_PATH) -> None:
    records = []

    for path in input_dir.rglob("ocr.txt"):
        record = parse_ocr_file(path)
        records.append(record)

    write_jsonl(records, output_path)
