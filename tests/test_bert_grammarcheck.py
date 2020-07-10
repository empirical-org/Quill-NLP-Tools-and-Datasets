from quillnlp.grammar.grammarcheck import SpaCyGrammarChecker
from quillnlp.grammar.unsupervised import UnsupervisedGrammarChecker


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
