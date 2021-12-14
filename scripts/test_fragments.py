import csv
import spacy
import click
from sklearn.metrics import classification_report, confusion_matrix
from scripts.quillgrammar.count_clauses import get_clauses2

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


grammar_model_path = '/home/yves/projects/grammar-api/quillgrammar/models/current/'
grammar_model = spacy.load(grammar_model_path)


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
            elif len(line) == 2:
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

    predicted_labels_no_grammar_errors = []
    gold_labels_no_grammar_errors = []

    correct = 0

    if len(data[0]) == 3:
        total = len(data)*2
        with open('fragment_results.txt', 'w') as o:
            writer = csv.writer(o, delimiter='\t')
            for (fragment, no_fragment, gold_label_fine) in data:

                if gold_label_fine not in known_fragments:
                    continue

                fragment_doc = nlp(fragment)
                no_fragment_doc = nlp(no_fragment)

                clauses_fragment = get_clauses2(fragment)
                clauses_no_fragment = get_clauses2(no_fragment)

                runon_fragment = 'Runon:yes' if len([c for c in clauses_fragment if c['clause_type'] == 'run-on']) > 0 else 'Runon:no'
                runon_nofragment = 'Runon:yes' if len([c for c in clauses_no_fragment if c['clause_type'] == 'run-on']) > 0 else 'Runon:no'

                gold_labels.append(FRAGMENT_LABEL)
                gold_labels_fine.append(gold_label_fine)

                # First the fragment
                if fragment_doc.cats[NO_FRAGMENT_LABEL] < threshold_for_correct:
                    predicted_labels.append(FRAGMENT_LABEL)
                    del fragment_doc.cats[NO_FRAGMENT_LABEL]
                    best_label = max(fragment_doc.cats, key=fragment_doc.cats.get)
                    predicted_labels_fine.append(best_label)
                    correct += 1
                    writer.writerow([fragment, gold_label_fine, best_label, runon_fragment])
                else:
                    predicted_labels.append(NO_FRAGMENT_LABEL)
                    predicted_labels_fine.append(NO_FRAGMENT_LABEL)
                    writer.writerow([fragment, gold_label_fine, NO_FRAGMENT_LABEL, runon_fragment])

                # Then the correct sentence
                gold_labels.append(NO_FRAGMENT_LABEL)
                gold_labels_fine.append(NO_FRAGMENT_LABEL)

                if no_fragment_doc.cats[NO_FRAGMENT_LABEL] > threshold_for_correct:
                    predicted_labels.append(NO_FRAGMENT_LABEL)
                    predicted_labels_fine.append(NO_FRAGMENT_LABEL)
                    correct += 1
                    writer.writerow([no_fragment, NO_FRAGMENT_LABEL, NO_FRAGMENT_LABEL, runon_nofragment])
                else:
                    predicted_labels.append(FRAGMENT_LABEL)
                    del no_fragment_doc.cats[NO_FRAGMENT_LABEL]
                    best_label = max(no_fragment_doc.cats, key=no_fragment_doc.cats.get)
                    predicted_labels_fine.append(best_label)
                    writer.writerow([no_fragment, NO_FRAGMENT_LABEL, best_label, runon_nofragment])
    else:
        total = len(data)
        for (original_item, label) in data:

            item = original_item[0].upper() + original_item[1:]
            print(item)
            grammar_errors = grammar_model(item).ents

            if not item.endswith('.'):
                item = item + '.'


            doc = nlp(item)
            prediction = 'Fragment' if doc.cats['fragment'] >= threshold_for_correct else 'No fragment'

            gold_labels.append(label)
            predicted_labels.append(prediction)

            if not grammar_errors:
                predicted_labels_no_grammar_errors.append(prediction)
                gold_labels_no_grammar_errors.append(label)
    
            # if label != prediction:
            print(item, label, prediction, grammar_errors)

    acc = correct/total
    print('Accuracy:', acc)

    report = classification_report(gold_labels, predicted_labels)
    print(report)

    if predicted_labels_no_grammar_errors:
        report = classification_report(gold_labels_no_grammar_errors, predicted_labels_no_grammar_errors)
        print(report)

    if predicted_labels_fine:
        report = classification_report(gold_labels_fine, predicted_labels_fine)
        print(report)

        label_list = sorted(list(set(gold_labels_fine)))
        confmatrix = confusion_matrix(gold_labels_fine, predicted_labels_fine, labels=label_list)

        print(",".join([""]+label_list))
        for label, predictions in zip(label_list,confmatrix):
            print(",".join([label]+[str(v) for v in predictions]))

if __name__ == '__main__':
    evaluate()
