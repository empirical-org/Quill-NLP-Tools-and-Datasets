import spacy
import json
import click
from functools import partial
from tqdm import tqdm
from quillnlp.grammar import corpus


error_types = {"VB": corpus.has_infinitive,
               "NNS": corpus.has_plural_noun,
               "POS": corpus.has_possessive_noun,
               "VBP": corpus.has_present_verb_non_third_person,
               "VBZ": corpus.has_third_person_singular_verb,
               "ADV": corpus.has_adverb,
               "its": partial(corpus.contains_token, "its"),
               "it's": partial(corpus.contains_phrase, ["it", "'s"]),
               "child": partial(corpus.contains_token, "child"),
               "children": partial(corpus.contains_token, "children"),
               "woman": partial(corpus.contains_token, "woman"),
               "women": partial(corpus.contains_token, "women"),
               "than": partial(corpus.contains_token, "than"),
               "then": partial(corpus.contains_token, "then")
               }


@click.command()
@click.argument('filename')
@click.argument('number')
@click.argument('output_file')
def create_corpus(filename, number, output_file):

    def file_len(fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    number = int(number)
    error_corpus = {error: [] for error in error_types}
    nlp = spacy.load("en")

    num_lines = file_len(filename)

    with open(filename) as i:
        for line in tqdm(i, total=num_lines):
            line = line.strip()
            if "=" in line:
                continue

            doc = nlp(line)

            for error_type in error_types:
                if len(error_corpus[error_type]) < number:
                    if error_types[error_type](doc):
                        error_corpus[error_type].append(line)

    with open(output_file, "w") as o:
        json.dump(error_corpus, o)


if __name__ == "__main__":
    create_corpus()
