# Code for reading the News of the World corpus.

import re
import os
import glob
import tqdm
import nltk
import json
import zipfile

from typing import List

PUNCTUATION = set([".", "?", "!"])

# The NOTW corpus contains sources from many different countries. The list below lists
# the sources from the US that we use.
US_SOURCES = set(["Yahoo News", "Huffington Post", "ABC News", "NPR", "Los Angeles Times",
                  "Washington Post", "New York Times", "USA TODAY", "Chicago Tribune",
                  "CNN", "New York Post", "Fox News", "CNBC", "CBS News"])

NOTW_SOURCE_FILE = 'notw_sources.json'


def read_sources(corpus_dir):
    """
    Create a file that maps every text id in the NOTW corpus to
    its source. This json file will be used to determine the source
    of every NOTW document when the corpus is read.
    """
    source_files = glob.glob(os.path.join(corpus_dir, "sources/*.zip"))

    id2source = {}
    for f in tqdm(source_files):
        with zipfile.ZipFile(f) as myzip:
            ftxt = os.path.basename(f).replace(".zip", ".txt")
            with myzip.open(ftxt) as i:
                for line in i:
                    line = line.decode("latin-1").strip().split("\t")
                    source = line[4]
                    text_id = line[0]
                    id2source[text_id] = source

    with open(NOTW_SOURCE_FILE, "w") as o:
        json.dump(id2source, o)

    return id2source


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


def is_a_good_sentence(sentence: str) -> bool:
    """Determines if we want to keep a sentence. Throws out sentences
    that are too short, contain a @ and do not end in a punctuation sign.

    Args:
        sentence (str): the sentence to check

    Returns:
        bool: True if the sentence is fine, False otherwise.
    """
    return len(sentence.split()) > 3 \
            and "@" not in sentence \
            and sentence[-1] in PUNCTUATION


def is_a_complex_sentence(sentence: str) -> bool:
    """Determines is a sentence if a complex sentence. Complex sentences
    must look like a Quill sentence (i.e. contain because/but/so), and
    also have 'and' after 'because/but/so'. These sentences are used
    to create synthetic runons.

    Args:
        sentence (str): the sentence to check

    Returns:
        bool: True if the sentence is complex, False otherwise.
    """
    return re.search(r' because .* and ', sentence) \
        or re.search(r' but .* and ', sentence) \
        or re.search(r' so .* and ', sentence)


def read_sentences(corpus_dir: str, max_sentences: int=1000, is_complex: bool=False) -> List[str]:
    """ Reads the News of the World corpus and splits it into sentences.

    Args:
        corpus_dir (str): the directory with the News of the World corpus
        max_sentences (int, optional): the maximum number of sentences that should be returned.
            Defaults to 1000.
        is_complex (bool, optional): True if only complex sentence should be returned.
            Defaults to False.

    Returns:
        _type_: _description_
    """

    with open(NOTW_SOURCE_FILE) as i:
        id2source = json.load(i)

    files = glob.glob(os.path.join(corpus_dir, "*.zip"))

    notw_sentences = set()
    for f in tqdm(files):
        with zipfile.ZipFile(f) as myzip:
            zipped_files = myzip.namelist()
            for zf in zipped_files:

                # Read every zipped file
                with myzip.open(zf) as i:
                    for line in i:
                        line = line.decode("latin-1").strip().split()

                        # Locate the text id. If it is not found,
                        # ignore the line
                        try:
                            text_id = line[0][2:]
                        except:
                            continue

                        # If we know the source of the text id, analyze
                        # the text and split it into sentences
                        if text_id in id2source:
                            text = " ".join(line[1:])
                            text = clean_text(text)
                            sentences = nltk.sent_tokenize(text)
                            for sentence in sentences:
                                # If we only want complex sentences, and the sentence is not complex,
                                # ignore it.
                                if complex and not is_a_complex_sentence(sentence):
                                    continue

                                # If the sentence is good, and we don't have it yet, keep it.
                                if is_a_good_sentence(sentence) and sentence not in notw_sentences:
                                    notw_sentences.add(sentence)

                                    if len(notw_sentences) > max_sentences:
                                        break

                if len(notw_sentences) > max_sentences:
                    break

        if len(notw_sentences) > max_sentences:
            break

    return list(notw_sentences)