import random
import ndjson
import json
import spacy
import os
import yaml

from collections import Counter

from quillnlp.grammar.constants import GrammarError

CORRECT_LABEL = 'correct'

file_list = [
    ("bae.ndjson", 100000, 0),
    ("quill_labels_20221125_train.ndjson", 10000, 0),
    ("data/training/fragment_no_verb.ndjson", 50000, 1000),
    # ("data/training/they_instead_of_the.ndjson", 50000, 500),
    ("data/training/he_instead_of_the.ndjson", 20000, 500),
    ("data/training/an_instead_of_and.ndjson", 20000, 500),
    ("data/training/articles_an_optimal.ndjson", 20000, 500),
    ("data/training/articles_a_optimal.ndjson", 20000, 500),
    # ("data/training/i_instead_of_it.ndjson", 10000, 500),
    ("data/training/Runons_notw.ndjson", 200000, 2000),  # was 500000, 5000
    ("data/training/Runons_with_however.ndjson", 5000, 200),
    ("data/training/however.ndjson", 2000, 200),
    ("data/training/Runons_with_therefore.ndjson", 2000, 200),
    ("data/training/Runons_with_for_example.ndjson", 2000, 200),
    ("data/training/Runons_with_as_a_result.ndjson", 2000, 200),
    # ("data/training/passive_without_be.ndjson", 200000, 2000),
   ("data/training/passive_with_incorrect_be.ndjson", 20000, 1000),
   ("data/training/passive_perfect_without_have.ndjson", 20000, 1000),
#    ("data/training/perfect_progressive_with_incorrect_be_and_without_have.ndjson", 200000, 1000),
#    ("data/training/perfect_progressive_without_have.ndjson", 200000, 1000),
    # ("data/training/perfect_without_have.ndjson", 200000, 5000),
    # ("data/training/simple_past_instead_of_past_perfect.ndjson", 200000, 1000),
    ("data/training/its_versus_it_s.ndjson", 20000, 1000),
    ("data/training/incorrect_infinitive.ndjson", 10000, 500),
    ("data/training/incorrect_infinitive_ing.ndjson", 10000, 500),
    ("data/training/incorrect_infinitive_past.ndjson", 10000, 500),
    ("data/training/missing_preposition_after_stat.ndjson", 5000, 500),
    # ("data/training/singular_and_plural_nouns.ndjson", 50000, 1000),
    ("data/training/singular_and_plural_nouns_no_determiner.ndjson", 100000, 1000),
    ("data/training/singular_and_plural_nouns_these_those.ndjson", 10000, 500),
    ("data/training/plural_versus_possessive_nouns_possessive_noun_optimal_filtered.ndjson", 100000, 2000),
    ("data/training/plural_versus_possessive_nouns_possessive_noun_optimal_propn.ndjson", 10000, 200),
    ("data/training/plural_versus_possessive_nouns_plural_noun_optimal_filtered.ndjson", 100000, 2000),
    ("data/training/plural_versus_possessive_nouns_plural_noun_optimal_negative_ing.ndjson", 10000, 200),
    ("data/training/singular_and_plural_possessive.ndjson", 20000, 1000),
    ("data/training/subject_verb_agreement_with_inversion2.ndjson", 100000, 3000),  # was 500000, 5000
    ("data/training2/subject_verb_agreement_with_personal_pronoun.ndjson", 100000, 3000), # was 500000
    ("data/training/subject_verb_agreement_with_relative_pronoun.ndjson", 100000, 1000),  #was 200000, 200
    ("data/training/subject_verb_agreement_with_simple_noun_filtered.ndjson", 500000, 5000), # was 500000
    ("data/training/subject_verb_agreement_with_indefinite_pronoun.ndjson", 200000, 3000), # was 500000
    ("data/training/past_instead_of_participle.ndjson", 100000, 1000),
    ("data/training/passive_with_simple_past_instead_of_participle.ndjson", 100000, 1000),
#    ("data/training/passive_perfect_with_incorrect_participle.ndjson", 200000, 5000), # was 500000
    ("data/training/VBN_VBD.ndjson", 50000, 2000),
    # ("data/training/possessive_pronouns.ndjson", 100000, 1000),
    # ("data/training/subject_pronouns.ndjson", 200000, 2000),
    # ("data/training/object_pronouns.ndjson", 200000, 2000),
    ("data/training/their_vs_there_vs_they_re.ndjson", 50000, 1000),
#    ("data/training/incorrect_participle.ndjson", 200000, 5000), # was 500000
    ("data/training/than_versus_then.ndjson", 10000, 1000),
    ("data/training/accept_vs_except.ndjson", 10000, 1000),
    ("data/training/affect_vs_effect.ndjson", 5000, 500), # 20230602: was 1000
    ("data/training/passed_vs_past.ndjson", 5000, 500), # 20230602: was 1000
    ("data/training/lead_vs_led.ndjson", 20000, 500), # 20230602: was 1000
    ("data/training/you_re_vs_your.ndjson", 20000, 1000),
    ("data/training/who_s_vs_whose.ndjson", 20000, 1000),
    ("data/training/to_vs_too_vs_two_to_optimal.ndjson", 10000, 500),
    ("data/training/to_vs_too_vs_two_two_optimal.ndjson", 10000, 500),
    ("data/training/to_vs_too_vs_two_too_optimal.ndjson", 10000, 500),
    ("data/training2/loose_vs_lose2.ndjson", 20000, 500), # 20230602: was 1000
    ("data/training/further_vs_farther.ndjson", 10000, 500), # 20230602: was 1000
    ("data/training/advise_vs_advice.ndjson", 5000, 500), # 20230602: was 1000
    ("data/training/council_vs_counsel.ndjson", 10000, 500), # 20230602: was 1000
    ("data/training/through_vs_threw_vs_thru.ndjson", 10000, 500), # 20230602: was 1000
    ("data/training/apart_vs_a_part.ndjson", 20000, 500), # 20230602: was 1000
    ]

