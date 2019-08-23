"""
Trains a number of "traditional" (i.e. non-deep-learning-based) scikit-learn classifiers
for our topic classification experiments.
"""

import ndjson
import click
import glob
import numpy as np
import logging
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, precision_recall_fscore_support
from sklearn.model_selection import GridSearchCV


logging.getLogger().setLevel(logging.INFO)


def load_data(files):
    """
    Loads all data from a list of ndjson files.

    Args:
        files: a list of ndjson files

    Returns: the data in the files as a list of dicts
    """

    data = []
    for f in files:
        with open(f) as i:
            data += ndjson.load(i)

    texts = [x["text"] for x in data]
    labels = [x["label"] for x in data]

    return texts, labels


@click.command()
@click.argument('train')
@click.argument('dev')
@click.argument('test')
def train(train, dev, test):
    """
    Trains a classifier on the data in the training files and tests
    it on the data in the testfile.

    Args:
        train: path to the training files, possibly with wildcards
        test: test file path

    Returns:

    """

    preprocessing = Pipeline([
        ('vect', CountVectorizer(ngram_range=(1,2), min_df=1, max_df=0.7)),
        ('tfidf', TfidfTransformer())
    ])

    naive_bayes = MultinomialNB()
    #classifier = LinearSVC()
    classifier = LogisticRegression()

    train_files = glob.glob(train)
    logging.info(f"Found {len(train_files)} train_files.")

    train_texts, train_labels = load_data(train_files)
    dev_texts, dev_labels = load_data([dev])
    test_texts, test_labels = load_data([test])

    train_dev_preprocessed = preprocessing.fit_transform(train_texts + dev_texts)
    test_preprocessed = preprocessing.transform(test_texts)

    parameters = {'C': [0.1, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]}
    #parameters = {'C': [1]}

    logging.info("Performing grid search")
    best_classifier = GridSearchCV(classifier, parameters, cv=5, verbose=1)
    best_classifier.fit(train_dev_preprocessed, train_labels + dev_labels)

    logging.info("Best Parameters: " + str(best_classifier.best_params_))
    predicted = best_classifier.predict(test_preprocessed)

    logging.info("Report:\n" + classification_report(test_labels, predicted))

    naive_bayes.fit(train_dev_preprocessed, train_labels + dev_labels)
    predicted_nb = naive_bayes.predict(test_preprocessed)
    scores_nb = precision_recall_fscore_support(test_labels, predicted_nb, average="micro")
    logging.info("Naive Bayes P:{0:.3f} R:{1:.3f} F:{2:.3f}".format(*scores_nb))
    scores = precision_recall_fscore_support(test_labels, predicted, average="micro")
    logging.info("New P:{0:.3f} R:{1:.3f} F:{2:.3f}".format(*scores))


if __name__ == '__main__':
    train()
