# Splits up tsv data files in a training and test portion and saves them
# to an ndjson output file.

from sklearn.model_selection import train_test_split
import ndjson
import os

files = ["data/raw/junkfood_because.tsv", "data/raw/junkfood_but.tsv"]
prompt = "Schools should not allow junk food to be sold on campus "

for f in files:

    texts, labels = [], []
    with open(f) as i:
        for line in i:
            line = line.strip().split("\t")
            if len(line) == 2:
                text, label = line
                texts.append(prompt + text)
                labels.append(label)

    texts_train, texts_test, labels_train, labels_test = \
        train_test_split(texts, labels, test_size=0.3, random_state=30)

    texts_train, texts_dev, labels_train, labels_dev = \
        train_test_split(texts_train, labels_train, test_size=0.2, random_state=30)

    data_train = [{"text": text, "label": label} for text, label in zip(texts_train, labels_train)]
    data_dev = [{"text": text, "label": label} for text, label in zip(texts_dev, labels_dev)] 
    data_test = [{"text": text, "label": label} for text, label in zip(texts_test, labels_test)]

    target_path = "data/interim"
    target_file_train = os.path.basename(f).replace(".tsv", "_train_withprompt.ndjson")
    target_file_dev = os.path.basename(f).replace(".tsv", "_dev_withprompt.ndjson")
    target_file_test = os.path.basename(f).replace(".tsv", "_test_withprompt.ndjson")

    target_file_train = os.path.join(target_path, target_file_train)
    target_file_dev = os.path.join(target_path, target_file_dev)
    target_file_test = os.path.join(target_path, target_file_test)

    with open(target_file_train, "w") as o:
        ndjson.dump(data_train, o)

    with open(target_file_dev, "w") as o:
        ndjson.dump(data_dev, o)

    with open(target_file_test, "w") as o:
        ndjson.dump(data_test, o)