print("Total train data:", sum(x[1] for x in file_list))
print("Total dev data:", sum(x[2] for x in file_list))


entity_map = {
    GrammarError.TO_TWO_TOO_TO_OPTIMAL.value: GrammarError.TO_TWO_TOO.value,
    GrammarError.TO_TWO_TOO_TOO_OPTIMAL.value: GrammarError.TO_TWO_TOO.value,
    GrammarError.TO_TWO_TOO_TWO_OPTIMAL.value: GrammarError.TO_TWO_TOO.value,
}


def select_train_data_sva(train_data, max_per_error, seen_sentences):
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

        if sentence in seen_sentences:
            continue

        if len(errors) > 0:
            error_start = errors[0][0]
            error_end = errors[0][1]
            error_token = sentence[error_start:error_end]
            token_counter.update([error_token])
            if token_counter[error_token] <= 5000:
                error_items.append(item)
        else:
            correct_items.append(item)

    selected_error_items = error_items[:int(max_per_error/2)]
    selected_correct_items = correct_items[:int(max_per_error/2)]
    seen_sentences.update([item[0] for item in selected_error_items + selected_correct_items])

    return selected_error_items + selected_correct_items


def select_best_sentences(train_data, min_sentence_char_length=20, max_sentence_char_length=300):
    """ Filters out sentences that are too short or too long, and that
    contain the word 'Caption' """
    filtered_train_data = []
    for line in train_data:
        if "Caption" in line[0]:
            continue
        elif "Photos:" in line[0]:
            continue
        elif "  " in line[0]:
            continue
        elif len(line[0]) > min_sentence_char_length and len(line[0]) < max_sentence_char_length:
            filtered_train_data.append(line)
    print(f"After noise removal: {len(train_data)} => {len(filtered_train_data)}")
    return filtered_train_data


