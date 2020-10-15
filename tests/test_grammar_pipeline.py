import yaml

from quillgrammar.grammar.pipeline import GrammarPipeline
from quillgrammar.grammar.constants import GrammarError

config_file = "tests/config.yaml"


def test_grammar_pipeline1():

    sentence = "By the time Fatma retired from the United States Navy, she'd earned 899830810830 medals!"

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    errors = pipeline.check(sentence, "")

    # We only want to find the "Commas in numbers" error
    assert len(errors) == 1



def test_grammar_pipeline3():

    sentence = "The construction worker, who is working right outside of our building, work all night."
    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    errors = pipeline.check(sentence, "")

    assert errors[0].type == GrammarError.SVA_SEPARATE.value


def test_grammar_pipeline4():

    sentence = "Nancy had been considering moving out of the apartment " \
               "when she finally decided to re-sign the lease with her old roommates."

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    errors = pipeline.check(sentence, "")

    assert len(errors) == 0


def test_grammar_pipeline5():

    sentence = "What kitchen appliance do you use every day"

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    errors = pipeline.check(sentence, "")

    assert errors[0].type == GrammarError.QUESTION_MARK.value


def test_grammar_pipeline6():

    sentence = "It been done, the crook said."

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    errors = pipeline.check(sentence, "")

    assert errors[0].type == GrammarError.PASSIVE_PERFECT_WITHOUT_HAVE.value


def test_grammar_pipeline_for_sva_no_errors():

    sentences = [("Large amounts of meat consumption are harming the environment "
                  "because it generates 30 to 50 gallons of methane daily contributing "
                  "to greenhouse gases and global warming.",
                  "Large amounts of meat consumption are harming the environment because"),
                 ('Alison Bechdel’s memoir has been challenged in certain '
                  'communities, so it is important to recognize the dangerous '
                  'precedent that will be set by banning her work because it '
                  '"further stigmatizes and marginalizes LGBTQ youth and '
                  'fosters an atmosphere of intolerance."',
                  'Alison Bechdel’s memoir has been challenged in certain '
                  'communities, so'),
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities, but one advocacy group is fighting back, "
                  "claiming that the book resonates with the experiences "
                  "of many LGBT youth.",
                  'Alison Bechdel’s memoir has been challenged in certain '
                  'communities, so'),
                 ("Large amounts of meat consumption are harming the "
                  "environment because it accumulates in the atmosphere "
                  "and traps in heat, leading to global warming.",
                  "Large amounts of meat consumption are harming the "
                  "environment because"),
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities, so the battle rages on between freedom of "
                  "expression and holding on to moral values.",
                  'Alison Bechdel’s memoir has been challenged in certain '
                  'communities, so'),
                 ("Large amounts of meat consumption are harming the "
                  "environment, so Impossible Burger has developed a "
                  "plant-based burger that tastes similar to beef.",
                  "Large amounts of meat consumption are harming the "
                  "environment because"),
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities, but advocacy groups are fighting back "
                  "because it resonates with many youth experiences.",
                  'Alison Bechdel’s memoir has been challenged in certain '
                  'communities, so'),
                 ("Large amounts of meat consumption are harming the "
                  "environment, but if they ate seaweed more often, "
                  "they would burp less.",
                  "Large amounts of meat consumption are harming the "
                  "environment because"),
#                 ("Young kids’ lives often revolve around seeing their "
#                  "friends and exploring the world, so being forced to "
#                  "shelter at home with their family can feel really "
#                  "hard.", ""),
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities because it was “promoting the gay and lesbian "
                  "lifestyle.”", "Alison Bechdel’s memoir has been "
                  "challenged in certain communities because"),
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities, but memories are too pornographic for schools.",
                  "Alison Bechdel’s memoir has been challenged in certain "
                  "communities, but ")]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt in sentences:
        errors = pipeline.check(sentence, prompt)

        assert len(errors) == 0


