import random
import ndjson
import json
import os
import jsonlines

from quillnlp.grammar.constants import GrammarError

import click




file_list = [
    ("data/training/v2/passive_without_be.ndjson", 10000, 1000),
    ("data/training/v2/passive_with_incorrect_be.ndjson", 10000, 1000),
    ("data/training/v2/passive_perfect_without_have.ndjson", 1000, 100),
    ("data/training/v2/perfect_progressive_with_incorrect_be_and_without_have.ndjson", 10000, 1000),
    ("data/training/Perfect_progressive_without_have.ndjson", 10000, 1000),
    ("data/training/v2/perfect_without_have.ndjson", 10000, 1000),
    ("data/training/Simple_past_instead_of_past_perfect.ndjson", 10000, 1000),
    ("data/training/v2/its_versus_it's.ndjson", 10000, 1000),
    ("data/training/Plural_versus_possessive_nouns.ndjson", 10000, 1000),
    ("data/training/Subject_verb_agreement_with_inversion.ndjson", 10000, 1000),
    ("data/training/v2/subject_verb_agreement_with_personal_pronoun.ndjson", 10000, 1000),
    ("data/training/v2/subject_verb_agreement_with_simple_noun.ndjson", 10000, 1000),
    ("data/training/v2/subject_verb_agreement_with_indefinite_pronoun.ndjson", 10000, 1000),
    ("data/training/Past_instead_of_participle.ndjson", 10000, 1000),
    ("data/training/Passive_with_simple_past_instead_of_participle.ndjson", 10000, 1000),
    ("data/training/Passive_perfect_with_incorrect_participle.ndjson", 10000, 1000),
    ("data/training/VBN_VBD.ndjson", 10000, 1000),
    ("data/training/v2/possessive_pronouns.ndjson", 10000, 1000),
    ("data/training/v2/subject_pronouns.ndjson", 10000, 1000),
    ("data/training/v2/object_pronouns.ndjson", 10000, 1000),
    ("data/training/Their_vs._there_vs._they're.ndjson", 10000, 1000),
    ("data/training/Incorrect_participle.ndjson", 10000, 1000),
    ("data/training/Than_versus_then.ndjson", 10000, 1000),
    ("data/training/Accept_vs_except.ndjson", 10000, 1000),
    ("data/training/Affect_vs_effect.ndjson", 10000, 1000),
    ("data/training/Passed_vs_past.ndjson", 10000, 1000),
    ("data/training/Lead_vs_led.ndjson", 10000, 1000),
    ("data/training/You're_vs_your.ndjson", 10000, 1000),
    ("data/training/Who's_vs_whose.ndjson", 10000, 1000),
    ("data/training/To_vs_too_vs_two.ndjson", 10000, 1000),
    ("data/training/Loose_vs_lose.ndjson", 10000, 1000),
    ("data/training/Further_vs_farther.ndjson", 10000, 1000),
    ("data/training/Advise_vs_advice.ndjson", 10000, 1000),
    ("data/training/Council_vs_counsel.ndjson", 10000, 1000),
    ("data/training/Cite_vs_sight_vs_site.ndjson", 10000, 1000),
    ("data/training/Through_vs_threw_vs_thru.ndjson", 10000, 1000),
    ("data/training/Apart_vs_a_part.ndjson", 10000, 1000),
]


entity_map = {
    GrammarError.SVA_SIMPLE_NOUN.value: GrammarError.SUBJECT_VERB_AGREEMENT.value,
    GrammarError.SVA_PRONOUN.value: GrammarError.SUBJECT_VERB_AGREEMENT.value,
    GrammarError.SVA_INDEFINITE.value: GrammarError.SUBJECT_VERB_AGREEMENT.value,
    GrammarError.SVA_INVERSION.value: GrammarError.SUBJECT_VERB_AGREEMENT.value
}


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
        if "subject_verb_agreement" in f.lower():
            for item in train_data:
                if item[1]['entities']:
                    for entity in item[1]['entities']:
                        # entity[2] = entity[2].replace("_", " ")  # Remove _ in Subject_verb
                        entity[2] = entity_map.get(entity[2], entity[2])
                        # entity[2] = entity[2].replace(" ", "_")
        else:
            train_data = train_data[:train_size]
        print(f"-> {len(train_data)} sentences")

        all_train_data.extend(train_data[:train_size])
        all_dev_data.extend(train_data[train_size:train_size+test_size])
        all_test_data.extend(train_data[train_size+test_size:train_size+2*test_size])

    random.shuffle(all_train_data)
    random.shuffle(all_dev_data)
    random.shuffle(all_test_data)

    return all_train_data, all_dev_data, all_test_data


def find_index_from_offsets(doc, start, end):

    first_token_start = None
    next_token_start = None

    for token in doc:
        if token.idx >= start and first_token_start is None:
            first_token_start = token.i
        if token.idx > end and next_token_start is None:
            next_token_start = token.i

    if next_token_start is None:
        next_token_start = len(doc)

    return first_token_start, next_token_start



def write_output(data, output_path):
    with jsonlines.open(output_path, 'w') as writer:
        for item in data:
            label = 'Correct' if item[1].get('entities') == [] else item[1].get('entities')[0][2]
            label = label.replace(' ', '_')

            if label != 'Correct':
                start_index = item[1].get('entities')[0][0]
                end_index = item[1].get('entities')[0][1]
                text = item[0][start_index:end_index]
                writer.write({'prompt': item[0] + '\n\n###\n\n',
                            'completion': ' ' + str(start_index) + ' ' + text + ' ' + label})
            else:
                writer.write({'prompt': item[0] + '\n\n###\n\n',
                            'completion': ' ' + label})



@click.command()
@click.argument('output_path')
def run(output_path):

    # Read grammar data    
    grammar_train, grammar_dev, grammar_test = read_grammar_data()

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    write_output(grammar_test, os.path.join(output_path, 'grammar_test_10000_ft.jsonl'))
    write_output(grammar_dev, os.path.join(output_path, 'grammar_dev_10000_ft.jsonl'))
    write_output(grammar_train, os.path.join(output_path, 'grammar_train_10000_ft.jsonl'))


if __name__ == '__main__':
    run()