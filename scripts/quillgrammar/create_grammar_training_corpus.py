import json

import nltk
import spacy
import ndjson
import click
import random
import os
import re
import glob
import zipfile

from nltk import sent_tokenize
from tqdm import tqdm

from nltk.tokenize.treebank import TreebankWordDetokenizer

from quillnlp.grammar.constants import GrammarError
from quillnlp.grammar.generation import TokenReplacementErrorGenerator, subject_pronoun_error_generator, \
    object_pronoun_error_generator, possessive_pronoun_error_generator, PluralPossessivePossessiveOptimalErrorGenerator, \
    PluralPossessivePluralOptimalErrorGenerator, SingularPluralErrorGenerator, PrepositionDropGenerator, \
    their_error_generator, PronounReplacementErrorGenerator, IncorrectIrregularPastErrorGenerator, \
    IncorrectParticipleErrorGenerator, IrregularPluralNounErrorGenerator, its_its_error_generator, \
    SingularPluralPossessiveErrorGenerator, SingularPluralErrorGeneratorDropDet
from quillnlp.grammar.fragments import FragmentWithoutSubjectGenerator, FragmentWithoutVerbGenerator, FragmentWithoutVerbOrAuxGenerator
from quillnlp.grammar.verbs import perfect, agreement, passive, tense
from quillnlp.grammar.verbs.passive import PassiveWithoutBeErrorGenerator, PassiveWithIncorrectBeErrorGenerator
from quillnlp.grammar.verbs.agreement import IncorrectInfinitiveIngGenerator
from quillnlp.models.spacy.train import train_spacy_ner

PUNCTUATION = set([".", "?", "!"])

detokenizer = TreebankWordDetokenizer()


def read_sources(corpus_dir):
    source_files = glob.glob(os.path.join(corpus_dir, "sources/*.zip"))

    id2source = {}
    print("Reading sources")
    for f in tqdm(source_files):
        with zipfile.ZipFile(f) as myzip:
            ftxt = os.path.basename(f).replace(".zip", ".txt")
            with myzip.open(ftxt) as i:
                for line in i:
                    line = line.decode("latin-1").strip().split("\t")
                    source = line[4]
                    text_id = line[0]
                    id2source[text_id] = source

    with open("notw_sources.json", "w") as o:
        json.dump(id2source, o)

    return id2source


US_SOURCES = set(["Yahoo News", "Huffington Post", "ABC News", "NPR", "Los Angeles Times",
                  "Washington Post", "New York Times", "USA TODAY", "Chicago Tribune",
                  "CNN", "New York Post", "Fox News", "CNBC", "CBS News"])


def clean_text(text):
    """ Clean a text from the News of the World corpus"""
    text = re.sub("<h>.*<h>", "", text)
    text = re.sub("<.*?>", "", text)
    text = re.sub(" ([\.\,\!\?\)\;\:])", "\\1", text)
    text = re.sub("([\(]) ", "\\1", text)
    return text


def get_data_from_files(files, id2source, seen_sentences, error_generator, train_length, nlp,
                        output_file, from_us=True, verbose=False, probability=0.5):

    total_items = 0
    ignored_sentences = 0

    # Add more data
    for f in files:
        print(f)
        with zipfile.ZipFile(f) as myzip:
            zipped_files = myzip.namelist()
            for zf in zipped_files:
                print("->", zf)

                # Read new zip file
                texts = []
                with myzip.open(zf) as i:
                    for line in i:
                        line = line.decode("latin-1").strip().split()
                        try:
                            text_id = line[0][2:]
                        except:
                            continue
                        if (from_us and text_id in id2source) or (not from_us and text_id not in id2source):
                            text = line[1:]
                            text = detokenizer.detokenize(text)
                            paragraphs = re.split("<p>", text)

                            for paragraph in paragraphs:
                                sentences = nltk.sent_tokenize(paragraph)
                                for sentence in sentences:
                                    if len(re.findall("' ", sentence)) < 2:
                                        sentence = clean_text(sentence.strip())
                                        if len(sentence.split()) > 3 and "@" not in sentence \
                                                and sentence[-1] in PUNCTUATION and sentence not in seen_sentences:

                                            seen_sentences.add(sentence)
                                            texts.append(sentence)
                                    else:
                                        # print("Ignored:", sentence)
                                        ignored_sentences += 1

                docs = list(nlp.pipe(texts))

                # Process texts
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

                if not os.path.exists(output_file):
                    with open(output_file, "w") as o:
                        ndjson.dump(train_data, o)
                elif len(train_data) > 0:
                    with open(output_file, "a") as o:
                        o.write("\n")
                        ndjson.dump(train_data, o)

                total_items += len(train_data)
                print(f"Collected: {total_items} - Ignored: {ignored_sentences}")

                if total_items > train_length:
                    break

        if total_items > train_length:
            break


