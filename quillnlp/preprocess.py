import spacy

nlp = spacy.load("en")

STOPWORDS = set(["have", "-pron-", "not", "i.e."])


def lemmatize(text, lowercase=True, remove_stopwords=True):
    """ Return the lemmas of the tokens in a text. """
    doc = nlp(text)
    if lowercase and remove_stopwords:
        lemmas = [t.lemma_.lower() for t in doc if not (t.is_stop or t.orth_.lower() in STOPWORDS)]
    elif lowercase:
        lemmas = [t.lemma_.lower() for t in doc]
    elif remove_stopwords:
        lemmas = [t.lemma_ for t in doc if not (t.is_stop or t.orth_.lower() in STOPWORDS)]
    else:
        lemmas = [t.lemma_ for t in doc]

    return lemmas