import csv
import spacy
import click
from sklearn.metrics import classification_report, confusion_matrix

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


@click.command()
@click.argument('model_path')
@click.argument('test_file')
@click.argument('threshold_for_correct', type=float)
def evaluate(model_path, test_file, threshold_for_correct):

    data = []
    with open(test_file) as i:
        reader = csv.reader(i, delimiter='\t')
        for line in reader:
            if len(line) == 3:
                data.append(line)

    nlp = spacy.load('/home/yves/projects/grammar-api/quillgrammar/models/current')
    fragment_pipeline = spacy.load(model_path)
    fragment_pipeline.get_pipe('textcat').model.get_ref('tok2vec').layers[0].upstream_name = 'fragment-transformer'
    nlp.add_pipe('transformer', source=fragment_pipeline, name='fragment-transformer')
    nlp.add_pipe('textcat', source=fragment_pipeline, last=True)

    predicted_labels = []
    gold_labels = []

    predicted_labels_fine = []
    gold_labels_fine = []

    correct = 0
    with open('fragment_results.txt', 'w') as o:
        for (fragment, no_fragment, gold_label_fine) in data:

            if gold_label_fine not in known_fragments:
                continue

            fragment_doc = nlp(fragment)
            no_fragment_doc = nlp(no_fragment)

            gold_labels.append(FRAGMENT_LABEL)
            gold_labels_fine.append(gold_label_fine)

            # First the fragment
            if fragment_doc.cats[NO_FRAGMENT_LABEL] < threshold_for_correct:
                predicted_labels.append(FRAGMENT_LABEL)
                del fragment_doc.cats[NO_FRAGMENT_LABEL]
                best_label = max(fragment_doc.cats, key=fragment_doc.cats.get)
                predicted_labels_fine.append(best_label)
                correct += 1
                o.write(fragment + '\t' + gold_label_fine + '\t' + best_label + '\n')
            else:
                predicted_labels.append(NO_FRAGMENT_LABEL)
                predicted_labels_fine.append(NO_FRAGMENT_LABEL)
                o.write(fragment + '\t' + gold_label_fine + '\t' + NO_FRAGMENT_LABEL + '\n')

            # Then the correct sentence
            gold_labels.append(NO_FRAGMENT_LABEL)
            gold_labels_fine.append(NO_FRAGMENT_LABEL)

            if no_fragment_doc.cats[NO_FRAGMENT_LABEL] > threshold_for_correct:
                predicted_labels.append(NO_FRAGMENT_LABEL)
                predicted_labels_fine.append(NO_FRAGMENT_LABEL)
                correct += 1
                o.write(no_fragment + '\t' + NO_FRAGMENT_LABEL + '\t' + NO_FRAGMENT_LABEL + '\n')
            else:
                predicted_labels.append(FRAGMENT_LABEL)
                del no_fragment_doc.cats[NO_FRAGMENT_LABEL]
                best_label = max(no_fragment_doc.cats, key=no_fragment_doc.cats.get)
                predicted_labels_fine.append(best_label)
                o.write(no_fragment + '\t' + NO_FRAGMENT_LABEL + '\t' + best_label + '\n')

    total = len(data)*2

    acc = correct/total
    print('Accuracy:', acc)

    report = classification_report(gold_labels, predicted_labels)
    print(report)

    report = classification_report(gold_labels_fine, predicted_labels_fine)
    print(report)

    label_list = sorted(list(set(gold_labels_fine)))
    confmatrix = confusion_matrix(gold_labels_fine, predicted_labels_fine, labels=label_list)

    print(",".join([""]+label_list))
    for label, predictions in zip(label_list,confmatrix):
        print(",".join([label]+[str(v) for v in predictions]))

if __name__ == '__main__':
    evaluate()
