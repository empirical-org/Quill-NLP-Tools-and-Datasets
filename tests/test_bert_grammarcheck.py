from quillnlp.grammar.grammarcheck import SpaCyGrammarChecker
from quillnlp.grammar.unsupervised import UnsupervisedGrammarChecker
from quillnlp.grammar.models.albert_predictor import BertPredictor


def test_check1():

    sentence = "I've been told that ponies are just small horses, but apparently I'm wrong according to the American Pony Association."

    checker = UnsupervisedGrammarChecker()
    results = checker.check(sentence)
    assert results == []


def test_check2():
    sentence = "My dentist thinks that I am more susceptible to cavities than my sister, who doesn't drink coffee."

    checker = UnsupervisedGrammarChecker()
    results = checker.check(sentence)
    print(results)
    assert results == []


def test_check3():
    sentence = "Crimea has been took."

    checker = UnsupervisedGrammarChecker()
    results = checker.check(sentence)
    print(results)


def test_check4():

    p = BertPredictor.from_path("/samba/public/models/albert-large")
    results = p.correct_instance({'sentence': 'Crimea has been took.', 'targets': [{'token': 'has', 'start': 7, 'alternatives': ['have']}, {'token': 'been', 'start': 11, 'alternatives': ['is', 'are', 'was']}, {'token': 'took', 'start': 16, 'alternatives': ['taken']}, {'token': '.', 'start': 20, 'alternatives': ['?']}]})

    print(results)

