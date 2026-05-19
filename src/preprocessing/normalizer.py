def normalize(doc):
    tokens = [
        "<NUM>" if token.like_num else token.lemma_.lower()
        for token in doc
        if token.is_alpha and not token.is_stop and not token.is_punct
    ]

    return tokens
