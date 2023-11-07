import os
import random
import click
from pathlib import Path
from tqdm import tqdm
from grammar_corpus import read_grammar_data

import spacy
from spacy.tokens import DocBin, Span

from quillnlp.grammar.myspacy import nlp
from quillnlp.corpora.notw import read_sentences

TRAINING_INDEX_FILE = 'scripts/quillgrammar/grammar_files.csv'


def find_index_from_offsets(doc, start, end):
    """ Finds the start and end index of a spaCy token,
    based on its entity information """

    first_token_start = None
    next_token_start = None

    for token in doc:
        if token.idx >= start and first_token_start is None:
            first_token_start = token.i
        if token.idx >= end and next_token_start is None:
            next_token_start = token.i

    if next_token_start is None:
        next_token_start = len(doc)

    return first_token_start, next_token_start

# nlp = spacy.load('en_core_web_sm')
# doc = nlp("The younger the child, the smaller the group should is.")
# start_idx, end_idx = find_index_from_offsets(doc, 52, 54)
# x = Span(doc, start_idx, end_idx, 'TEST')
# print(x.text)
# assert x.text == 'is'

def write_output(data, output_path):
    """ Writes error data to an output_path in spaCy's DocBin format. """
    db = DocBin()
    nlp = spacy.blank('en')

    random.shuffle(data)
    for sentence, label in tqdm(data):
        doc = nlp.make_doc(sentence)

        if isinstance(label, dict):
            entities = []
            start_idx_returned_none = False
            for ent in label['entities']:
                start_idx, end_idx = find_index_from_offsets(doc, ent[0], ent[1])

                if start_idx and end_idx:
                    entities.append(Span(doc, start_idx, end_idx, ent[2]))
                else:
                    start_idx_returned_none = True
            # try:
            if not start_idx_returned_none:
                if entities or random.randint(0, 3) != 3:
                    doc.set_ents(entities)
                    db.add(doc)
            # except:
            #     continue
        else:
            raise ValueError('Unknown label type for', label)


    db.to_disk(output_path)


@click.command()
@click.argument('output_path')
def run(output_path):

    # Read grammar data
    grammar_train, grammar_dev, grammar_test = read_grammar_data(TRAINING_INDEX_FILE)

    # The training data will be saved in <output_path>/train.
    # If this path doesn't exist, we create it.
    train_files_path = os.path.join(output_path, 'train')

    path = Path(train_files_path)
    path.mkdir(parents=True)

    write_output(grammar_test, os.path.join(output_path, 'test.spacy'))
    write_output(grammar_dev, os.path.join(output_path, 'dev.spacy'))

    # Write the training data in chunks. Otherwise the files are too big
    # to read for spaCy.
    chunk_size = 1000000
    for i in range(0, len(grammar_train), chunk_size):
        write_output(grammar_train[i:i+chunk_size], os.path.join(train_files_path, f"train{int(i/chunk_size)}.spacy"))


if __name__ == '__main__':
    run()