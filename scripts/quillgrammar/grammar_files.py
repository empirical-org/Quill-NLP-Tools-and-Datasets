import random
import ndjson
import json
import os
import yaml

from collections import Counter

from quillnlp.grammar.constants import GrammarError


file_list = [
    ("data/training/Passive_without_be.ndjson", 500000, 5000),
    ("data/training/Passive_with_incorrect_be.ndjson", 200000, 1000),
    ("data/training/Passive_perfect_without_have.ndjson", 200000, 1000),
    ("data/training/Perfect_progressive_with_incorrect_be_and_without_have.ndjson", 200000, 1000),
    ("data/training/Perfect_progressive_without_have.ndjson", 200000, 1000),
    ("data/training/Perfect_without_have.ndjson", 500000, 5000),
    ("data/training/Simple_past_instead_of_past_perfect.ndjson", 200000, 1000),
    ("data/training/Its_vs_it_s.ndjson", 50000, 1000),
    ("data/training/Plural_versus_possessive_nouns.ndjson", 200000, 1000),
    ("data/training/Subject_verb_agreement_with_inversion.ndjson", 500000, 5000),
    ("data/training/Subject_verb_agreement_with_personal_pronoun2.ndjson", 500000, 5000),
    ("data/training/Subject_verb_agreement_with_simple_noun2.ndjson", 500000, 5000),
    ("data/training/Subject_verb_agreement_with_indefinite_pronoun.ndjson", 500000, 5000),
    ("data/training/Past_instead_of_participle.ndjson", 200000, 1000),
    ("data/training/Passive_with_simple_past_instead_of_participle.ndjson", 200000, 1000),
    ("data/training/Passive_perfect_with_incorrect_participle.ndjson", 500000, 5000),
    ("data/training/VBN_VBD.ndjson", 100000, 1000),
    ("data/training/Possessive_pronouns.ndjson", 100000, 1000),
    ("Subject_pronouns.ndjson", 100000, 1000),
    ("data/training/Object_pronouns.ndjson", 200000, 1000),
    ("data/training/Their_vs._there_vs._they're.ndjson", 100000, 1000),
    # ("Incorrect_irregular_past_tense.ndjson", 500000, 5000),
    ("Incorrect_participle.ndjson", 500000, 5000),
    # ("Irregular_plural_nouns.ndjson", 500000, 5000),
    ("data/training/Than_versus_then.ndjson", 50000, 500),
    ("data/training/Accept_vs_except.ndjson", 50000, 500),
    ("data/training/Affect_vs_effect.ndjson", 50000, 500),
    ("data/training/Passed_vs_past.ndjson", 50000, 500),
    ("data/training/Lead_vs_led.ndjson", 50000, 500),
    ("data/training/You're_vs_your.ndjson", 50000, 500),
    ("data/training/Who's_vs_whose.ndjson", 50000, 500),
    ("data/training/To_vs_too_vs_two.ndjson", 50000, 500),
    ("data/training/Loose_vs_lose.ndjson", 50000, 500),
    ("data/training/Further_vs_farther.ndjson", 50000, 500),
    ("data/training/Advise_vs_advice.ndjson", 50000, 500),
    # ("data/training/Elicit_vs_illicit.ndjson", 50000, 500),
    ("data/training/Council_vs_counsel.ndjson", 50000, 500),
    ("data/training/Cite_vs_sight_vs_site.ndjson", 50000, 500),
    ("data/training/Through_vs_threw_vs_thru.ndjson", 50000, 500),
    ("data/training/Apart_vs_a_part.ndjson", 50000, 500),
]


entity_map = {
    GrammarError.SVA_SIMPLE_NOUN.value: GrammarError.SUBJECT_VERB_AGREEMENT.value,
    GrammarError.SVA_PRONOUN.value: GrammarError.SUBJECT_VERB_AGREEMENT.value,
    GrammarError.SVA_INDEFINITE.value: GrammarError.SUBJECT_VERB_AGREEMENT.value,
    GrammarError.SVA_INVERSION.value: GrammarError.SUBJECT_VERB_AGREEMENT.value
}


def select_train_data(train_data, max_per_error):
    """
    The goal of this method is to make the training data for verb errors much more
    diverse, so that we don't have an over-representation of be and have.

    Args:
        train_data:
        max_per_error:

    Returns:

    """
    token_counter = Counter()

    correct_items = []
    error_items = []
    for item in train_data:
        sentence = item[0]
        errors = item[1].get("entities")
        if len(errors) > 0:
            error_start = errors[0][0]
            error_end = errors[0][1]
            error_token = sentence[error_start:error_end]
            token_counter.update([error_token])
            if token_counter[error_token] <= 5000:
                error_items.append(item)
        else:
            correct_items.append(item)

    return error_items[:int(max_per_error/2)] + correct_items[:int(max_per_error/2)]


def read_grammar_data():
    all_train_data = []
    all_test_data = []
    all_dev_data = []
    for f, train_size, test_size in file_list:
        print("Reading:", f)
        with open(f) as i:
            train_data = []
            try:
                train_data += ndjson.load(i)
            except json.decoder.JSONDecodeError:
                print(f"JSONDecodeError in file {f}")
                with open(f) as i2:
                    for line in i2:
                        if len(line.strip()) > 0:
                            train_data.append(json.loads(line.strip()))

        print("Filtering")
        filtered_train_data = []
        for line in train_data:
            if len(line[0]) > 20 and len(line[0]) < 200 and not "Caption" in line[0]:
                filtered_train_data.append(line)
        print(f"{len(train_data)} => {len(filtered_train_data)}")

        train_data = filtered_train_data

        random.shuffle(train_data)
        if "Subject_verb_agreement" in f:
            train_data = select_train_data(train_data, 500000)

            for item in train_data:
                if item[1]['entities']:
                    for entity in item[1]['entities']:
                        entity[2] = entity[2].replace("_", " ")  # Remove _ in Subject_verb
                        entity[2] = entity_map.get(entity[2], entity[2])
                        entity[2] = entity[2].replace(" ", "_")
        else:
            train_data = train_data[:train_size]
        print(f"-> {len(train_data)} sentences")

        all_test_data.extend(train_data[:test_size])
        all_dev_data.extend(train_data[test_size:2*test_size])
        all_train_data.extend(train_data[2*test_size:])

    random.shuffle(all_train_data)
    random.shuffle(all_dev_data)
    random.shuffle(all_test_data)

    return all_train_data, all_dev_data, all_test_data

