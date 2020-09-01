import ndjson
import click
import json
import random

from quillnlp.models.spacy.train import train_spacy_ner


@click.command()
@click.argument('output_file')
def train_grammar_model(output_file):

    file_list = ["data/training/Passive_without_be.ndjson",
                 "data/training/Passive_perfect_without_have.ndjson",
                 "data/training/Perfect_progressive_with_incorrect_be_and_without_have.ndjson",
                 "data/training/Perfect_progressive_without_have.ndjson",
                 "data/training/Perfect_without_have.ndjson",
                 "data/training/Simple_past_instead_of_past_perfect.ndjson",
                 "data/training/Its_vs_it_s.ndjson",
                 "Plural_vs_possessive.ndjson"]

    test_size = 10000
    train_data = []
    for f in file_list:
        with open(f) as i:
            try:
                train_data += ndjson.load(i)
            except json.decoder.JSONDecodeError:
                for line in i:
                    if len(line.strip()) > 0:
                        train_data.append(json.loads(line.strip()))

    random.shuffle(train_data)

    for x in train_data[:100]:
        print(x)

    print("Data items:", len(train_data))

    test_data = train_data[-test_size:]
    dev_data = train_data[-test_size*2:-test_size]
    train_data = train_data[:-test_size*2]

    train_spacy_ner(train_data, dev_data, test_data, "/tmp/spacy_grammartest", output_file, n_iter=50, patience=5)


if __name__ == "__main__":
    train_grammar_model()

