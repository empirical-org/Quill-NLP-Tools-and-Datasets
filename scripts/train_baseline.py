import ndjson
import click
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report


@click.command()
@click.option('--train', help="train file")
@click.option('--test', help="test file")
def train(train, test):
    text_clf = Pipeline([
        ('vect', CountVectorizer(ngram_range=(1,2), min_df=1, max_df=0.7)),
        ('tfidf', TfidfTransformer()),
        ('clf', LogisticRegression()),
    ])

    with open(train) as i:
        train_data = ndjson.load(i)

    with open(test) as i:
        test_data = ndjson.load(i)

    train_texts = [x["text"] for x in train_data]
    train_labels = [x["label"] for x in train_data]

    test_texts = [x["text"] for x in test_data]
    test_labels = [x["label"] for x in test_data]

    text_clf.fit(train_texts, train_labels)

    predicted = text_clf.predict(test_texts)
    print(classification_report(test_labels, predicted))


if __name__ == '__main__':
    train()
