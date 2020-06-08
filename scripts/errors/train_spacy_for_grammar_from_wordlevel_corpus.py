import random
from pathlib import Path
import spacy
import json
import ndjson
from collections import Counter

from quillnlp.models.spacy.train import train_spacy_ner

TEST_SIZE = 5000
DEV_SIZE = 5000

nlp = spacy.load("en")

files = ["wiki_errors.ndjson", "subtitles.ndjson", "notw.ndjson"]

train_data = []
for f in files:
    with open(f) as i:
        train_data += ndjson.load(i)[:7200000]

seen_sentences = set()
filtered_train_data = []
for sentence in train_data:
    if "synth_sentence" in sentence and sentence["synth_sentence"] not in seen_sentences:
        filtered_train_data.append((sentence["synth_sentence"], {"entities": sentence["entities"]}))
        seen_sentences.update([sentence["synth_sentence"]])
    elif "orig_sentence" in sentence and sentence["orig_sentence"] not in seen_sentences:
        filtered_train_data.append((sentence["orig_sentence"], {"entities": []}))
        seen_sentences.update([sentence["orig_sentence"]])

train_data = filtered_train_data
random.shuffle(train_data)

TEST_DATA = train_data[-TEST_SIZE:]
DEV_DATA = train_data[-(TEST_SIZE + DEV_SIZE):-TEST_SIZE]
TRAIN_DATA = train_data[:len(train_data) - TEST_SIZE - DEV_SIZE]
TRAIN_DATA = TRAIN_DATA[:20000000]

train_set = set([x[0] for x in TRAIN_DATA])
test_set = set([x[0] for x in TEST_DATA])
intersection = train_set & test_set
if len(intersection) > 0:
    print("Test sentences in training set:", len(intersection))

for x in intersection:
    print(x, len(x))

print("Train:", len(TRAIN_DATA))
print("Dev:", len(DEV_DATA))
print("Test:", len(TEST_DATA))

error_counter = Counter()
for item in TRAIN_DATA:
    error_counter.update([e[2] for e in item[1]["entities"]])

print(error_counter)


def main(output_dir=None):
    train_spacy_ner(TRAIN_DATA, DEV_DATA, TEST_DATA, output_dir)


if __name__ == "__main__":
    main(output_dir="/tmp/grammar20M/")
