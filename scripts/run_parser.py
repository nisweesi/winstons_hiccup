from src.preprocessing.tokenizer import tokenize
from src.preprocessing.normalizer import normalize


def process(text):
    doc = tokenize(text)
    return normalize(doc)
