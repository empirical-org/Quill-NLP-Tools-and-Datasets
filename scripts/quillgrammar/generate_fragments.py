import os
import csv
import random
import click
from tqdm import tqdm
from collections import Counter

import spacy
from spacy.tokens import DocBin

from quillnlp.grammar.fragments import FragmentWithoutVerbGenerator, FragmentWithoutSubjectGenerator, \
    MissingObjectFragmentGenerator, prepositionalPhraseFragmentGenerator, \
    RelativeClauseFragmentGenerator, InfinitiveFragmentGenerator, NounPhraseFragmentGenerator, \
    FragmentWithoutAuxiliaryGenerator, VerbPhraseFragmentGenerator, DependentClauseFragmentGenerator, \
    KeeperFragmentFragmentGenerator
from quillnlp.grammar.myspacy import nlp
from quillnlp.corpora.notw import read_sentences

def get_transitive_verbs(f):
    transitives = set()
    with open(f) as i:
        reader = csv.reader(i, delimiter='\t')
        next(reader)

        for line in reader:
            verb = line[0]
            total = int(line[1])
            dobj = int(line[2])
            if total >= 10 and dobj/total >= 0.75:
                transitives.add(verb)

    return transitives

transitives = get_transitive_verbs('transitives.csv')

#f = '/home/yves/projects/grammar-api/quillgrammar/data/new_comprehension.csv'
f = '/home/yves/projects/grammar-api/new_comprehension.tsv'
output_path = '.'

NO_FRAGMENT = 'no_fragment'
FRAGMENT= 'fragment'
MISSING_SUBJECT_FRAGMENT = 'fragment_no_subject'
MISSING_VERB_FRAGMENT = 'fragment_no_verb'
MISSING_AUX_FRAGMENT = 'fragment_no_aux'
MISSING_OBJECT_FRAGMENT = 'fragment_no_object'
PP_FRAGMENT = 'fragment_prepositional_phrase'
ADV_CL_FRAGMENT = 'fragment_adverbial_clause'
REL_CL_FRAGMENT = 'fragment_relative_clause'
INF_FRAGMENT = 'fragment_infinitive_phrase'
NP_FRAGMENT = 'fragment_noun_phrase'
VP_FRAGMENT = 'fragment_verb_phrase'

MAX_FRAGMENT_COUNT = 5000
NO_FRAGMENT_COUNT = 50000

def add_random_noise(sentence):

    random_number = random.random()
    
    # deletion
    if random_number < 0.05:
        random_idx = random.randint(1, len(sentence))
        sentence = sentence[:random_idx-1] + sentence[random_idx:]

    # swap
    elif random_number < 0.1:
        random_idx = random.randint(2, len(sentence))
        sentence = sentence[:random_idx-2] + sentence[random_idx-1] + \
            sentence[random_idx-2] + sentence[random_idx:]

    # remove punctuation
    elif random_number < 0.15 and sentence[-1] == '.':
        sentence = sentence[:-1]

    return sentence


