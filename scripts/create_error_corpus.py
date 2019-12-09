import gzip
import spacy
import random
from collections import defaultdict

from quillnlp.utils import detokenize

MISSPELLING_FILE = "data/validated/birkbeck_misspellings.txt"
CORPUS_FILE = "/Users/yvespeirsman/Corpora/EN/Wikipedia/enwiki-first5sents.txt.gz"

nlp = spacy.load("en")

with open(MISSPELLING_FILE) as i:

    misspellings = defaultdict(lambda: [])
    current_word = None
    for line in i:
        line = line.strip()
        if line.startswith("$"):
            current_word = line[1:]
        elif current_word is not None:
            misspellings[current_word].append(line)

with gzip.open(CORPUS_FILE, "rb") as i:
    for line in i:
        doc = nlp(line.decode("utf-8"))
        for sentence in doc.sents:
            new_sentence = ""
            for token in sentence:
                if token.orth_ in misspellings:
                    number_of_misspellings = len(misspellings[token.text])
                    new_token = random.choice([token.text]*number_of_misspellings*10 + misspellings[token.text])
                    new_sentence += new_token + token.whitespace_
                else:
                    new_sentence += token.text_with_ws

            if new_sentence.strip() != sentence.text.strip():
                print(sentence.text.strip())
                print(new_sentence.strip())
                print("--")


