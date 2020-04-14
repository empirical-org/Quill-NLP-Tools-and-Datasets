import requests

from quillnlp.grammar.grammarcheck import SpaCyGrammarChecker, BertGrammarChecker
from private import BING_URL, BING_KEY


def correct_sentence_with_bing(sentence):
    data = {'text': sentence}

    params = {
        'mkt': 'en-us',
        'mode': 'proof'
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Ocp-Apim-Subscription-Key': BING_KEY,
    }

    response = requests.post(BING_URL, headers=headers, params=params, data=data).json()
    print(response)

    corrections = []
    for error in response["flaggedTokens"]:
        if len(error["suggestions"]) > 0:
            corrections.append((error["offset"], error["token"], error["suggestions"][0]["suggestion"]))

    corrections.sort(reverse=True)

    for offset, token, replacement in corrections:
        sentence = sentence[:offset] + replacement + sentence[offset+len(token):]

    return sentence


def test_fragment():
    checker = SpaCyGrammarChecker("models/spacy_grammar")

    text = "Mix the sugar and butter. Then, the flour slowly."
    errors = checker.check(text)

    assert len(errors) == 1
    assert errors[0].type == "Fragment"


def test_this_vs_that():
    checker = SpaCyGrammarChecker("models/spacy_grammar")

    text = "This man over there is my brother."
    errors = checker.check(text)

    assert len(errors) == 1
    assert errors[0].type == "This versus that"


def test_this_vs_that2():
    checker = SpaCyGrammarChecker("models/spacy_grammar")

    text = "This library over there is very popular."
    errors = checker.check(text)

    assert len(errors) == 1
    assert errors[0].type == "This versus that"


def test_question_mark():

    # This sentence should not have a question mark error
    text = "The Sister's are still on the run from Santiago, as are we."
    checker = SpaCyGrammarChecker("models/spacy_grammar")

    errors = checker.check(text)

    assert len(errors) == 1


def test_woman_vs_women():
    checker = SpaCyGrammarChecker("models/spacy_grammar")

    text = "These womans were hilarious."
    errors = checker.check(text)

    assert len(errors) == 1
    assert errors[0].type == "Woman versus women"


def test_possessive_pronouns():
    checker = SpaCyGrammarChecker("models/spacy_grammar")

    text = "I danced at Leslie's and them party."
    errors = checker.check(text)

    assert len(errors) == 1
    assert errors[0].type == "Possessive pronouns"


def test_possessive_pronouns2():
    checker = SpaCyGrammarChecker("models/spacy_grammar")

    text = "I danced at Leslie's and their's party."
    errors = checker.check(text)

    assert len(errors) == 1
    assert errors[0].type == "Possessive pronouns"


def test_yesno():

    checker = SpaCyGrammarChecker("models/spacy_grammar")

    sentences = [("No that's not a problem.", 1),
                 ("That's no problem.", 0)]

    for sentence, num_errors in sentences:
        found_errors = checker.check(sentence)
        assert len(found_errors) == num_errors