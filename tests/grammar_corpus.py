from spacy.gold import biluo_tags_from_offsets

from quillnlp.grammar import corpus
from quillnlp.grammar.spacy import nlp


def test_possessive_replacement1():
    sentence = "The country's wealth is growing."
    doc = nlp(sentence)
    text, entities = corpus.replace_possessive_by_plural("POSSESSIVE", doc)

    assert text == "The countrys wealth is growing."
    assert entities == [(4, 12, "POSSESSIVE")]


def test_possessive_replacement2():
    sentence = "Mum's party was fantastic."
    doc = nlp(sentence)
    text, entities = corpus.replace_possessive_by_plural("POSSESSIVE", doc)
    biluo_tags = biluo_tags_from_offsets(nlp(text), entities)
    tags = [t.split("-")[-1] for t in biluo_tags]

    assert text == "Mums party was fantastic."
    assert entities == [(0, 4, "POSSESSIVE")]
    assert tags == ["POSSESSIVE", "O", "O", "O", "O"]


def test_double_possessive_replacement():
    sentence = "My best friend's car and her sister's bike."
    doc = nlp(sentence)
    text, entities = corpus.replace_possessive_by_plural("POSSESSIVE", doc)

    assert text == "My best friends car and her sisters bike."
    assert entities == [(8, 15, 'POSSESSIVE'), (28, 35, 'POSSESSIVE')]


def test_plural_replacement1():
    sentence = "There are over 200 countries in the world."
    doc = nlp(sentence)
    text, entities = corpus.replace_plural_by_possessive("POSSESSIVE", doc)
    biluo_tags = biluo_tags_from_offsets(nlp(text), entities)
    tags = [t.split("-")[-1] for t in biluo_tags]

    assert text == "There are over 200 country's in the world."
    assert entities == [(19, 28, "POSSESSIVE")]
    assert tags == ["O", "O", "O", "O", "POSSESSIVE", "POSSESSIVE", "O", "O", "O", "O"]


def test_plural_replacement2():
    sentence = "Cats are great."
    doc = nlp(sentence)
    text, entities = corpus.replace_plural_by_possessive("POSSESSIVE", doc)

    assert text == "Cat's are great."
    assert entities == [(0, 5, "POSSESSIVE")]


def test_double_plural_replacement():
    sentence = "I bet you had hundreds of proposals when you were my age."
    doc = nlp(sentence)
    text, entities = corpus.replace_plural_by_possessive("POSSESSIVE", doc)

    assert text == "I bet you had hundred's of proposal's when you were my age."
    assert entities == [(14, 23, 'POSSESSIVE'), (27, 37, 'POSSESSIVE')]


def test_VBZ_VB_replacement():
    sentence = "He goes home."
    doc = nlp(sentence)
    text, entities = corpus.replace_verb_form("VBZ", "VB", "VERB", doc)

    assert text == "He go home."
    assert entities == [(3, 5, "VERB")]


def test_VBP_VBZ_replacement():
    sentence = "We go home."
    doc = nlp(sentence)
    text, entities = corpus.replace_verb_form("VBP", "VBZ", "VERB", doc)

    assert text == "We goes home."
    assert entities == [(3, 7, "VERB")]


def test_VBP_VB_replacement():
    """ If the two verb forms happen to be the same, the list of errors should be empty."""
    sentence = "We go home."
    doc = nlp(sentence)
    text, entities = corpus.replace_verb_form("VBP", "VB", "VERB", doc)

    assert text == "We go home."
    assert entities == []


def test_ADV_replacement1():
    sentence = "She sings beautifully."
    doc = nlp(sentence)
    text, entities = corpus.replace_adverb_by_adjective("ADV", doc)

    assert text == "She sings beautiful."


def test_ADV_replacement2():
    sentence = "Beautifully put."
    doc = nlp(sentence)
    text, entities = corpus.replace_adverb_by_adjective("ADV", doc)

    assert text == "Beautiful put."


def test_find_phrase1():
    sentence = "It's great."
    doc = nlp(sentence)
    assert corpus.contains_phrase(["it", "'s"], doc) is True


def test_find_phrase2():
    sentence = "Of course it's great."
    doc = nlp(sentence)
    assert corpus.contains_phrase(["it", "'s"], doc) is True


def test_find_phrase3():
    sentence = "Of course it's"
    doc = nlp(sentence)
    assert corpus.contains_phrase(["it", "'s"], doc) is True


def test_find_phrase4():
    sentence = "Of course it is"
    doc = nlp(sentence)
    assert corpus.contains_phrase(["it", "'s"], doc) is False
