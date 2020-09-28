import yaml

from quillgrammar.grammar.pipeline import GrammarPipeline

config_file = "tests/config.yaml"


def test_grammar_pipeline1():

    sentence = "By the time Fatma retired from the United States Navy, she'd earned 899830810830 medals!"

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    errors = pipeline.check(sentence, "")

    # We only want to find the "Commas in numbers" error
    assert len(errors) == 1


def test_grammar_pipeline2():

    sentence = "My mom likes to tell me stories about when she and her brother were young and lived in New Mexico."
    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    errors = pipeline.check(sentence, "")

    # We only want to find the "Commas in numbers" error
    assert len(errors) == 0
