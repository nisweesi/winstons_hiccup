# scripts/run_parser.py

from pathlib import Path

from src.preprocessing.tokenizer import tokenize
from src.preprocessing.normalizer import normalize
from src.parsing.parser import parse_corpus


def parse():
    input_dir = Path("data/raw/")
    output_path = Path("data/processed/parsed/parsed_documents.jsonl")

    parse_corpus(input_dir, output_path)


def process(text):
    doc = tokenize(text)
    return normalize(doc)


def main():
    parse()


if __name__ == "__main__":
    main()
