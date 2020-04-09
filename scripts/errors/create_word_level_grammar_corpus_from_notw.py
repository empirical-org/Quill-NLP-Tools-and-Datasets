import spacy
import ndjson
import click
import random
import os
import re
import glob
import zipfile

from tqdm import tqdm
from quillnlp.grammar.corpus import replace


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

    return id2source


US_SOURCES = set(["Yahoo News", "Huffington Post", "ABC News", "NPR", "Los Angeles Times",
                  "Washington Post", "New York Times", "USA TODAY", "Chicago Tribune",
                  "CNN", "New York Post", "Fox News", "CNBC", "CBS News"])

@click.command()
@click.argument('corpus_dir')
@click.argument('output_file')
@click.option('--error_ratio', default=1/4)
def create_corpus(corpus_dir, output_file, error_ratio):

    files = glob.glob(os.path.join(corpus_dir, "*.zip"))

    def file_len(fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    train_data = []
    nlp = spacy.load("en")

    id2source = read_sources(corpus_dir)

    for f in files:
        print(f)
        print(len(train_data))
        with zipfile.ZipFile(f) as myzip:
            zipped_files = myzip.namelist()
            for zf in zipped_files:
                with myzip.open(zf) as i:
                    for line in i:
                            line = line.decode("latin-1").strip().split()
                            try:
                                text_id = line[0][2:]
                            except:
                                continue
                            if text_id in id2source:
                                source = id2source[text_id]
                                if source in US_SOURCES:
                                    text = " ".join(line[1:])
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

                                    doc = nlp(text)

                                    for sentence in doc.sents:
                                        if len(sentence) > 3 and "@" not in sentence.text:

                                            synthetic_sentence, errors = replace(sentence, error_ratio)
                                            if len(errors) > 0:
                                                train_data.append({"orig_sentence": sentence.text.strip(),
                                                                   "synth_sentence": synthetic_sentence.strip(),
                                                                   "entities": errors})
                                            else:
                                                train_data.append({"orig_sentence": sentence.text.strip()})

                                            if len(train_data) % 100000 == 0:
                                                with open(output_file, "w") as o:
                                                    ndjson.dump(train_data, o)
                            #else:
                            #    print(f, text_id)


if __name__ == "__main__":
    create_corpus()

