import os
import csv
import random
import click
from tqdm import tqdm
from collections import Counter

import spacy
from spacy.tokens import DocBin

from quillnlp.grammar.fragments import FragmentWithoutVerbGenerator, FragmentWithoutSubjectGenerator, \
    MissingObjectFragmentGenerator, prepositionalPhraseFragmentGenerator, adverbialClauseFragmentGenerator, \
    relativeClauseFragmentGenerator, infinitiveFragmentGenerator, nounPhraseFragmentGenerator
from quillnlp.grammar.myspacy import nlp
from quillnlp.corpora.notw import read_sentences

#f = '/home/yves/projects/grammar-api/quillgrammar/data/new_comprehension.csv'
f = '/home/yves/projects/grammar-api/new_comprehension.tsv'
output_path = '.'

NO_FRAGMENT = 'no_fragment'
MISSING_SUBJECT_FRAGMENT = 'fragment_no_subject'
MISSING_VERB_FRAGMENT = 'fragment_no_verb'
MISSING_OBJECT_FRAGMENT = 'fragment_no_object'
PP_FRAGMENT = 'fragment_prepositional_phrase'
ADV_CL_FRAGMENT = 'fragment_adverbial_clause'
REL_CL_FRAGMENT = 'fragment_relative_clause'
INF_FRAGMENT = 'fragment_infinitive_phrase'
NP_FRAGMENT = 'fragment_noun_phrase'


def create_instance(sentence, prompt):
    generator_no_subj = FragmentWithoutSubjectGenerator()
    generator_no_verb = FragmentWithoutVerbGenerator()
    generator_no_obj = MissingObjectFragmentGenerator()
    generator_pp = prepositionalPhraseFragmentGenerator
    generator_advcl = adverbialClauseFragmentGenerator
    generator_relcl = relativeClauseFragmentGenerator
    generator_inf = infinitiveFragmentGenerator
    generator_np = nounPhraseFragmentGenerator


    candidate_fragments = []
    doc = nlp(sentence)
    for label, generator in [(MISSING_SUBJECT_FRAGMENT, generator_no_subj),
                             (MISSING_OBJECT_FRAGMENT, generator_no_obj),
                             (MISSING_VERB_FRAGMENT, generator_no_verb),
                             (PP_FRAGMENT, generator_pp),
                             (ADV_CL_FRAGMENT, generator_advcl),
                             (REL_CL_FRAGMENT, generator_relcl),
                             (INF_FRAGMENT, generator_inf),
                             (NP_FRAGMENT, generator_np)]:

        fragment, _, relevant = generator.generate_from_doc(doc, prompt)
        if relevant:
            candidate_fragments.append((label, fragment))

    random_number = random.random()

    if random_number < 0.5:
        label, sentence = random.choice(candidate_fragments)
    else:
        label = NO_FRAGMENT

    return sentence, label


def read_csv_input(f):

    data = []
    instance_set = set()

    print('Creating fragments from Quill data')
    with open(f) as i:
        reader = csv.reader(i, delimiter=',')
        for line in tqdm(reader):
            sentence, prompt, _, _, _ = line

            instance, label = create_instance(sentence, prompt)

            if instance not in instance_set:
                data.append((instance, label))
                instance_set.add(instance)

    print('Fetching NOTW data')
    with open('data/raw/notw_sentences.txt') as i:
        notw_sentences = [line.strip() for line in i]

    print('Creating fragments from NOTW data')
    for sentence in tqdm(notw_sentences):
        instance, label = create_instance(sentence, prompt)

        if instance not in instance_set:
            data.append((instance, label))
            instance_set.add(instance)

    return data


def read_grammar_model_output(grammar_file):
    data = []

    instance_set = set()
    print('Creating fragments from Quill data')
    with open(grammar_file) as i:
        reader = csv.reader(i, delimiter='\t')
        for line in tqdm(reader):
            sentence, prompt, error, _, _ = line
            if error == '':
                instance, label = create_instance(sentence, prompt)
                if instance not in instance_set:
                    data.append((instance, label))
                    instance_set.add(instance)

    return data


def read_notw_data(notw_sentence_file):

    data = []
    instance_set = set()
    print('Fetching NOTW data')
    with open(notw_sentence_file) as i:
        notw_sentences = [line.strip() for line in i]

    print('Creating fragments from NOTW data')
    for sentence in tqdm(notw_sentences[:200000]):
        instance, label = create_instance(sentence, '')

        if instance not in instance_set:
            data.append((instance, label))
            instance_set.add(instance)

    print('Instances:', len(data))
    labels = Counter([d[1] for d in data])
    print(labels)

    return data


def write_output(data, output_path):
    db = DocBin()
    nlp = spacy.blank('en')
    for sentence, label in tqdm(data):
        doc = nlp.make_doc(sentence)
        doc.cats = {
            NO_FRAGMENT: 0,
            MISSING_VERB_FRAGMENT: 0,
            MISSING_SUBJECT_FRAGMENT: 0,
            MISSING_OBJECT_FRAGMENT: 0,
            PP_FRAGMENT: 0,
            ADV_CL_FRAGMENT: 0,
            REL_CL_FRAGMENT: 0
        }

        doc.cats[label] = 1.0
        db.add(doc)
    db.to_disk(output_path)


@click.command()
@click.argument('grammar_file')
@click.argument('notw_file')
def run(grammar_file, notw_file):
    data = read_grammar_model_output(grammar_file)
    data.extend(read_notw_data(notw_file))
    random.shuffle(data)
    test_size = int(len(data)/10)
    write_output(data[:test_size], os.path.join(output_path, 'test.spacy'))
    write_output(data[test_size:test_size*2], os.path.join(output_path, 'dev.spacy'))
    write_output(data[test_size*2:], os.path.join(output_path, 'train.spacy'))


if __name__ == '__main__':
    run()