def create_instance(sentence, prompt, label_counter):
    generator_no_subj = FragmentWithoutSubjectGenerator()
    generator_no_verb = FragmentWithoutVerbGenerator()
    generator_no_aux = FragmentWithoutAuxiliaryGenerator()
    generator_no_obj = MissingObjectFragmentGenerator(transitives)
    generator_pp = prepositionalPhraseFragmentGenerator
    generator_advcl = DependentClauseFragmentGenerator()
    generator_relcl = RelativeClauseFragmentGenerator()
    generator_inf = InfinitiveFragmentGenerator()
    generator_np = NounPhraseFragmentGenerator()
    generator_vp = VerbPhraseFragmentGenerator()

    candidate_fragments = []
    doc = nlp(sentence)
    for label, generator in [(MISSING_SUBJECT_FRAGMENT, generator_no_subj),
                             (MISSING_OBJECT_FRAGMENT, generator_no_obj),
                             (MISSING_VERB_FRAGMENT, generator_no_verb),
                             (MISSING_AUX_FRAGMENT, generator_no_aux),
                             (PP_FRAGMENT, generator_pp),
                             (ADV_CL_FRAGMENT, generator_advcl),
                             (REL_CL_FRAGMENT, generator_relcl),
                             (INF_FRAGMENT, generator_inf),
                             (NP_FRAGMENT, generator_np),
                             (VP_FRAGMENT, generator_vp)
                             ]:

        if label in label_counter and label_counter[label] >= MAX_FRAGMENT_COUNT:
            continue
        else:
            fragment, _, relevant = generator.generate_from_doc(doc, prompt)
            if relevant:
                candidate_fragments.append((label, fragment))

    if len(candidate_fragments) > 0:
        label, sentence = random.choice(candidate_fragments)

        return sentence, label, label_counter
    return None, None, label_counter


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

    label_counter = Counter()

    print('Creating fragments from NOTW data')
    for sentence in tqdm(notw_sentences[:250000]):
        if label_counter and min(label_counter.values()) >= MAX_FRAGMENT_COUNT:
            break

        instance, label, label_counter = create_instance(sentence, '', label_counter)

        if instance is not None and instance not in instance_set:
            data.append((add_random_noise(instance), label))
            label_counter.update([label])
            instance_set.add(instance)

    random.shuffle(notw_sentences)
    for sentence in notw_sentences[:NO_FRAGMENT_COUNT]:
        data.append((add_random_noise(sentence), NO_FRAGMENT))

    print('Instances:', len(data))
    labels = Counter([d[1] for d in data])
    print(labels)

    return data


def write_output(data, output_path):
    db = DocBin()
    nlp = spacy.blank('en')

    random.shuffle(data)
    for sentence, label in tqdm(data):
        doc = nlp.make_doc(sentence)
        doc.cats = {
            NO_FRAGMENT: 0,
            MISSING_VERB_FRAGMENT: 0,
            MISSING_AUX_FRAGMENT: 0,
            MISSING_SUBJECT_FRAGMENT: 0,
            MISSING_OBJECT_FRAGMENT: 0,
            PP_FRAGMENT: 0,
            ADV_CL_FRAGMENT: 0,
            REL_CL_FRAGMENT: 0,
            INF_FRAGMENT: 0,
            NP_FRAGMENT: 0,
            VP_FRAGMENT: 0
        }

        doc.cats[label] = 1.0
        db.add(doc)
    db.to_disk(output_path)


def write_output_binary(data, output_path):
    db = DocBin()
    nlp = spacy.blank('en')

    random.shuffle(data)
    for sentence, label in tqdm(data):
        doc = nlp.make_doc(sentence)
        doc.cats = {
            NO_FRAGMENT: 0,
            FRAGMENT: 0
        }

        if label == NO_FRAGMENT:
            doc.cats = {FRAGMENT: 0, NO_FRAGMENT: 1}
        else:
            doc.cats = {FRAGMENT: 1, NO_FRAGMENT: 0}

        db.add(doc)
    db.to_disk(output_path)


@click.command()
@click.argument('grammar_file')
@click.argument('notw_file')
def run(grammar_file, notw_file):
    #data = read_grammar_model_output(grammar_file)
    data = []
    data.extend(read_notw_data(notw_file))
    random.shuffle(data)
    test_size = int(len(data)/10)

    with open('fragments_synthetic.tsv', 'w') as o:
        writer = csv.writer(o, delimiter='\t')
        for sentence, label in data[:10000]:
            writer.writerow([sentence, label])

    write_output(data[:test_size], os.path.join(output_path, 'test.spacy'))
    write_output(data[test_size:test_size*2], os.path.join(output_path, 'dev.spacy'))
    write_output(data[test_size*2:], os.path.join(output_path, 'train.spacy'))


if __name__ == '__main__':
    run()