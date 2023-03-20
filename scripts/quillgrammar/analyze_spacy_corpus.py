import os
import click
import spacy
import glob

from collections import Counter
from spacy.tokens import DocBin


@click.command()
@click.argument('path')
def run(path):

    nlp = spacy.load('en_core_web_sm')

    error_counter = Counter()
    word_counter = {}
    if os.path.isfile(path):
        doc_bin = DocBin().from_disk(path)
        for doc in doc_bin.get_docs(nlp.vocab):
            error_counter.update([ent.label_ for ent in doc.ents])
            error_labels_and_words = [(ent.label_, ent.text) for ent in doc.ents]
            for label, word in error_labels_and_words:
                if label not in word_counter:
                    word_counter[label] = Counter()
                word_counter[label].update([word])

            # if 'incorrect_infinitive_ing' in error_labels:
            #     print(doc)
            #     print(doc.ents)
    elif os.path.isdir(path):
        files = glob.glob(os.path.join(path, '*.spacy'))
        for f in files:
            print(f)
            doc_bin = DocBin().from_disk(f)
            for doc in doc_bin.get_docs(nlp.vocab):
                error_counter.update([ent.label_ for ent in doc.ents])
                error_labels_and_words = [(ent.label_, ent.text) for ent in doc.ents]
                for label, word in error_labels_and_words:

                    if word.endswith('.'):
                        print(doc, doc.ents, doc.ents[0].start_char, doc.ents[0].end_char)

                    if label not in word_counter:
                        word_counter[label] = Counter()
                    word_counter[label].update([word])

    for error, freq in error_counter.most_common():
        print(error, freq, word_counter[error].most_common(20))


if __name__ == '__main__':
    run()