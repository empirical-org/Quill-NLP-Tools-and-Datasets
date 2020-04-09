import spacy
import ndjson
import click
import random

from tqdm import tqdm
from quillnlp.grammar.corpus import replace


@click.command()
@click.argument('filename')
@click.argument('output_file')
@click.option('--error_ratio', default=1/6)
def create_corpus(filename, output_file, error_ratio):

    def file_len(fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    train_data = []
    nlp = spacy.load("en")

    num_lines = file_len(filename)

    with open(filename) as i:
        for line in tqdm(i, total=num_lines):

            if random.random() > 0.1:
                continue

            sentence = line.strip()
            if "=" in line:  # Ignore noisy Wikipedia lines
                continue

            doc = nlp(sentence)
            synthetic_sentence, errors = replace(doc, error_ratio)
            if len(errors) > 0:
                train_data.append({"orig_sentence": sentence,
                                   "synth_sentence": synthetic_sentence,
                                   "entities": errors})
            else:
                train_data.append({"orig_sentence": sentence})

            if len(train_data) % 100000 == 0:
                with open(output_file, "w") as o:
                    ndjson.dump(train_data, o)

        with open(output_file, "w") as o:
            ndjson.dump(train_data, o)


if __name__ == "__main__":
    create_corpus()
