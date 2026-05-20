import json
from pathlib import Path

path = Path("data/processed/parsed/parsed_documents.jsonl")

doc_ids = set()
num_docs = 0
empty_text = 0
bad_lines = 0

with path.open("r", encoding="utf-8") as f:
    for line_no, line in enumerate(f, start=1):
        try:
            doc = json.loads(line)
        except json.JSONDecodeError:
            bad_lines += 1
            print("Bad JSON line:", line_no)
            continue

        num_docs += 1

        required = ["doc_id", "newspaper_id", "date", "edition", "page", "text", "path"]
        missing = [field for field in required if field not in doc]

        if missing:
            print(f"Line {line_no} missing fields:", missing)

        if doc["doc_id"] in doc_ids:
            print("Duplicate doc_id:", doc["doc_id"])

        doc_ids.add(doc["doc_id"])

        if not doc["text"].strip():
            empty_text += 1

print("documents:", num_docs)
print("unique doc_ids:", len(doc_ids))
print("empty text docs:", empty_text)
print("bad JSON lines:", bad_lines)
