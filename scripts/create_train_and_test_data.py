# Splits up tsv data files in a training and test portion and saves them
# to an ndjson output file.

import os

from sklearn.model_selection import train_test_split
import ndjson
import click

@click.command()
@click.option('--input_file', help='input file')
def prepare_data(input_file):
    texts, labels = [], []
    with open(input_file) as i:
        for line in i:
            line = line.strip().split("\t")
            if len(line) == 2:
                text, label = line
                texts.append(text)
                labels.append(label)

    texts_train, texts_test, labels_train, labels_test = \
        train_test_split(texts, labels, test_size=0.3, random_state=30)

    texts_train, texts_dev, labels_train, labels_dev = \
        train_test_split(texts_train, labels_train, test_size=0.2, random_state=30)

    data_train = [{"text": text, "label": label} for text, label in zip(texts_train, labels_train)]
    data_dev = [{"text": text, "label": label} for text, label in zip(texts_dev, labels_dev)] 
    data_test = [{"text": text, "label": label} for text, label in zip(texts_test, labels_test)]

    target_path = "data/interim"
    target_file_train = os.path.basename(input_file).replace(".tsv", "_train.ndjson")
    target_file_dev = os.path.basename(input_file).replace(".tsv", "_dev.ndjson")
    target_file_test = os.path.basename(input_file).replace(".tsv", "_test.ndjson")

    target_file_train = os.path.join(target_path, target_file_train)
    target_file_dev = os.path.join(target_path, target_file_dev)
    target_file_test = os.path.join(target_path, target_file_test)

    with open(target_file_train, "w") as o:
        ndjson.dump(data_train, o)

    with open(target_file_dev, "w") as o:
        ndjson.dump(data_dev, o)

    with open(target_file_test, "w") as o:
        ndjson.dump(data_test, o)


if __name__ == '__main__':
    prepare_data()