def test_grammar_pipeline_for_sva_errors():

    sentences = [("There exist another way for all of us to live.", ""),
                 ("That ballad, performed by the one and only Katy Perry, "
                  "am moving the audience to tears.", ""),
                 ("I are coming home", ""),
                 ("Lord Howe Island hug a turquoise lagoon rimmed with the "
                  "world’s southernmost coral reef.", ""),
                 ("Located at the exact point where Switzerland, France and "
                  "Germany meet, Basel straddle a bend of the Rhine.", "")]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt in sentences:
        errors = pipeline.check(sentence, prompt)

        assert len(errors) > 0


def test_grammar_pipeline_for_question_marks():

    sentences = [("Alison Bechdel’s memoir has been challenged in certain "
                  "communities, but it continues to resonate as a personal "
                  "coming of age story,",
                  "Alison Bechdel’s memoir has been challenged in certain "
                  "communities, but")]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt in sentences:
        errors = pipeline.check(sentence, prompt)

        assert len(errors) == 1
        assert errors[0].type == GrammarError.PUNCTUATION.value


def test_grammar_pipeline_for_subject_pronouns():

    sentences = [("Our mom has been fixing the sink for the past few hours, but I think it's still leaky.",
                  "", 0),
                 ("Our are going to rise up in the name of justice.", "", 1)]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, num_errors in sentences:
        errors = set([e.type for e in pipeline.check(sentence, prompt)])

        assert len(errors) == num_errors


def test_grammar_pipeline_spacing():

    sentences = [("Eastern Michigan University cut women's tennis and "
                  "softball because it faced a budget shortfall of least "
                  "$4.5 million in 2018.",
                  "", 0),
                 ("There are 1.5ish million cows.", "", 0),
                 ("Large amounts of meat consumption are harming the environment "
                  "because there are 1.5 billion cows.",
                  "", 0),
                 ("Methane from cow burps harms the environment, but it "
                  "produces about 14.5% of the worlds green houses gas .",
                  "", 1),
                 ("Methane from cow burps harms the environment, but it "
                  "produces about 14.5 % of the worlds green houses gas.",
                  "", 1)
                 ]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, num_errors in sentences:
        errors = set([e.type for e in pipeline.check(sentence, prompt)])

        print("Identified errors:", errors)
        assert len(errors) == num_errors


def test_grammar_pipeline_articles():

    sentences = [("Large amounts of meat consumption are harming the "
                  "environment, but an impossible burger generates 89% "
                  "fewer greenhouse gases. ",
                  "Large amounts of meat consumption are harming the "
                  "environment, but ", 0)
                 ]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, num_errors in sentences:
        errors = set([e.type for e in pipeline.check(sentence, prompt)])

        print("Identified errors:", errors)
        assert len(errors) == num_errors


def test_grammar_pipeline_capitalization():

    sentences = [("Methane from cow burps harms the environment, but BY "
                  "MAKING DIFFERENT FEED CHOICES, IT WILL REDUCE EFFECTS "
                  "OF METHANE.",
                  "Methane from cow burps harms the environment, but", 1),
                 ("Methane from cow burps harms the environment, but BY "
                  "MAKING DIFFERENT FEED CHOICES, IT WILL REDUCE EFFECTS "
                  "OF METHANE.", "", 0)
                 ]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, num_errors in sentences:
        errors = set([e.type for e in pipeline.check(sentence, prompt)])

        print("Identified errors:", errors)
        assert len(errors) == num_errors


def test_grammar_pipeline_its():

    sentences = [
#                 ("Alison Bechdel’s memoir has been challenged in certain "
#                  "communities because some people believe that it's "
#                  "pornographic and promotes gay and lesbian lifestyle.",
#                  "Alison Bechdel’s memoir has been challenged in certain "
#                  "communities because", 0),
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities because of its pornographic style.",
                  "Alison Bechdel’s memoir has been challenged in certain "
                  "communities because", 0),
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities because it's pornographic.",
                  "Alison Bechdel’s memoir has been challenged in certain "
                  "communities because", 1),
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities because of it's pornographic style.",
                  "Alison Bechdel’s memoir has been challenged in certain "
                  "communities because", 1)]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, num_errors in sentences:
        errors = set([e.type for e in pipeline.check(sentence, prompt)])

        print("Identified errors:", errors)
        assert len(errors) == num_errors
