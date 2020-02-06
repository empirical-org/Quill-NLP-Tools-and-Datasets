import spacy
import ndjson
import click
import random

from functools import partial
from tqdm import tqdm
from quillnlp.grammar import corpus

ERROR_RATIO = 1/3

VERB_AGREEMENT_ERROR_TYPE = "VERB"
WOMAN_WOMEN_ERROR_TYPE = "WOMAN"
THEN_THAN_ERROR_TYPE = "THEN"
CHILD_CHILDREN_ERROR_TYPE = "CHILD"
IT_S_ITS_ERROR_TYPE = "ITS"
PLURAL_POSSESSIVE_ERROR_TYPE = "POSSESSIVE"
ADV_ERROR_TYPE = "ADV"

error_types = {"VB": corpus.has_infinitive,
               "NNS": corpus.has_plural_noun,
               "POS": corpus.has_possessive_noun,
               "VBP": corpus.has_present_verb_non_third_person,
               "VBZ": corpus.has_third_person_singular_verb,
               "MD": corpus.has_modal,
               "AUX": corpus.has_aux,
               "ADV": corpus.has_adverb,
               "do": corpus.has_do,
               "its": partial(corpus.contains_token, "its"),
               "it's": partial(corpus.contains_phrase, ["it", "'s"]),
               "child": partial(corpus.contains_token, "child"),
               "children": partial(corpus.contains_token, "children"),
               "woman": partial(corpus.contains_token, "woman"),
               "women": partial(corpus.contains_token, "women"),
               "than": partial(corpus.contains_token, "than"),
               "then": partial(corpus.contains_token, "then")
               }


replacement_functions = {"POS": partial(corpus.replace_possessive_by_plural, PLURAL_POSSESSIVE_ERROR_TYPE),
                         "NNS": partial(corpus.replace_plural_by_possessive, PLURAL_POSSESSIVE_ERROR_TYPE),
                         "VBZ": partial(corpus.replace_verb_form, "VBZ", "VB", VERB_AGREEMENT_ERROR_TYPE),
                         "VBP": partial(corpus.replace_verb_form, "VBP", "VBZ", VERB_AGREEMENT_ERROR_TYPE),
                         "VB": partial(corpus.replace_verb_form, "VB", "VBZ", VERB_AGREEMENT_ERROR_TYPE),
                         "AUX": partial(corpus.replace_verb_form, "VB", "VBZ", VERB_AGREEMENT_ERROR_TYPE),
                         "MD": partial(corpus.replace_verb_form, "VB", "VBZ", VERB_AGREEMENT_ERROR_TYPE),
                         "do": partial(corpus.replace_verb_form, "VB", "VBZ", VERB_AGREEMENT_ERROR_TYPE),
                         "ADV": partial(corpus.replace_adverb_by_adjective, ADV_ERROR_TYPE),
                         "woman": partial(corpus.replace_word, "woman", "women", WOMAN_WOMEN_ERROR_TYPE),
                         "women": partial(corpus.replace_word, "women", "woman", WOMAN_WOMEN_ERROR_TYPE),
                         "then": partial(corpus.replace_word, "then", "than", THEN_THAN_ERROR_TYPE),
                         "than": partial(corpus.replace_word, "than", "then", THEN_THAN_ERROR_TYPE),
                         "child": partial(corpus.replace_word, "child", "children", CHILD_CHILDREN_ERROR_TYPE),
                         "children": partial(corpus.replace_word, "children", "child", CHILD_CHILDREN_ERROR_TYPE),
                         "its": partial(corpus.replace_word, "its", "it's", IT_S_ITS_ERROR_TYPE),
                         "it's": partial(corpus.replace_bigram, ["it", "'s"], "its", IT_S_ITS_ERROR_TYPE)
                         }


@click.command()
@click.argument('filename')
@click.argument('output_file')
def create_corpus(filename, output_file):

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
            sentence = line.strip()
            if "=" in line:
                continue

            doc = nlp(sentence)

            for error_type in error_types:
                if error_types[error_type](doc):

                    if random.random() < ERROR_RATIO:
                        sentence_with_error, entities = replacement_functions[error_type](doc)
                        train_data.append({"type": error_type,
                                           "orig_sentence": sentence,
                                           "synth_sentence": sentence_with_error,
                                           "entities": entities})
                    else:
                        train_data.append({"type": error_type,
                                           "orig_sentence": sentence})

            if len(train_data) % 100000 == 0:
                with open(output_file, "w") as o:
                    ndjson.dump(train_data, o)

        with open(output_file, "w") as o:
            ndjson.dump(train_data, o)


if __name__ == "__main__":
    create_corpus()
