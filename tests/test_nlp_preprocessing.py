from quillnlp.preprocess import lemmatize


def test_lemmatization():
    sentence = "He has written two books."
    lemmas = lemmatize(sentence, remove_stopwords=False)

    assert lemmas == ["-pron-", "have", "write", "two", "book", "."]


def test_lemmatization_remove_stopwords():
    sentence = "He has written two books."
    lemmas = lemmatize(sentence, remove_stopwords=True)

    assert lemmas == ["-pron-", "write", "book", "."]
