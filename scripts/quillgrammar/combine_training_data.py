import re
from collections import Counter

import ndjson
import click
import json
import random

from quillgrammar.grammar.constants import GrammarError
from quillnlp.models.spacy.train import train_spacy_ner
from tqdm import tqdm
import spacy
from spacy.training import offsets_to_biluo_tags

nlp = spacy.load("en_core_web_sm")

entity_map = {
    GrammarError.SVA_SIMPLE_NOUN.value: GrammarError.SUBJECT_VERB_AGREEMENT.value,
    GrammarError.SVA_PRONOUN.value: GrammarError.SUBJECT_VERB_AGREEMENT.value,
    GrammarError.SVA_INDEFINITE.value: GrammarError.SUBJECT_VERB_AGREEMENT.value,
    GrammarError.SVA_INVERSION.value: GrammarError.SUBJECT_VERB_AGREEMENT.value
}


def make_conll_data(data_items):
    random.shuffle(data_items)

    conll_data = []

    for item in tqdm(data_items):
        sentence = item[0]

        # Skip synthetic sentences where the 's was incorrectly added to the
        # first part of a compound
        if re.search("'s[a-zA-Z]", sentence):
            continue

        entities = item[1]["entities"]
        for entity in entities:
            entity[2] = entity[2].replace("_", " ")  # Remove _ in Subject_verb
            entity[2] = entity_map.get(entity[2], entity[2])
            entity[2] = entity[2].replace(" ", "_")

        docs = nlp.tokenizer.pipe([sentence])
        doc = list(docs)[0]
        tokens = [t.text for t in doc]
        # pos = [t.tag_ for t in doc]

        try:
            tags = offsets_to_biluo_tags(doc, entities)
        except:
            continue

        pos = ["X" for _ in tokens]

        write_to_output = True
        for tag in set(tags):
            if tag == "-":
                write_to_output = False
                print("Skipping sentence")
                break

        if write_to_output:
            conll_data.append((tokens, pos, tags))

    return conll_data


def write_conll_file(data, f, docstart=False):
    with open(f, "w") as o:
        for tokens, poss, tags in data:
            if docstart:
                o.write("-DOCSTART- -X- O O\n\n")
            for (token, pos, tag) in zip(tokens, poss, tags):
                if len(token.strip()) > 0:
                    o.write(" ".join([token, pos, "_", tag]) + "\n")
            o.write("\n")


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


def filter_conll_file(file_in, file_out, max_sentences=2800000):
    sentences = []
    sentence = []
    with open(file_in) as i:
        for line in i:
            line = line.strip().split()
            if len(line) == 0:
                if len(sentence) < 50:
                    sentences.append(sentence)
                sentence = []
            elif len(line) > 0:
                sentence.append(line)
            else:
                sentence = []

        if len(sentence) > 0:
            sentences.append(sentence)

    print(len(sentences))
    random.shuffle(sentences)

    with open(file_out, "w") as o:
        for sentence in sentences[:max_sentences]:
            if len(sentence) > 3:
                tokens = " ".join([t[0] for t in sentence])
                if "Caption" not in tokens:
                    for token in sentence:
                        o.write(" ".join(token) + "\n")
                    o.write("\n")


@click.command()
@click.argument('output_file')
def create_conll_corpus(output_file):

    file_list = [("data/training/Passive_without_be.ndjson", 500000, 5000),
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
#                 ("data/training/Possessive_pronouns.ndjson", 100000),
                 ("Subject_pronouns.ndjson", 100000, 1000),
                 ("data/training/Object_pronouns.ndjson", 200000, 1000),
                 ("data/training/Their_vs._there_vs._they're.ndjson", 100000, 1000),
                 ("Incorrect_irregular_past_tense.ndjson", 500000, 5000),
                 ("Incorrect_participle.ndjson", 500000, 5000),
                 ("Irregular_plural_nouns.ndjson", 500000, 5000),
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
                 ("data/training/Elicit_vs_illicit.ndjson", 50000, 500),
                 ("data/training/Council_vs_counsel.ndjson", 50000, 500),
                 ("data/training/Cite_vs_sight_vs_site.ndjson", 50000, 500),
                 ("data/training/Through_vs_threw_vs_thru.ndjson", 50000, 500),
                 ("data/training/Apart_vs_a_part.ndjson", 50000, 500),
    ]

    file_list = [
        ("data/training/Subject_verb_agreement_with_indefinite_pronoun.ndjson", 500000, 5000),
    ]

    for x in file_list:
        if not len(x) == 3:
            print(x)

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
            else:
                train_data = train_data[:train_size]
            print(f"-> {len(train_data)} sentences")

            all_test_data.extend(train_data[:test_size])
            all_dev_data.extend(train_data[test_size:2*test_size])
            all_train_data.extend(train_data[2*test_size:])

    test_data = make_conll_data(all_test_data)
    write_conll_file(test_data, f"{output_file}_test_20210526.conll")

    dev_data = make_conll_data(all_dev_data)
    write_conll_file(dev_data, f"{output_file}_dev_20210526.conll")

    random.shuffle(all_train_data)

    chunk_size = 1000000
    for i in range(0, len(all_train_data), 1000000):
        train_data = make_conll_data(all_train_data[i:i+chunk_size])
        write_conll_file(train_data, f"{output_file}_train{int(i/chunk_size)}_20210526.conll")


if __name__ == "__main__":
    create_conll_corpus()
    #filter_conll_file(file_in="grammarmix_train_2020.conll",
    #                  file_out="grammarmix_train_20201215.conll2")