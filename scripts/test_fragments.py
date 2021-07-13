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
            if len(line) == 2:
                data.append(line)


    nlp = spacy.load(model_path)

    predicted_labels = []
    gold_labels = []

    correct = 0
    for (fragment, no_fragment) in data:
        fragment_doc = nlp(fragment)
        no_fragment_doc = nlp(no_fragment)

        gold_labels.append(FRAGMENT_LABEL)

        print(fragment)
        print(fragment_doc.cats)
        if fragment_doc.cats[NO_FRAGMENT_LABEL] < threshold_for_correct:
            predicted_labels.append(FRAGMENT_LABEL)
            correct += 1
            print('Correct')
        else:
            predicted_labels.append(NO_FRAGMENT_LABEL)
            print('Incorrect*******')

        gold_labels.append(NO_FRAGMENT_LABEL)

        print(no_fragment)
        print(no_fragment_doc.cats)
        if no_fragment_doc.cats[NO_FRAGMENT_LABEL] > threshold_for_correct:
            predicted_labels.append(NO_FRAGMENT_LABEL)
            correct += 1
            print('Correct')
        else:
            predicted_labels.append(FRAGMENT_LABEL)
            print('Incorrect*******')

    total = len(data)*2

    acc = correct/total
    print('Accuracy:', acc)

    report = classification_report(gold_labels, predicted_labels)
    print(report)


if __name__ == '__main__':
    evaluate()