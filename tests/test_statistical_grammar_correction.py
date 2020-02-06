import re
import requests
import spacy
from spacy.gold import biluo_tags_from_offsets
from sklearn.metrics import classification_report

SPACY_DIRECTORY = "/tmp/grammar/"

f = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRBi-FtMTBFnfvHI-Fgr91HNmQdOzWgQ5FRyu1DfO4RiWzuDZLmYrsc5GFkT-M3Lbkk444tXyrvipi8/pub?gid=0&single=true&output=tsv"

nlp = spacy.load(SPACY_DIRECTORY)


data = requests.get(f)
lines = re.split("\n", data.text)

error_types = set()
predicted_tags, correct_tags = [], []
for line in lines[1:]:
    line = line.strip().split("\t")
    if len(line) >= 5:
        error_type, error_subtype, sentence, error_start, error_end = line[:5]
        error_start = int(error_start) if error_start else None
        error_end = int(error_end) if error_end else None
    else:
        print("Invalid line", line)

    error_type = error_type.upper()
    error_types.add(error_type)

    doc = nlp(sentence)

    predicted_entities = [(e.start_char, e.end_char, e.label_) for e in doc.ents]
    correct_entities = [(error_start, error_end, error_type)] if error_start else []

    print(sentence, predicted_entities)

    sentence_predicted_tags = [t.split("-")[-1] for t in biluo_tags_from_offsets(doc, predicted_entities)]
    sentence_correct_tags = [t.split("-")[-1] for t in biluo_tags_from_offsets(doc, correct_entities)]

    predicted_tags += sentence_predicted_tags
    correct_tags += sentence_correct_tags

print(classification_report(correct_tags, predicted_tags, labels=list(error_types)))