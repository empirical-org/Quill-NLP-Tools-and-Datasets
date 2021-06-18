import os
import csv
import random
from tqdm import tqdm

import spacy
from spacy.tokens import DocBin

from quillnlp.grammar.fragments import FragmentWithoutVerbGenerator, FragmentWithoutSubjectGenerator
from quillnlp.grammar.myspacy import nlp

f = '/home/yves/projects/grammar-api/quillgrammar/data/new_comprehension.csv'
output_path = '/tmp/fragments/'

generator1 = FragmentWithoutSubjectGenerator()
generator2 = FragmentWithoutVerbGenerator()

data = []

with open(f) as i:
    reader = csv.reader(i, delimiter=',')
    for line in tqdm(reader):
        sentence, prompt, _, _, _ = line

        random_number = random.random()
        if random_number < 0.25:
            generator = generator1
            doc = nlp(sentence)
            sentence, _, _ = generator.generate_from_doc(doc, prompt)
            label = 'fragment'
        elif random_number < 0.5:
            generator = generator2
            doc = nlp(sentence)
            sentence, _, _ = generator.generate_from_doc(doc, prompt)
            label = 'fragment'
        else:
            label = 'no_fragment'

        data.append((sentence, label))

def write_output(data, output_path):
    db = DocBin()
    nlp = spacy.blank('en')
    for sentence, label in tqdm(data):
        doc = nlp.make_doc(sentence)
        if label == 'fragment':
            doc.cats = {'fragment': 1.0, 'no_fragment': 0}
        else:
            doc.cats = {'fragment': 0, 'no_fragment': 1.0}
        db.add(doc)
    db.to_disk(output_path)


random.shuffle(data)
test_size = int(len(data)/10)
write_output(data[:test_size], os.path.join(output_path, 'test.spacy'))
write_output(data[test_size:test_size*2], os.path.join(output_path, 'dev.spacy'))
write_output(data[test_size*2:], os.path.join(output_path, 'train.spacy'))
