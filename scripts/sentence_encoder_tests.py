import os
import re

import tensorflow as tf
import tensorflow_hub as hub
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import click
import ndjson
import seaborn as sns
from tensorflow.contrib import predictor
from sklearn.metrics import classification_report

PROMPT = ""
BATCH_SIZE = 32
MODULE = "https://tfhub.dev/google/universal-sentence-encoder/2"
#    https://tfhub.dev/google/universal-sentence-encoder-large/3
#    "https://tfhub.dev/google/elmo/2"

# Merge positive and negative examples, add a polarity column and shuffle.


def get_label_vocab(train_data_path):
    with open(train_data_path) as i:
        d = ndjson.load(i)

    labels = list(set([i["label"] for i in d]))
    label_vocab = {label:i for i,label in enumerate(labels)}
    return label_vocab


def load_dataset(f, label_vocab):
    with open(f) as i:
        d = ndjson.load(i)

    table = [(PROMPT + " " + i["text"], label_vocab[i["label"]]) for i in d]
    df = pd.DataFrame(table)
    df.columns = ["sentence", "label"]
    return df


def load_datasets(train_file, dev_file, test_file):
    label_vocab = get_label_vocab(train_file)

    train_df = load_dataset(train_file, label_vocab)
    dev_df = load_dataset(dev_file, label_vocab)
    test_df = load_dataset(test_file, label_vocab)

    return train_df, dev_df, test_df, label_vocab


@click.command()
@click.option('--train', help="train file")
@click.option('--dev', help="dev file")
@click.option('--test', help="test file")
@click.option('--out', help="output directory")
def train(train, dev, test, out):
    train_df, dev_df, test_df, label2idx = load_datasets(train, dev, test)
    idx2label = {i:l for l,i in label2idx.items()}

    print(train_df.head())

    # Training input on the whole training set with no limit on training epochs.
    train_input_fn = tf.estimator.inputs.pandas_input_fn(
        train_df, train_df["label"], num_epochs=None, batch_size=BATCH_SIZE, shuffle=True)

    num_labels = len(set(np.array(train_df["label"])))

    # Prediction on the whole training set.
    predict_train_input_fn = tf.estimator.inputs.pandas_input_fn(
        train_df, train_df["label"], shuffle=False, batch_size=BATCH_SIZE)

    # Prediction on the dev set.
    predict_dev_input_fn = tf.estimator.inputs.pandas_input_fn(
        dev_df, dev_df["label"], shuffle=False)

    # Prediction on the test set.
    predict_test_input_fn = tf.estimator.inputs.pandas_input_fn(
        test_df, test_df["label"], shuffle=False)

    embedded_text_feature_column = hub.text_embedding_column(
        key="sentence",
        module_spec=MODULE, trainable=True)

    config = tf.estimator.RunConfig(model_dir=out,
        save_checkpoints_steps=100) # This sets the default for saving, and also evaluation!

    estimator = tf.estimator.DNNClassifier(
        config=config,
        hidden_units=[500, 100],
        feature_columns=[embedded_text_feature_column],
        n_classes=num_labels,
        optimizer=tf.train.AdagradOptimizer(learning_rate=0.003))

    # max_steps_without_decrease sets the maximum TRAINING steps with no decrease in the metric.
    # So, if we evaluate every 200 steps, and set max_steps_without_decrease to 1000, training
    # will stop after 5 evaluations in a row gave no decrease.
    early_stopping = tf.contrib.estimator.stop_if_no_decrease_hook(
        estimator,
        metric_name='loss',
        max_steps_without_decrease=1000,
        min_steps=100)

    # TODO: needs to be integrated
    #def serving_input_receiver_fn():
    #    input = {"sentence": tf.placeholder(tf.string, shape=[None])}
    #    embedded_text_feature_column = hub.text_embedding_column(
    #        key="sentence",
    #        module_spec=MODULE, trainable=True)
    #    features = embedded_text_feature_column
    #    return tf.estimator.export.ServingInputReceiver(features, input)


    #exporter = tf.estimator.BestExporter(name="best_exporter",
    #    serving_input_receiver_fn=serving_input_receiver_fn,
    #    exports_to_keep=1)

    train_spec = tf.estimator.TrainSpec(input_fn=train_input_fn, max_steps=10000, hooks=[early_stopping])
    eval_spec = tf.estimator.EvalSpec(input_fn=predict_dev_input_fn, steps=100, start_delay_secs=0, throttle_secs=2)

    tf.estimator.train_and_evaluate(estimator, train_spec, eval_spec)

    #estimator.train(input_fn=train_input_fn, steps=800) #, hooks=[early_stopping])

    train_eval_result = estimator.evaluate(input_fn=predict_train_input_fn)
    test_eval_result = estimator.evaluate(input_fn=predict_test_input_fn)

    correct_labels = []
    predicted_labels = []
    results = estimator.predict(predict_test_input_fn)
    for sentence, correct_label_id, result in zip(np.array(test_df["sentence"]), np.array(test_df["label"]), results):
        class_id = result["class_ids"][0]
        predicted_label = idx2label[class_id]
        correct_label = idx2label[correct_label_id]
        correct_labels.append(correct_label)
        predicted_labels.append(predicted_label)

        print("\t".join([sentence, correct_label, predicted_label]))

    print("Step:", estimator.get_variable_value("global_step"))
    print("Training set accuracy: {accuracy}".format(**train_eval_result))
    print("Test set accuracy: {accuracy}".format(**test_eval_result))

    print(classification_report(correct_labels, predicted_labels))


if __name__ == "__main__": 
    train()

