import csv
import random
import ndjson
import numpy as np

from nltk.corpus import stopwords

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC, SVC
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split, KFold

input_file = "scripts/data/shared_oceans_because.tsv"
#input_file = "scripts/data/whaling_so.tsv"
input_file = "data/interim/voting_but_withprompt.ndjson"
print(input_file)

RANDOM_STATE = 1
stopwords = stopwords.words("english")


def read_input(filename):
    data = []
    with open(filename) as i:
        reader = csv.reader(i, delimiter="\t")
        for line in reader:
            data.append(line)

    return data


def read_input_ndjson(filename):
    data = []
    with open(filename) as i:
        for line in ndjson.load(i):
            if "label" in line:
                label = line["label"]
            else:
                if len(line["labels"]) > 1:
                    print("Multilabel")
                    print(line)
                label = line["labels"][0]

            data.append((line["text"], label))

    return data


if input_file.endswith(".tsv"):
    data = read_input(input_file)
else:
    data = read_input_ndjson(input_file)


def classify_with_clustering(data):

    texts, labels = zip(*data)

    texts = np.array(texts)
    labels = np.array(labels)

    preprocessing = Pipeline([
        ('vect', CountVectorizer(ngram_range=(1, 5), analyzer='char_wb',
                                 max_df=0.5)),
        ('tfidf', TfidfTransformer(use_idf=False))
    ])

    kf = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    accuracies = []

    for train_idx, test_idx in kf.split(texts):
        train_texts = texts[train_idx]
        train_labels = labels[train_idx]
        test_texts = texts[test_idx]
        test_labels = labels[test_idx]

        preprocessing.fit_transform(train_texts)
        train_preprocessed = preprocessing.transform(train_texts)
        test_preprocessed = preprocessing.transform(test_texts)

        classifier = LinearSVC()
        classifier.fit(train_preprocessed, train_labels)
        predictions = classifier.predict(test_preprocessed)

        accuracy = np.mean(predictions == test_labels)
        print(accuracy)
        accuracies.append(accuracy)

    return accuracies


accuracies = classify_with_clustering(data)

print(accuracies)
print("Mean accuracy:", np.mean(accuracies))

