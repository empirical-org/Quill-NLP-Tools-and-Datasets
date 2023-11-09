import json

import spacy
import ndjson
import click
import random

from tqdm import tqdm


from quillnlp.grammar import generation, fragments
from quillnlp.corpora import notw
from quillnlp.grammar.constants import GrammarError




def inject_errors(sentences, error_generator, verbose=False, probability=0.5):
    """Inject errors into a list of sentences

    Args:
        sentences (_type_): the sentences in which the error will be injected.
        error_generator (_type_): the error generator that will inject the errors.
        verbose (bool, optional): If True, prints out the original and synthetic sentence. Defaults to False.
        probability (float, optional): The probability of the error. Defaults to 0.5.
    """

    nlp = spacy.load("en_core_web_sm")
    docs = list(nlp.pipe(sentences))

    train_data = []
    for sentence in docs:
        synthetic_sentence, entities, relevant = error_generator.generate_from_doc(sentence, add_optimal=False)

        if relevant and synthetic_sentence != sentence.text:
            if verbose:
                print(sentence)
                print(synthetic_sentence)
                print(entities)

            if random.random() < probability:
                train_data.append((synthetic_sentence, {"entities": entities,
                                                        "original": sentence.text}))
            else:
                train_data.append((sentence.text, {"entities": []}))

    output_file = f"{error_generator.name.lower()}.ndjson"
    with open(output_file, "w") as o:
        ndjson.dump(train_data, o)

    print(f"Collected {len(train_data)} sentences for {error_generator.name}")


@click.command()
@click.argument('corpus_dir')
def create_corpus(corpus_dir):

    error_generator = generation.TokenReplacementErrorGenerator({'an': ['a']}, GrammarError.ARTICLE.value)
    print("Reading corpus")
    sentences = notw.read_sentences(corpus_dir,
                                    max_sentences=100000,
                                    notw_source_file='data/corpora/newsoftheworld/notw_sources.json')

    print("Injecting errors")
    inject_errors(sentences, error_generator, verbose=True)


if __name__ == "__main__":
    create_corpus()
