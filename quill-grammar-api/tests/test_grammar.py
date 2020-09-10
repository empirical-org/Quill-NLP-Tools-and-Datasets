from grammar.pipeline import GrammarPipeline


def test_grammar_pipeline1():
    pipeline = GrammarPipeline()

    sentence = "We should stop eating meat, because meat are bad."
    prompt = "We should stop eating meat, because"

    errors = pipeline.check(sentence, prompt)
    print(errors)

    assert len(errors) == 2


def test_grammar_pipeline2():
    pipeline = GrammarPipeline()

    sentence = "We should stop eating meat, because we eaten too much already."
    prompt = "We should stop eating meat, because"

    errors = pipeline.check(sentence, prompt)
    print(errors)

    assert len(errors) == 2


def test_grammar_pipeline3():
    pipeline = GrammarPipeline()

    sentence = "We should stop eating meat, because there are several woman in the room."
    prompt = "We should stop eating meat, because"

    errors = pipeline.check(sentence, prompt)
    print(errors)

    assert len(errors) == 1


def test_grammar_pipeline4():
    sentence = "The new line be called Line 4."
    prompt = ""

    pipeline = GrammarPipeline()
    errors = pipeline.check(sentence, prompt)
    print(errors)

    assert len(errors) == 2


def test_grammar_pipeline5():
    sentence = "More man are standing in the backyard."
    prompt = ""

    pipeline = GrammarPipeline()
    errors = pipeline.check(sentence, prompt)
    print(errors)

    assert len(errors) == 1


def test_grammar_pipeline6():
    sentence = "Two woman wrote the book."
    prompt = ""

    pipeline = GrammarPipeline()
    errors = pipeline.check(sentence, prompt)
    print(errors)

    assert len(errors) == 1
