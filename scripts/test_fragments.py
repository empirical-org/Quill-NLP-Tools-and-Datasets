import csv
import spacy
import click
from sklearn.metrics import classification_report

model_path = '/tmp/fragment-model/model-best/'
test_file = 'scripts/data/fragments.tsv'

FRAGMENT_LABEL = 'fragment'
NO_FRAGMENT_LABEL = 'no_fragment'


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

    nlp = spacy.load(model_path)

    predicted_labels = []
    gold_labels = []

    predicted_labels_fine = []
    gold_labels_fine = []

    correct = 0
    for (fragment, no_fragment, gold_label_fine) in data:
        fragment_doc = nlp(fragment)
        no_fragment_doc = nlp(no_fragment)

        gold_labels.append(FRAGMENT_LABEL)
        gold_labels_fine.append(gold_label_fine)

        # First the fragment
        print(fragment)
        print(fragment_doc.cats)
        if fragment_doc.cats[NO_FRAGMENT_LABEL] < threshold_for_correct:
            predicted_labels.append(FRAGMENT_LABEL)
            del fragment_doc.cats[NO_FRAGMENT_LABEL]
            best_label = max(fragment_doc.cats, key=fragment_doc.cats.get)
            predicted_labels_fine.append(best_label)
            correct += 1
            print('Correct')
        else:
            predicted_labels.append(NO_FRAGMENT_LABEL)
            predicted_labels_fine.append(NO_FRAGMENT_LABEL)
            print('Incorrect*******')

        # Then the correct sentence
        gold_labels.append(NO_FRAGMENT_LABEL)
        gold_labels_fine.append(NO_FRAGMENT_LABEL)

        print(no_fragment)
        print(no_fragment_doc.cats)
        if no_fragment_doc.cats[NO_FRAGMENT_LABEL] > threshold_for_correct:
            predicted_labels.append(NO_FRAGMENT_LABEL)
            predicted_labels_fine.append(NO_FRAGMENT_LABEL)
            correct += 1
            print('Correct')
        else:
            predicted_labels.append(FRAGMENT_LABEL)
            del no_fragment_doc.cats[NO_FRAGMENT_LABEL]
            best_label = max(no_fragment_doc.cats, key=no_fragment_doc.cats.get)
            predicted_labels_fine.append(best_label)

            print('Incorrect*******')

    total = len(data)*2

    acc = correct/total
    print('Accuracy:', acc)

    report = classification_report(gold_labels, predicted_labels)
    print(report)

    report = classification_report(gold_labels_fine, predicted_labels_fine)
    print(report)


if __name__ == '__main__':
    evaluate()