@click.command()
@click.argument('corpus_dir')
def create_corpus(corpus_dir):

    files = glob.glob(os.path.join(corpus_dir, "*.zip"))
    nlp = spacy.load("en_core_web_sm")

    with open("notw_us_sources.json") as i:
        id2source = json.load(i)

    train_length = 1000000
    test_size = 1000

    error_generators = [
        # perfect.PassivePerfectWithoutHaveErrorGenerator(),
        # perfect.PerfectTenseWithoutHaveErrorGenerator(),
        # perfect.PerfectProgressiveWithIncorrectBeAndWithoutHaveErrorGenerator(),
        # perfect.PerfectProgressiveWithoutHaveErrorGenerator(),
        # passive.PassiveWithoutBeErrorGenerator(),
        # passive.PassiveWithIncorrectBeErrorGenerator()
        # agreement.SubjectVerbAgreementWithSimpleNounErrorGenerator(),
        # agreement.SubjectVerbAgreementWithPronounErrorGenerator(),
        # agreement.SubjectVerbAgreementWithIndefinitePronounErrorGenerator(),
        # perfect.PassivePerfectWithIncorrectParticipleErrorGenerator()
        # SubjectVerbAgreementWithInversionErrorGenerator(),
        # its_its_error_generator
        # subject_pronoun_error_generator,
        # object_pronoun_error_generator,
        # possessive_pronoun_error_generator,
        # their_error_generator
        # TokenReplacementErrorGenerator({"then": ["than"],
        #                                 "than": ["then"]},
        #                                GrammarError.THAN_THEN.value)
        # TokenReplacementErrorGenerator({"loose": ["lose"],
        #                                 "looses": ["loses"],
        #                                 "looser": ["loser"],
        #                                 "loosers": ["losers"],
        #                                 "lose": ["loose"],
        #                                 "loses": ["looses"],
        #                                 "loser": ["looser"],
        #                                 "losers": ["loosers"]
        #                                 },
        #                                GrammarError.LOOSE_LOSE.value)
        # agreement.SubjectVerbAgreementWithPronounErrorGenerator(),
        # agreement.IncorrectInfinitivePastGenerator(),
        # FragmentWithoutVerbOrAuxGenerator(),
        # TokenReplacementErrorGenerator({'too': ['two', 'to']},
        #                                GrammarError.TO_TWO_TOO_TOO_OPTIMAL.value,
        #                                probs=[0.1, 0.9])
        TokenReplacementErrorGenerator({'an': ['a']},
                                       GrammarError.ARTICLE.value)

        # TokenReplacementErrorGenerator({'the': ['he']},
        #                                GrammarError.HE_THE.value)
        # TokenReplacementErrorGenerator({"advise": ["advice"],
        #                                 "advises": ["advices"],
        #                                 "advised": ["adviced"],
        #                                 "advising": ["advicing"],
        #                                 "advice": ["advise"],
        #                                 "advices": ["advises"]},
        #                                GrammarError.ADVISE_ADVICE.value)
        ]

    for error_generator in error_generators:
        seen_sentences = set()
        output_name = error_generator.name.replace(" ", "_").replace("-", "_").lower()
        output_file = f"{output_name}.ndjson"
        get_data_from_files(files, id2source, seen_sentences, error_generator, train_length,
                            nlp, output_file, from_us=True, verbose=True)

if __name__ == "__main__":
    create_corpus()
