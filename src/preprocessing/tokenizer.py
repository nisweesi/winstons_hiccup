import spacy
from spacy.tokens import Doc

nlp = spacy.load("en_core_web_sm")


def tokenize(text: str) -> Doc:
    return nlp(text)
