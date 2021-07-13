import re
import os
import glob
import nltk
import json
import zipfile

PUNCTUATION = set([".", "?", "!"])

# The NOTW corpus contains sources from many different countries. The list below lists
# the sources we use.
US_SOURCES = set(["Yahoo News", "Huffington Post", "ABC News", "NPR", "Los Angeles Times",
                  "Washington Post", "New York Times", "USA TODAY", "Chicago Tribune",
                  "CNN", "New York Post", "Fox News", "CNBC", "CBS News"])


def read_sources(corpus_dir):
    """
    Create a file that maps every text id in the NOTW corpus to
    its source.
    """
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


def read_sentences(corpus_dir, n=1000):

    with open("notw_us_sources.json") as i:
        id2source = json.load(i)

    files = glob.glob(os.path.join(corpus_dir, "*.zip"))

    notw_sentences = set()
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
                        if text_id in id2source:
                            text = " ".join(line[1:])
                            text = clean_text(text)

                            sentences = nltk.sent_tokenize(text)
                            for sentence in sentences:
                                if len(sentence.split()) > 3 and "@" not in sentence \
                                        and sentence[-1] in PUNCTUATION and sentence not in notw_sentences:
                                    notw_sentences.add(sentence)

        if len(notw_sentences) > n:
            break

    return list(notw_sentences)

