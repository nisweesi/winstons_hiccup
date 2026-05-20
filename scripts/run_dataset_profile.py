from pathlib import Path
from datetime import date
import json

ARCHIVES_DIR = Path("data/raw/archives")
EXTRACTED_DIR = Path("data/raw/extracted")
RESULTS_DIR = Path("results/dataset")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def dir_size(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def extract_date_from_path(path: Path):
    parts = path.parts

    for i in range(len(parts) - 3):
        year, month, day = parts[i], parts[i + 1], parts[i + 2]

        if year.isdigit() and month.isdigit() and day.isdigit():
            if len(year) == 4 and len(month) == 2 and len(day) == 2:
                return date(int(year), int(month), int(day)).isoformat()

    return None


txt_files = list(EXTRACTED_DIR.rglob("*.txt"))

dates = []
char_counts = []
token_counts = []

for path in txt_files:
    d = extract_date_from_path(path)
    if d:
        dates.append(d)

    text = path.read_text(encoding="utf-8", errors="replace")
    char_counts.append(len(text))
    token_counts.append(len(text.split()))

stats = {
    "corpus_slice": "loc_ocr_14_archives_v1",
    "num_archives": len(list(ARCHIVES_DIR.glob("*.tar.bz2"))),
    "compressed_size_bytes": dir_size(ARCHIVES_DIR),
    "extracted_size_bytes": dir_size(EXTRACTED_DIR),
    "num_ocr_pages": len(txt_files),
    "date_min": min(dates) if dates else None,
    "date_max": max(dates) if dates else None,
    "avg_chars_per_page": sum(char_counts) / len(char_counts) if char_counts else 0,
    "avg_tokens_per_page": sum(token_counts) / len(token_counts) if token_counts else 0,
}

with open(RESULTS_DIR / "dataset_stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

print(json.dumps(stats, indent=2))
