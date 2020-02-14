import csv

from collections import Counter

from quillnlp.grammar.grammarcheck import GrammarChecker


error_map = {"WOMAN": "Woman versus women",
             "ITS": "Its versus it's",
             "THEN": "Than versus then",
             "VERB": "Subject-verb agreement",
             "POSSESSIVE": "Plural versus possessive nouns",
             "CHILD": "Child versus children",
             "Possessive nouns": "Plural versus possessive nouns", # from the manual labelling
             "Plural possessive nouns": "Plural versus possessive nouns",
             "Irregular past tense verbs": "Verb tense", # from the manual labelling
             "Those versus these": "This versus that",
             "Adverbs": "Adverbs versus adjectives",
             "Adjectives versus adverbs": "Adverbs versus adjectives"
             }


def test_fragment():
    checker = GrammarChecker("models/spacy_grammar")

    text = "Mix the sugar and butter. Then, the flour slowly."
    errors = checker.check(text)

    assert len(errors) == 1
    assert errors[0].type == "Fragment"


def test_this_vs_that():
    checker = GrammarChecker("models/spacy_grammar")

    text = "This man over there is my brother."
    errors = checker.check(text)

    assert len(errors) == 1
    assert errors[0].type == "This versus that"


def test_this_vs_that2():
    checker = GrammarChecker("models/spacy_grammar")

    text = "This library over there is very popular."
    errors = checker.check(text)

    assert len(errors) == 1
    assert errors[0].type == "This versus that"


def test_question_mark():

    # This sentence should not have a question mark error
    text = "The Sister's are still on the run from Santiago, as are we."
    checker = GrammarChecker("models/spacy_grammar")

    errors = checker.check(text)

    assert len(errors) == 1


def test_woman_vs_women():
    checker = GrammarChecker("models/spacy_grammar")

    text = "These womans were hilarious."
    errors = checker.check(text)

    assert len(errors) == 1
    assert errors[0].type == "Woman versus women"


def test_possessive_pronouns():
    checker = GrammarChecker("models/spacy_grammar")

    text = "I danced at Leslie's and them party."
    errors = checker.check(text)

    assert len(errors) == 1
    assert errors[0].type == "Possessive pronouns"


def test_possessive_pronouns2():
    checker = GrammarChecker("models/spacy_grammar")

    text = "I danced at Leslie's and their's party."
    errors = checker.check(text)

    assert len(errors) == 1
    assert errors[0].type == "Possessive pronouns"


def test_yesno():

    checker = GrammarChecker("models/spacy_grammar")

    sentences = [("No that's not a problem.", 1),
                 ("That's no problem.", 0)]

    for sentence, num_errors in sentences:
        found_errors = checker.check(sentence)
        assert len(found_errors) == num_errors


def test_grammar():

    checker = GrammarChecker("models/spacy_grammar")

    # Read error input
    data = []
    with open("tests/data/grammar.tsv") as i:
        reader = csv.reader(i, delimiter="\t")
        for row in reader:
            if len(row) > 1:
                data.append(row)

    results = {}

    error_counts = Counter()
    with open("results.tsv", "w") as o:
        for item in data:
            sentence = item[0]
            errors = set([error_map.get(e.strip(), e.strip()) for e in item[1:] if len(e.strip()) > 0])
            error_counts.update(errors)

            found_errors = checker.check(sentence)
            found_error_types = set([error_map.get(e[2], e[2]) for e in found_errors])

            for error_type in errors:
                if error_type not in results:
                    results[error_type] = {"tp": 0, "fp": 0, "fn": 0}

                if error_type in found_error_types:
                    results[error_type]["tp"] += 1
                else:
                    results[error_type]["fn"] += 1

            for found_error in found_error_types:
                if found_error not in errors:
                    if found_error not in results:
                        results[found_error] = {"tp": 0, "fp": 0, "fn": 0}

                    results[found_error]["fp"] += 1

            o.write("\t".join([sentence, ",".join(errors), ",".join(found_error_types)]) + "\n")


    error_types = sorted(list(results.keys()))
    for error_type in error_types:
        tp = results[error_type]["tp"]
        fp = results[error_type]["fp"]
        fn = results[error_type]["fn"]
        support = error_counts[error_type]

        precision = tp/(tp+fp) if (tp+fp) > 0 else 0
        recall = tp/(tp+fn) if (tp+fn) > 0 else 0
        fscore = 2*precision*recall/(precision+recall) if precision+recall > 0 else 0

        print(f"{error_type}\t{precision}\t{recall}\t{fscore}\t{support}")


def test_grammar2():

    checker = GrammarChecker("models/spacy_grammar")

    # Read error input
    data = []
    with open("tests/data/grammar2.tsv") as i:
        for line in i:
            data.append(line.strip())

    with open("results2.tsv", "w") as o:
        for item in data:

            found_errors = checker.check(item)
            found_error_types = set([error_map.get(e[2], e[2]) for e in found_errors])

            o.write("\t".join([item, ",".join(found_error_types)]) + "\n")

