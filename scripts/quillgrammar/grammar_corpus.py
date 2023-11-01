import random
import ndjson
import json
import csv

from typing import List, Dict
from collections import Counter

from quillnlp.grammar.constants import GrammarError

CORRECT_LABEL = 'correct'

entity_map = {
    GrammarError.TO_TWO_TOO_TO_OPTIMAL.value: GrammarError.TO_TWO_TOO.value,
    GrammarError.TO_TWO_TOO_TOO_OPTIMAL.value: GrammarError.TO_TWO_TOO.value,
    GrammarError.TO_TWO_TOO_TWO_OPTIMAL.value: GrammarError.TO_TWO_TOO.value,
}


def read_file_list(csv_path: str):
    """ Get the list of training files and the number of train/test examples
    we will source from them. """
    training_files = []
    with open(csv_path) as i:
        reader = csv.DictReader(i)
        for row in reader:
            training_files.append(row)

    return training_files


def read_training_data_from_file(filepath: str):
    """Read all training data from an ndjson file. """
    train_data = []
    with open(filepath) as i:
        try:
            train_data += ndjson.load(i)
        except json.decoder.JSONDecodeError:
            with open(filepath) as i2:
                for line in i2:
                    if len(line.strip()) > 0:
                        train_data.append(json.loads(line.strip()))
    return train_data



def filter_sentences(train_data, min_sentence_char_length=20, max_sentence_char_length=300):
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

    return filtered_train_data


def get_error_frequencies(train_data):
    """ Gets the distribution of error types in the data. If there are several error types
    in one file, we want to distribute them as evenly as possible. """
    error_type_counter = Counter()
    for item in train_data:
        _, info = item
        entities = info.get('entities')
        if entities:
            for entity in entities:
                _, _, label = entity
                error_type_counter.update([label])
        else:
            error_type_counter.update([CORRECT_LABEL])

    return error_type_counter


def sample_train_data_default(train_data, error_frequencies, target_number, seen_sentences):
    """ Selects a training data set that has a good representation of all errors."""

    # We always use 50% correct sentences
    num_sents_correct = target_number / 2

    # The other 50% is distributed as evenly as possible across the other error types
    num_error_types = len([x for x in error_frequencies if x != CORRECT_LABEL])
    num_sents_per_error_type = target_number / (2 * num_error_types) if num_error_types > 0 else 0

    final_train_data = []
    sampled_frequencies = Counter()

    for item in train_data:
        sentence = item[0]
        errors = item[1].get("entities")

        # If we've seen the sentence before, we do not include it anymore.
        if sentence in seen_sentences:
            continue

        # If there are errors in the sentence, and we haven't yet reached
        # the maximum number of examples for the error,
        # then add the sentence to the training data.
        elif errors:
            first_error_label = errors[0][2]
            if sampled_frequencies[first_error_label] < num_sents_per_error_type:
                final_train_data.append(item)
                seen_sentences.update([item[0]])
                sampled_frequencies.update([first_error_label])

        # If there are no errors in the sentence, and we don't yet have
        # enough correct sentences, then add the sentence to the training data.
        else:
            if sampled_frequencies[CORRECT_LABEL] < num_sents_correct:
                final_train_data.append(item)
                seen_sentences.update([item[0]])
                sampled_frequencies.update([CORRECT_LABEL])

    return final_train_data, seen_sentences


def sample_train_data_sva(train_data, max_per_error, seen_sentences,
                          max_sva_errors_per_verb=5000):
    """ Make the training data for verb errors much more diverse, so
    that we don't have an over-representation of be and have. """

    token_counter = Counter()

    correct_items = []
    error_items = []
    for item in train_data:
        sentence = item[0]
        errors = item[1].get("entities")

        # If we've seen the sentence before, we do not include it anymore.
        if sentence in seen_sentences:
            continue

        # Otherwise, if there is an error in the sentence, identify the
        # token and add the sentence to the training data if the number of
        # examples for this token does not exceed the maximum.
        elif errors:
            error_start = errors[0][0]
            error_end = errors[0][1]
            error_token = sentence[error_start:error_end]
            token_counter.update([error_token])
            if token_counter[error_token] <= max_sva_errors_per_verb:
                error_items.append(item)

        # If the unseen sentence does not contain errors, add it to the
        # correct items.
        else:
            correct_items.append(item)

    # Now we have a list of error items where the frequency of the
    # most frequent verbs has been reduced.
    # Sample the final items and update the set of seen sentences
    selected_error_items = error_items[:int(max_per_error/2)]
    selected_correct_items = correct_items[:int(max_per_error/2)]
    seen_sentences.update([item[0] for item in selected_error_items + selected_correct_items])

    return selected_error_items + selected_correct_items, seen_sentences


def sample_train_data(train_data, training_file, error_frequencies, seen_sentences):
    """ Sample the final training data for an error from all potential data for that error."""
    random.shuffle(train_data)

    # There are two sampling methods. One for subject-verb agreement, which uses downsampling
    # of the most frequent verbs (be and have in particular),
    # and one for all other errors, which does not use downsampling.
    if "subject_verb_agreement" in training_file['filepath'].lower():
        target_num = int(training_file['num_train_items']) + int(training_file['num_test_items'])
        train_data, seen_sentences = sample_train_data_sva(train_data, target_num, seen_sentences)
    else:
        target_num = int(training_file['num_train_items']) + 2*int(training_file['num_test_items'])
        train_data, seen_sentences = sample_train_data_default(train_data, error_frequencies, target_num, seen_sentences)

    random.shuffle(train_data)
    return train_data, seen_sentences


def map_error_labels(train_data):
    """ Map the error label to the correct name. """
    for item in train_data:
        if item[1]['entities']:
            for entity in item[1]['entities']:
                if entity[2] in entity_map:
                    entity[2] = entity_map.get(entity[2])
                if entity[2].startswith("subject_verb_agreement"):
                    entity[2] = "subject_verb_agreement"

    return train_data


def read_grammar_data(path_to_file_list: str):
    """Get all grammar data. """
    all_train_data = []
    all_test_data = []
    all_dev_data = []

    seen_sentences = set()

    training_files = read_file_list(path_to_file_list)

    for training_file in training_files:

        print(training_file['filepath'])
        train_data = read_training_data_from_file(training_file['filepath'])
        train_data = filter_sentences(train_data)
        error_frequencies = get_error_frequencies(train_data)

        train_data, seen_sentences = sample_train_data(train_data, training_file, error_frequencies, seen_sentences)
        train_data = map_error_labels(train_data)

        test_size = int(training_file['num_test_items'])
        error_test_data = train_data[:test_size]
        error_dev_data = train_data[test_size:2*test_size]
        error_train_data = train_data[2*test_size:]

        all_test_data.extend(error_test_data)
        all_dev_data.extend(error_dev_data)
        all_train_data.extend(error_train_data)

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

