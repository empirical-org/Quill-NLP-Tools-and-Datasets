import requests

from grammar.constants import GrammarError


def test_deployment1():
    data = {"sentence": "Does he love me.", "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 15


def test_deployment2():
    data = {"sentence": "Yes, he love me.", "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 8


def test_deployment3():
    data = {"sentence": "Yes, he loves me.", "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] is None


def test_deployment4():
    sentence = "Crimea has been took."
    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 16


def test_deployment5():
    sentence = "The new line be called Line 4."
    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 13


def test_deployment6():
    sentence = "The lion is knowed for its ferocious roar."
    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 12


def test_deployment7():
    sentence = "I had forgot to pay the bill."
    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 6
    assert r.json()["type"] == GrammarError.PAST_TENSE_INSTEAD_OF_PARTICIPLE.value


def test_deployment8():
    sentence = "I breaked the lamp."
    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 2
    assert r.json()["type"] == GrammarError.INCORRECT_IRREGULAR_PAST_TENSE.value


def test_deployment9():
    sentence = "She had breaked all the windows."
    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 8
    assert r.json()["type"] == GrammarError.PERFECT_TENSE_WITH_INCORRECT_SIMPLE_PAST.value


def test_deployment10():
    sentence = "The dog found it's food."
    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 14
    assert r.json()["model"] == "spaCy"
    assert r.json()["type"] == GrammarError.ITS_IT_S.value


def test_deployment11():
    sentence = "I applied at two company's."
    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 24
    assert r.json()["model"] == "rules"
    assert r.json()["type"] == GrammarError.PLURAL_VERSUS_POSSESSIVE_NOUNS.value


def test_deployment12():
    sentence = "I been working very hard."
    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 2
    assert r.json()["model"] == "spaCy"
    assert r.json()["type"] == GrammarError.PERFECT_PROGRESSIVE_WITHOUT_HAVE.value


def test_deployment13():
    sentence = "I been on holiday in France."
    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 2
    assert r.json()["model"] == "spaCy"
    assert r.json()["type"] == GrammarError.PERFECT_WITHOUT_HAVE.value


def test_deployment14():
    sentence = "I be working very hard."
    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 2
    assert r.json()["model"] == "spaCy"
    assert r.json()["type"] == GrammarError.PERFECT_PROGRESSIVE_WITH_INCORRECT_BE_AND_WITHOUT_HAVE.value


def test_deployment15():
    sentence = "More man are standing in the backyard."
    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 5
    assert r.json()["model"] == "lm"
    assert r.json()["type"] == GrammarError.MAN_MEN.value


def test_deployment16():
    sentence = "Two woman wrote the book."

    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 4
    assert r.json()["model"] == "lm"
    assert r.json()["type"] == GrammarError.WOMAN_WOMEN.value


def test_deployment17():
    sentence = "You are taller then me."

    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 15
    assert r.json()["type"] == GrammarError.THAN_THEN.value


def test_deployment18():
    sentence = "Him is home."

    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 0
    assert r.json()["model"] == "rules"
    assert r.json()["type"] == GrammarError.SUBJECT_PRONOUN.value


def test_deployment19():
    sentence = "I saw he in town."

    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 6
    assert r.json()["model"] == "rules"
    assert r.json()["type"] == GrammarError.OBJECT_PRONOUN.value


def test_deployment20():
    sentence = "He be helped by his mother."

    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 3
    assert r.json()["model"] == "lm"
    assert r.json()["type"] == GrammarError.PASSIVE_WITH_INCORRECT_BE.value


def test_deployment21():
    sentence = "The book was wrote last year."

    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 13
    assert r.json()["model"] == "lm"
    assert r.json()["type"] == GrammarError.INCORRECT_PAST_TENSE_AS_PARTICIPLE_IN_PASSIVE.value


def test_deployment22():
    sentence = "The book has been wrote last year."

    data = {"sentence": sentence, "prompt": ""}
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=data)

    print(r.json())
    assert r.json()["index"] == 18
    assert r.json()["model"] == "lm"
    assert r.json()["type"] == GrammarError.PASSIVE_PERFECT_WITH_INCORRECT_PARTICIPLE.value
