import csv
import requests
import ndjson

from private import BING_URL, BING_KEY

from collections import Counter

from quillnlp.grammar.grammarcheck import SpaCyGrammarChecker, BertGrammarChecker


error_map = {"WOMAN": "Woman versus women",
             "ITS": "Its versus it's",
             "THEN": "Than versus then",
             "VERB": "Subject-verb agreement",
             "POSSESSIVE": "Plural versus possessive nouns",
             "CHILD": "Child versus children",
             "Possessive nouns": "Plural versus possessive nouns",  # from the manual labelling
             "Plural possessive nouns": "Plural versus possessive nouns",
             "Irregular past tense verbs": "Verb tense",  # from the manual labelling
             "Those versus these": "This versus that",
             "Adverbs": "Adverbs versus adjectives",
             "Adjectives versus adverbs": "Adverbs versus adjectives",
             "Subject-verb agreement (rule)": "Subject-verb agreement",
             "Subject-verb agreement (stats)": "Subject-verb agreement",
             }


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


def test_grammar_quill():

    #checker = SpaCyGrammarChecker("models/spacy_grammar20M")
    checker = BertGrammarChecker("/tmp/grammar/model.bin", "/tmp/grammar/config.json")

    # Read error input
    with open("tests/data/grammar_bing.ndjson") as i:
        data = ndjson.load(i)

    results = {}

    error_counts = Counter()
    with open("results.tsv", "w") as o:
        for item in data:
            sentence = item["original_sentence"]
            #sentence = correct_sentence_with_bing(sentence)
            errors = set([error_map.get(e.strip(), e.strip()) for e in item["original_errors"] if len(e.strip()) > 0])
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
            #time.sleep(2)

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

    checker = SpaCyGrammarChecker("models/spacy_grammar")

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


def test_grammar_pairs():
    #checker = GrammarChecker("models/spacy_grammar")
    #checker = SpaCyGrammarChecker("models/grammar20M")
    checker = BertGrammarChecker("bert_grammar2M.bin")

    # Read error input
    data = []
    with open("tests/data/grammar_valid.tsv") as i:
        for line in i:
            line = line.strip().split("\t")
            if len(line) == 3:
                data.append(line)
    results = {}

    for (error_type, correct_sentence, incorrect_sentence) in data:
        if error_type not in results:
            results[error_type] = {"cc": 0, "ci": 0, "ic": 0, "ii": 0}
        errors = checker.check(correct_sentence)
        errors = [e for e in errors if e.type.startswith(error_type)]
        print(correct_sentence)
        print(errors)
        if len(errors) == 0:
            results[error_type]["cc"] += 1
        else:
            results[error_type]["ci"] += 1
        errors = checker.check(incorrect_sentence)
        errors = [e for e in errors if e.type.startswith(error_type)]
        print(incorrect_sentence)
        print(errors)
        if len(errors) == 0:
            results[error_type]["ic"] += 1
        else:
            results[error_type]["ii"] += 1

    for error_type in results:
        correct = results[error_type]["cc"] + results[error_type]["ii"]
        incorrect = results[error_type]["ic"] + results[error_type]["ci"]
        precision = results[error_type]["cc"]/ (results[error_type]["cc"] + results[error_type]["ic"])
        recall = results[error_type]["cc"] / (results[error_type]["cc"] + results[error_type]["ci"])
        fscore = 2*precision*recall/(precision+recall)
        print(error_type, precision, recall, fscore)


def evaluate_bing_corrections(data):
    counter_before = Counter()
    counter_after = Counter()

    for item in data:
        counter_before.update(item["original_errors"])
        counter_after.update(item["errors_after_bing"])

    correction_percentage = []
    for error in counter_before:
        correction_percentage.append((1-(counter_after.get(error, 0)/counter_before.get(error)), error))

    correction_percentage.sort(reverse=True)
    print("Bing corrections")
    for (p, e) in correction_percentage:
        print(p, e)


def test_bing():

    # Read error input
    with open("tests/data/grammar_bing.ndjson") as i:
        data = ndjson.load(i)

    # Evaluate Bing corrections
    evaluate_bing_corrections(data)

    checker = SpaCyGrammarChecker("models/spacy_grammar20M")
    #checker = BertGrammarChecker("bert_grammar500k.bin")

    # Evaluate cumulative corrections
    error_counts = Counter()
    results = {}
    with open("results_bing_quill.tsv", "w") as o:
        for item in data:
            sentence = item["sentence_after_bing"]
            errors = set([error_map.get(e.strip(), e.strip()) for e in item["original_errors"] if len(e.strip()) > 0])
            error_counts.update(errors)

            # Get the errors our own grammar model finds
            quill_errors = checker.check(sentence)
            quill_error_types = set([error_map.get(e[2], e[2]) for e in quill_errors])

            # Combine these with the errors Bing finds
            bing_errors = set(item["original_errors"]) - set(item["errors_after_bing"])
            bing_error_types = set([error_map.get(e, e) for e in bing_errors])

            found_error_types = quill_error_types | bing_error_types

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
            #time.sleep(2)

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