def get_error_frequencies(train_data):
    """ Gets the distribution of error types in the data. If there are several error types
    in one file, we want to distribute them as evenly as possible. """
    error_type_counter = Counter()
    for item in train_data:
        sentence, info = item
        entities = info.get('entities')
        if entities:
            for entity in entities:
                _, _, label = entity
                error_type_counter.update([label])
        else:
            error_type_counter.update([CORRECT_LABEL])

    return error_type_counter


def select_train_data(train_data, error_frequencies, data_size, seen_sentences):
    """ Selects a training data set that has a good representation of all errors."""

    # We always use 50% correct sentences
    num_sents_correct = data_size / 2

    # The other 50% is distributed as evenly as possible across the other error types
    num_error_types = len([x for x in error_frequencies if x != CORRECT_LABEL])
    num_sents_per_error_type = data_size / (2 * num_error_types) if num_error_types > 0 else 0

    final_train_data = []
    sampled_frequencies = Counter()

    for item in train_data:
        sentence, info = item
        entities = info.get('entities')

        if sentence in seen_sentences:
            continue

        if entities and sentence not in seen_sentences:
            first_entity_label = entities[0][2]
            if sampled_frequencies[first_entity_label] < num_sents_per_error_type:
                final_train_data.append(item)
                seen_sentences.update([item[0]])
                sampled_frequencies.update([first_entity_label])
        else:
            if sampled_frequencies[CORRECT_LABEL] < num_sents_correct:
                final_train_data.append(item)
                seen_sentences.update([item[0]])
                sampled_frequencies.update([CORRECT_LABEL])

    print(sampled_frequencies)

    return final_train_data


def read_grammar_data():
    all_train_data = []
    all_test_data = []
    all_dev_data = []

    seen_sentences = set()

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

        train_data = select_best_sentences(train_data)
        error_frequencies = get_error_frequencies(train_data)
        # print(error_frequencies)

        random.shuffle(train_data)

        if "subject_verb_agreement" in f.lower():
            train_data = select_train_data_sva(train_data, train_size + test_size, seen_sentences)
        else:
            train_data = select_train_data(train_data, error_frequencies, train_size + 2*test_size, seen_sentences)

        random.shuffle(train_data)

        print(f'Requested - Train: {train_size} Dev: {test_size} Test: {test_size}')

        # Map entity label to correct name
        for item in train_data:
            if item[1]['entities']:
                for entity in item[1]['entities']:
                    entity[2] = entity_map.get(entity[2], entity[2])

                    if entity[2].startswith("subject_verb_agreement"):
                        entity[2] = "subject_verb_agreement"

        train_data_unique = []
        for item in train_data:
            if item[0] in seen_sentences:
                continue
            else:
                train_data_unique.append(item)
                seen_sentences.add(item[0])

        error_test_data = train_data[:test_size]
        error_dev_data = train_data[test_size:2*test_size]
        error_train_data = train_data[2*test_size:]

        all_test_data.extend(error_test_data)
        all_dev_data.extend(error_dev_data)
        all_train_data.extend(error_train_data)

        print(f'Selected - Train: {len(error_train_data)} Dev: {len(error_test_data)} Test: {len(error_dev_data)}')

        positive_error_train_data = [x for x in error_train_data if x[1]['entities']]
        positive_error_dev_data = [x for x in error_dev_data if x[1]['entities']]
        positive_error_test_data = [x for x in error_test_data if x[1]['entities']]

        print(f'Selected - Train: {len(positive_error_train_data)} Dev: {len(positive_error_test_data)} Test: {len(positive_error_dev_data)}')
        print(f'Distribution: {get_error_frequencies(train_data)}')
        print('-'*20)


    random.shuffle(all_train_data)
    random.shuffle(all_dev_data)
    random.shuffle(all_test_data)

    print('Final distribution:')
    frequencies = get_error_frequencies(all_train_data)
    print('Total:', sum(frequencies.values()))
    for error, freq in frequencies.most_common():
        print(f"{error}: {freq}")

    return all_train_data, all_dev_data, all_test_data

