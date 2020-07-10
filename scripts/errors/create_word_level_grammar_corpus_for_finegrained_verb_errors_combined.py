import ndjson
import click
import json
import random

from quillnlp.models.spacy.train import train_spacy_ner


@click.command()
@click.argument('output_file')
def create_corpus(output_file):

    file_list = ["data/training/Simple_past_instead_of_past_perfect.ndjson",
                 "data/training/Perfect_without_have.ndjson",
                 "data/training/Past_instead_of_participle.ndjson",
                 "data/training/Perfect_progressive_without_have.ndjson",
                 "data/training/Perfect_progressive_with_incorrect_be_and_without_have.ndjson",
                 "data/training/Passive_perfect_without_have.ndjson",
                 "data/training/Passive_perfect_with_incorrect_participle.ndjson",
                 "data/training/Passive_without_be.ndjson",
                 "data/training/Passive_with_incorrect_be.ndjson",
                 "data/training/Passive_with_simple_past_instead_of_participle.ndjson"
#                 "data/training/Subject_verb_agreement_with_simple_noun.ndjson",
#                 "data/training/Subject_verb_agreement_with_personal_pronoun.ndjson"
                 ]

    file_list = ["Subject-verb_agreement2.ndjson",
                 "wiki_errors.ndjson",
                 "subtitles_errors.ndjson"]

    test_size = 10000

    train_data = []
    for f in file_list:
        with open(f) as i:
            train_data += ndjson.load(i)
            """
            for line in i:
                if len(line.strip()) > 0:
                    train_data.append(json.loads(line.strip()))
            """
    #train_data = [(item[0], {"entities": item[1]["entities"]}) for item in train_data]

    filtered_train_data = []
    for item in train_data:
        if len(item.get("entities", [])) == 1:
            for entity in item.get("entities", []):
                if entity[2] == "VERB" or entity[2] == "Subject-verb agreement":
                    entity[2] = "Subject-verb agreement"
                    orig_sentence = item.get("orig_sentence")
                    synth_sentence = item.get("synth_sentence")
                    filtered_train_data.append((orig_sentence, {"entities": []}))
                    filtered_train_data.append((synth_sentence, {"entities": item["entities"]}))
                    break

    train_data = filtered_train_data
    random.shuffle(train_data)

    for x in train_data[:100]:
        print(x)

    print("Data items:", len(train_data))

    test_data = train_data[-test_size:]
    dev_data = train_data[-test_size*2:-test_size]
    train_data = train_data[:-test_size*2]

    train_spacy_ner(train_data, dev_data, test_data, "/tmp/spacy_sva_xl", output_file, n_iter=50, patience=5)


if __name__ == "__main__":
    create_corpus()

