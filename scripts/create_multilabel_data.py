# Splits up tsv data files in a training and test portion and saves them
# to an ndjson output file.

import os
import re

from sklearn.model_selection import train_test_split
import ndjson
import click


PROMPT = "Governments should make voting compulsory but "


@click.command()
@click.argument('input_file')
@click.argument('output_file')
def prepare_data(input_file, output_file):
    """
    Splits labelled data into train, dev and test files. If a dev and test
    file already exist, adds the additional data to the training file.

    Args:
        input_file: the file with the labelled data
    """

    target_path = "data/interim"

    data = []
    with open(input_file) as i:
        for line in i:
            line = line.strip().split("\t")
            if len(line) == 2:
                text, label_string = line
                labels = [l.strip("( +") for l in label_string.split(")")]
                labels = [l for l in labels if len(l) > 1]
                labels = [l.replace("--optional", "") for l in labels]
                if len(labels) == 0:
                    labels = [label_string]
                data.append({"text": text, "label": labels})

    with open(output_file, "w") as o:
        ndjson.dump(data, o)


if __name__ == '__main__':
    prepare_data()
