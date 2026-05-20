from spacy.tokens import Doc


def normalize(doc: Doc) -> list[tuple[str, int]]:
    tokens = []
    position = 0

    for token in doc:
        if token.is_stop or token.is_punct or token.is_space:
            continue

        if token.like_num:
            tokens.append((token.text.lower(), position))
            position += 1

        elif token.is_alpha:
            tokens.append((token.lemma_.lower(), position))
            position += 1

    return tokens
