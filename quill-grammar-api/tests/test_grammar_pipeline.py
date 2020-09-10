import csv
import click

from tqdm import tqdm
from sklearn.metrics import classification_report, precision_recall_fscore_support
from sklearn.preprocessing import MultiLabelBinarizer

from grammar.pipeline import GrammarPipeline


@click.command()
@click.option('--input_file', default="tests/data/grammar_errors.csv", help='The input CSV file.')
@click.option('--output_file', prompt='The output file', help='The output CSV file.')
def test_grammar_pipeline(input_file, output_file):
    pipeline = GrammarPipeline()

    predicted_labels = []
    correct_labels = []

    data = []
    with open(input_file) as i:
        reader = csv.reader(i)
        for row in reader:
            if len(row) == 2:
                sentence, error = row
                data.append((sentence, "", error))
            elif len(row) == 3:
                data.append(row)

    import random
    random.shuffle(data)

    from grammar.constants import GrammarError
    error_map = {GrammarError.INCORRECT_PAST_TENSE_AS_PARTICIPLE_IN_PASSIVE.value:
                 GrammarError.PASSIVE_WITH_SIMPLE_PAST_INSTEAD_OF_PARTICIPLE.value,
                 "Past tense instead of participle": "Past instead of participle"}

    with open(output_file, "w") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["Sentence", "Errors", "Predictions"])
        for (sentence, prompt, error) in tqdm(data, desc="Predicting errors"):

            errors = pipeline.check(sentence, prompt)
            # print(errors)
            # errors = list(set([error_map.get(e.type, e.type) for e in errors]))
            errors.sort(reverse=True)
            if len(errors) > 0:
                predicted_error = error_map.get(errors[0].type, errors[0].type)
                highlighted_word = errors[0].text
                index = errors[0].index
                model = errors[0].model
            else:
                predicted_error = ""
                highlighted_word = ""
                index = ""
                model = ""
            # print(predicted_error)

            writer.writerow([sentence, error, predicted_error, highlighted_word, index, model])

            predicted_labels.append([predicted_error])
            correct_labels.append([error])

    mlb = MultiLabelBinarizer()
    correct_labels_binary = mlb.fit_transform(correct_labels)
    predicted_labels_binary = mlb.transform(predicted_labels)

    print(classification_report(correct_labels_binary,
                                predicted_labels_binary, target_names=mlb.classes_))

    p, r, f1, s = precision_recall_fscore_support(correct_labels_binary, predicted_labels_binary, beta=0.5)
    rows = zip(mlb.classes_, p, r, f1, s)

    with open("report_" + output_file, "w") as evaluation_file:
        writer = csv.writer(evaluation_file)
        writer.writerow(["Error type", "Precision", "Recall", "F0.5-score", "Support"])
        for row in rows:
            writer.writerow(row)


if __name__ == '__main__':
    test_grammar_pipeline()
