# Splits up tsv data files in a training and test portion and saves them
# to an ndjson output file.

import os

from sklearn.model_selection import train_test_split
import ndjson
import click


PROMPT = "Large amounts of meat consumption are harming the environment, because "


@click.command()
@click.argument('input_file')
def prepare_data(input_file):
    """
    Splits labelled data into train, dev and test files. If a dev and test
    file already exist, adds the additional data to the training file.

    Args:
        input_file: the file with the labelled data
    """

    target_path = "data/interim"

    texts, labels = [], []
    with open(input_file) as i:
        for line in i:
            line = line.strip().split("\t")
            if len(line) == 2:
                text, label = line
                if label not in EXCLUDE_LABELS:
                    texts.append(PROMPT + text)
                    labels.append(label)

    filename_train = os.path.basename(input_file).replace(".tsv", "_train_withprompt.ndjson")
    filename_dev = os.path.basename(input_file).replace(".tsv", "_dev_withprompt.ndjson")
    filename_test = os.path.basename(input_file).replace(".tsv", "_test_withprompt.ndjson")

    if path is None:
        texts_train, texts_test, labels_train, labels_test = \
            train_test_split(texts, labels, test_size=0.3, random_state=30)

        texts_dev, texts_test, labels_dev, labels_test = \
            train_test_split(texts_test, labels_test, test_size=0.6, random_state=30)

        data_train = [{"text": text, "label": label} for text, label in zip(texts_train, labels_train)]
        data_dev = [{"text": text, "label": label} for text, label in zip(texts_dev, labels_dev)]
        data_test = [{"text": text, "label": label} for text, label in zip(texts_test, labels_test)]

        target_file_train = os.path.join(target_path, filename_train)
        target_file_dev = os.path.join(target_path, filename_dev)
        target_file_test = os.path.join(target_path, filename_test)

        with open(target_file_train, "w") as o:
            ndjson.dump(data_train, o)

        with open(target_file_dev, "w") as o:
            ndjson.dump(data_dev, o)

        with open(target_file_test, "w") as o:
            ndjson.dump(data_test, o)

    else:

        existing_train_file = os.path.join(path, filename_train)
        existing_dev_file = os.path.join(path, filename_dev)
        existing_test_file = os.path.join(path, filename_test)

        with open(existing_dev_file) as i:
            data_dev = ndjson.load(i)

        with open(existing_test_file) as i:
            data_test = ndjson.load(i)

        with open(existing_train_file) as i:
            data_train = ndjson.load(i)

        existing_data = set([i["text"] for i in data_train + data_dev + data_test])

        for text, label in zip(texts, labels):
            if text not in existing_data:
                item = {"text": text, "label": label}
                data_train.append(item)
                existing_data.update([text])

        target_file_train = os.path.basename(input_file).replace(".tsv", "_train_withprompt.ndjson")
        target_file_train = os.path.join(target_path, target_file_train)

        with open(target_file_train, "w") as o:
            ndjson.dump(data_train, o)



if __name__ == '__main__':
    prepare_data()
