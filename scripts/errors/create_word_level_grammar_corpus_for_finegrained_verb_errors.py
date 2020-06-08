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
from quillnlp.grammar.verbs import perfect, agreement, passive, tense
from quillnlp.models.spacy.train import train_spacy_ner

PUNCTUATION = set([".", "?", "!"])

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
    text = text.replace(" n't", "n't")
    text = text.replace(" 's", "'s")
    text = text.replace(" 'll", "'ll")
    text = text.replace(" 'd", "'d")
    text = text.replace(" 're", "'re")
    text = text.replace(" 've", "'ve")
    text = re.sub("([\(]) ", "\\1", text)
    return text


def get_data_from_files(files, id2source, seen_sentences, error_generator, train_length, nlp,
                        output_file, from_us=True, verbose=False):

    # Count how much data we have already.
    total_items = 0
    if os.path.exists(output_file):
        with open(output_file) as i:
            data = ndjson.load(i)
            total_items = len(data)

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
                            text = " ".join(line[1:])
                            text = clean_text(text)

                            sentences = nltk.sent_tokenize(text)
                            for sentence in sentences:
                                if len(sentence.split()) > 3 and "@" not in sentence \
                                        and sentence[-1] in PUNCTUATION and sentence not in seen_sentences:
                                    seen_sentences.add(sentence)
                                    texts.append(sentence)

                print("Texts collected")
                docs = list(nlp.pipe(texts))
                print("Texts processed")

                # Process texts
                train_data = []
                for sentence in docs:
                    synthetic_sentence, entities = error_generator.generate_from_doc(sentence)

                    if synthetic_sentence != sentence.text:
                        if random.random() < 0.5:
                            if verbose:
                                print(sentence)
                                print(synthetic_sentence)
                                print(entities)
                                #print("")
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
                if total_items > train_length:
                    break

        if total_items > train_length:
            break


@click.command()
@click.argument('corpus_dir')
def create_corpus(corpus_dir):

    files = glob.glob(os.path.join(corpus_dir, "*.zip"))
    nlp = spacy.load("en")

    with open("notw_us_sources.json") as i:
        id2source = json.load(i)

    train_length = 100000
    test_size = 1000

    #error_generator = perfect.PerfectProgressiveWithIncorrectBeAndWithoutHaveErrorGenerator()
    #error_generator = perfect.PerfectTenseWithoutHaveErrorGenerator()
    #error_generator = tense.SimplePastInsteadOfPresentPerfectErrorGenerator()
    #error_generator = passive.PassivePastTenseAsParticipleErrorGenerator()
    #error_generator = passive.PassiveWithoutBeErrorGenerator()
    #error_generator = agreement.IncorrectThirdPersonErrorGenerator()
    #error_generator = agreement.SubjectVerbAgreementWithSimpleNoun()
    #error_generator = agreement.SubjectVerbAgreementWithPronounErrorGenerator()
    #error_generator = agreement.SubjectVerbAgreementWithInversionErrorGenerator()
    #error_generator = perfect.PerfectProgressiveWithoutHaveErrorGenerator()
    #error_generator = perfect.PassivePerfectWithIncorrectParticipleErrorGenerator()
    #error_generator = tense.SimplePastInsteadOfPastPerfectErrorGenerator()
    #error_generator = agreement.SubjectVerbAgreementWithEitherOrErrorGenerator()
    #error_generator = perfect.PassivePerfectWithoutHaveErrorGenerator()
    #error_generator = perfect.PassivePerfectWithIncorrectParticipleErrorGenerator()

    seen_sentences = set()

    output_file = error_generator.name.replace(" ", "_") + ".ndjson"
    get_data_from_files(files, id2source, seen_sentences, error_generator, train_length,
                        nlp, output_file, from_us=True, verbose=True)

    with open(output_file) as i:
        train_data = ndjson.load(i)

    if len(train_data) < train_length:
        get_data_from_files(files, id2source, seen_sentences, error_generator, train_length,
                            nlp, output_file, from_us=False, verbose=False)

    with open(output_file) as i:
        train_data = ndjson.load(i)

    train_data = [(x[0], {"entities": x[1]["entities"]}) for x in train_data]
    random.shuffle(train_data)

    test_data = train_data[-test_size:]
    dev_data = train_data[-test_size*2:-test_size]
    train_data = train_data[:-test_size*2]

    train_spacy_ner(train_data, dev_data, test_data, "/tmp/grammar_vfg",
                    error_generator.name.replace(" ", "_") + "_output.json")


if __name__ == "__main__":
    create_corpus()

