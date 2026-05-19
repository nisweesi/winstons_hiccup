import spacy

nlp = spacy.load("en_core_web_sm")

def tokenize(text: str) -> list[str]:
    return nlp(text)
