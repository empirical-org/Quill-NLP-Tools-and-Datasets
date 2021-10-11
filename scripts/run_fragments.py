import re
import csv
import spacy
import click
from tqdm import tqdm
from sklearn.metrics import classification_report
from quillnlp.grammar.fragment_map import fragment_label_map

FRAGMENT_LABEL = 'fragment'
NO_FRAGMENT_LABEL = 'no_fragment'

MISSING_SUBJECT_FRAGMENT = 'fragment_no_subject'
MISSING_VERB_FRAGMENT = 'fragment_no_verb'
MISSING_OBJECT_FRAGMENT = 'fragment_no_object'
MISSING_AUX_FRAGMENT = 'fragment_no_aux'
PP_FRAGMENT = 'fragment_prepositional_phrase'
ADV_CL_FRAGMENT = 'fragment_adverbial_clause'
REL_CL_FRAGMENT = 'fragment_relative_clause'
INF_FRAGMENT = 'fragment_infinitive_phrase'
NP_FRAGMENT = 'fragment_noun_phrase'
VP_FRAGMENT = 'fragment_verb_phrase'

known_fragments = set([
    MISSING_SUBJECT_FRAGMENT,
    MISSING_OBJECT_FRAGMENT,
    MISSING_VERB_FRAGMENT,
    MISSING_AUX_FRAGMENT,
    PP_FRAGMENT,
    ADV_CL_FRAGMENT,
    REL_CL_FRAGMENT,
    INF_FRAGMENT,
    NP_FRAGMENT,
    VP_FRAGMENT
])


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


@click.command()
@click.argument('model_path')
@click.argument('test_file')
def evaluate(model_path, test_file):

    print(test_file)
    data = []
    with open(test_file) as i:
        reader = csv.reader(i, delimiter=',')
        for line in reader:
            if len(line) == 2:
                data.append(line)
            elif len(line) == 1:
                data.append((line[0], identify_prompt(line[0])))
            elif len(line[9]) > 0:
                data.append((line[9], line[8]))


    print(data[:3])
    print(len(data), 'sentences')
    nlp = spacy.load(model_path)
    output_file = test_file.replace('.csv', '_fragments_fine_noise_cleaned.tsv')

    with open(output_file, 'w') as o:
        writer = csv.writer(o, delimiter='\t')

        for sentence, prompt in tqdm(data):

            response = sentence.replace(prompt, '').strip()
            if len(response) > 1:
                response_as_sentence = response[0].upper() + response[1:]
            if not response_as_sentence.endswith('.'):
                response_as_sentence += '.'

            response_as_sentence = re.sub(' \s+', ' ', response_as_sentence)

            doc = nlp(response_as_sentence)
            best_label = max(doc.cats, key=doc.cats.get)
            print(response_as_sentence, best_label)
            binary_label = 'No fragment' if best_label == 'no_fragment' else 'Fragment'

            # If we find a grammatical error, we do NOT label the sentence as a fragment
            if len(doc.ents) > 0 and binary_label == 'Fragment':
                binary_label = 'No fragment'

            writer.writerow([sentence, prompt, response, binary_label, best_label, fragment_label_map[best_label]])


if __name__ == '__main__':
    evaluate()
