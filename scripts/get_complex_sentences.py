from os import write
import re
import spacy
import random
from tqdm import tqdm
from spacy.tokens import DocBin


from quillnlp.corpora.notw import read_sentences

RUNON_LABEL = 'runon'
CORRECT_LABEL = 'correct'

nlp = spacy.load('en_core_web_sm')

corpus_dir = '/home/yves/data/newsoftheworld/'
notw_sentences = read_sentences(corpus_dir, n=100000000, complex=True)

input('done')

total = 0
with open('complex_sentences.txt') as i:
    lines = i.readlines()

complex_sentences = []
for line in tqdm(lines):
    sentence = line.strip()
    if ' and ' in sentence:
        clauses = re.split(r' because | but | so | and ', sentence)

        clauses_with_subject = 0
        for clause in clauses:
            doc = nlp(clause)
            deps = set([t.dep_ for t in doc])
            if 'nsubj' in deps or 'nsubjpass' in deps:
                clauses_with_subject += 1

        if len(clauses) == clauses_with_subject:
            # print(sentence)
            # print(clauses)
            # print()
            total += 1
            complex_sentences.append(sentence)

other_sentence_file = 'notw_sentences.txt'
with open(other_sentence_file) as i:
    other_sentences = [line.strip() for line in i if not '  ' in line]

db = DocBin()

random.shuffle(complex_sentences)

def write_corpus(complex_sentences, other_sentences, output_path):
    for sentence in tqdm(complex_sentences):

        sentence_without_and = re.sub(' and ', ' ', sentence, 1)

        doc_runon = nlp.make_doc(sentence_without_and)
        doc_original = nlp.make_doc(sentence)

        doc_runon.cats = {
            RUNON_LABEL: 1.0,
            CORRECT_LABEL: 0
        }

        doc_original.cats = {
            RUNON_LABEL: 0,
            CORRECT_LABEL: 1.0
        }

        db.add(doc_runon)
        db.add(doc_original)

    for sentence in tqdm(other_sentences):
        doc = nlp(sentence)

        doc.cats = {
            RUNON_LABEL: 0,
            CORRECT_LABEL: 1.0
        }

        db.add(doc)

    db.to_disk(output_path)


write_corpus(complex_sentences[:1000], other_sentences[:1000], 'runon_dev.spacy')
write_corpus(complex_sentences[1000:], other_sentences[1000:50000], 'runon_train.spacy')
