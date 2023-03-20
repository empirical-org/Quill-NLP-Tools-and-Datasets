import os
import csv
import random
import ndjson
import click
from scripts.test_fragments import NO_FRAGMENT_LABEL
from tqdm import tqdm
from collections import Counter
from grammar_files2 import read_grammar_data

import spacy
from spacy.tokens import DocBin, Span

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

MAX_FRAGMENT_COUNT = 10000
NO_FRAGMENT_COUNT = 200000


def identify_prompt(sentence):
    split_so = sentence.split(', so ')
    if len(split_so) > 1:
        return split_so[0] + ', so'

    split_but = sentence.split(', but ')
    if len(split_but) > 1:
        return split_but[0] + ', but'

    split_because = sentence.split(' because ')
    if len(split_because) > 1:
        return split_because[0] + ' because'

    print('Could not identify prompt:')
    print(sentence)
    return ''


def add_random_noise(sentence):

    random_number = random.random()
    
    # deletion
    if random_number < 0.05 and len(sentence) > 2:
        random_idx = random.randint(1, len(sentence))
        sentence = sentence[:random_idx-1] + sentence[random_idx:]

    # swap
    elif random_number < 0.1 and len(sentence) > 3:
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
    # generator_no_obj = MissingObjectFragmentGenerator(transitives)
    generator_pp = prepositionalPhraseFragmentGenerator
    generator_advcl = DependentClauseFragmentGenerator()
    generator_relcl = RelativeClauseFragmentGenerator()
    generator_inf = InfinitiveFragmentGenerator()
    generator_np = NounPhraseFragmentGenerator()
    generator_vp = VerbPhraseFragmentGenerator()

    candidate_fragments = []
    doc = nlp(sentence)
    for label, generator in [(MISSING_SUBJECT_FRAGMENT, generator_no_subj),
                            #  (MISSING_OBJECT_FRAGMENT, generator_no_obj),
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


def create_synthetic_data(grammar_file, notw_sentence_file):

    data = []
    instance_set = set()

    raw_sentences = []

    print('Fetching grammar data')
    with open(grammar_file) as i:
        reader = csv.reader(i, delimiter='\t')
        for line in tqdm(reader):
            sentence, error, _, _ = line
            if error == '':
                prompt = identify_prompt(sentence)
                if prompt:
                    raw_sentences.append((sentence, prompt))

    print(len(raw_sentences), 'sentences')

    print('Fetching NOTW data')
    with open(notw_sentence_file) as i:
        # a double space is often an indication that the sentence is preceded by a title
        # or a caption
        raw_sentences.extend([(line.strip(), '') for line in i if '  ' not in line and len(line) < 150])
    print(len(raw_sentences), 'sentences')

    label_counter = Counter()

    print('Creating fragments from NOTW data')
    for sentence, prompt in tqdm(raw_sentences[:250000]):
        if label_counter and min(label_counter.values()) >= MAX_FRAGMENT_COUNT:
            break

        instance, label, label_counter = create_instance(sentence, prompt, label_counter)

        if instance is not None and len(instance) > 3 and instance not in instance_set:
            data.append((add_random_noise(instance), label))
            label_counter.update([label])
            instance_set.add(instance)

    random.shuffle(raw_sentences)
    no_fragments_added = 0
    for (sentence, prompt) in raw_sentences:
        data.append((add_random_noise(sentence), NO_FRAGMENT))
        no_fragments_added += 1
        if "," in sentence:
            data.append((add_random_noise(sentence.replace(",", "")), NO_FRAGMENT))
            no_fragments_added += 1
        if no_fragments_added >= NO_FRAGMENT_COUNT:
            break

    print('Instances:', len(data))
    labels = Counter([d[1] for d in data])
    print(labels)

    return data


def find_index_from_offsets(doc, start, end):

    first_token_start = None
    next_token_start = None

    for token in doc:
        if token.idx >= start and first_token_start is None:
            first_token_start = token.i
        if token.idx > end and next_token_start is None:
            next_token_start = token.i

    if next_token_start is None:
        next_token_start = len(doc)

    return first_token_start, next_token_start


def write_output(data, output_path):
    db = DocBin()
    nlp = spacy.blank('en')

    random.shuffle(data)
    for sentence, label in tqdm(data):
        doc = nlp.make_doc(sentence)

        # Fragment data
        if isinstance(label, str):
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

        # Grammar data
        elif isinstance(label, dict):
            entities = []
            start_idx_returned_none = False
            for ent in label['entities']:
                start_idx, end_idx = find_index_from_offsets(doc, ent[0], ent[1])
                if start_idx and end_idx:
                    entities.append(Span(doc, start_idx, end_idx, ent[2]))
                else:
                    start_idx_returned_none = True
            try:
                if not start_idx_returned_none:
                    doc.set_ents(entities)
                    db.add(doc)
            except:
                continue
        else:
            raise ValueError('Unknown label type for', label)

    db.to_disk(output_path)


def write_output_binary(data, output_path):
    db = DocBin()
    nlp = spacy.blank('en')

    random.shuffle(data)
    for sentence, label in tqdm(data):
        doc = nlp.make_doc(sentence)

        if isinstance(label, str):
            doc.cats = {
                NO_FRAGMENT: 0,
                FRAGMENT: 0
            }

            if label == NO_FRAGMENT:
                doc.cats = {FRAGMENT: 0, NO_FRAGMENT: 1}
            else:
                doc.cats = {FRAGMENT: 1, NO_FRAGMENT: 0}

            db.add(doc)

        # Grammar data
        elif isinstance(label, dict):

            if random.randint(1,5) == 5:
                doc.cats = {FRAGMENT: 0, NO_FRAGMENT: 1}

            entities = []
            start_idx_returned_none = False
            for ent in label['entities']:
                start_idx, end_idx = find_index_from_offsets(doc, ent[0], ent[1])
                if start_idx and end_idx:
                    entities.append(Span(doc, start_idx, end_idx, ent[2]))
                else:
                    start_idx_returned_none = True
            try:
                if not start_idx_returned_none:
                    doc.set_ents(entities)
                    db.add(doc)
            except:
                continue
        else:
            raise ValueError('Unknown label type for', label)


    db.to_disk(output_path)


def read_fragment_data(grammar_file, notw_file):
    data = [] = create_synthetic_data(grammar_file, notw_file)
    random.shuffle(data)
    test_size = int(len(data)/10)

    with open('fragments_synthetic.tsv', 'w') as o:
        writer = csv.writer(o, delimiter='\t')
        for sentence, label in data[:10000]:
            writer.writerow([sentence, label])

    fragment_test = data[:test_size]
    fragment_dev = data[test_size:test_size*2]
    fragment_train = data[test_size*2:]

    return fragment_train, fragment_dev, fragment_test


@click.command()
@click.argument('grammar_file')
@click.argument('notw_file')
def run(grammar_file, notw_file):

    # Read fragment data
    fragment_train, fragment_dev, fragment_test = read_fragment_data(grammar_file, notw_file)

    # Read grammar data    
    grammar_train, grammar_dev, grammar_test = read_grammar_data()

    print('Fragment test', len(fragment_test))
    print('Grammar test', len(grammar_test))

    write_output_binary(fragment_test + grammar_test, os.path.join(output_path, 'test.spacy'))
    write_output_binary(fragment_dev + grammar_dev, os.path.join(output_path, 'dev.spacy'))

    OUTPUT_DIR = 'grammar-fragment-train'
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    grammar_cutoff = 200000
    train_data = grammar_train[:grammar_cutoff] + fragment_train #* 5
    # train_data = fragment_train
    random.shuffle(train_data)

    print('Grammar train:', grammar_cutoff)
    print('Fragment train:', len(fragment_train))
    
    chunk_size = 1000000
    for i in range(0, len(train_data), chunk_size):
        write_output_binary(train_data[i:i+chunk_size], os.path.join(OUTPUT_DIR, f"train{int(i/chunk_size)}.spacy"))


if __name__ == '__main__':
    run()