import os
import csv
import torch
import click
import time
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, pipeline

EPOCHS = 20
TRAIN_BATCH_SIZE = 16
EVAL_STEPS = 5


def read_input(filename):

    data = []
    with open(filename) as i:
        reader = csv.reader(i, delimiter=",")
        next(reader)

        for line in reader:
            if len(line) == 6:
                sentence, label, _, _, language, dataset = line
                data.append((sentence, label, language, dataset))
            elif len(line) == 3:
                dataset, sentence, label = line
                data.append((sentence, label, "original", dataset))
            else:
                print("Could not read line:", line)

    return data


def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='micro')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }


class QuillDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['label'] = self.labels[idx]
        return item

    def __len__(self):
        return len(self.labels)


@click.command()
@click.argument('input_file')
@click.argument('model_name')
@click.option('--synthetic', default=False, help='Use synthetic data?')
def run(input_file, model_name, synthetic):
    data = read_input(input_file)
    all_labels = list(set([d[1] for d in data]))
    label2idx = {l: i for i, l in enumerate(all_labels)}

    synthetic = False if synthetic == "False" else True

    print(f"Number of labels: {len(all_labels)}")
    print(f"Synthetic: {synthetic}")

    train_texts = [d[0] for d in data if d[3] == "TRAIN" and (d[2] == "original" or synthetic)]
    train_labels = [label2idx[d[1]] for d in data if d[3] == "TRAIN" and (d[2] == "original" or synthetic)]

    dev_texts = [d[0] for d in data if d[3] == "VALIDATION"]
    dev_labels = [label2idx[d[1]] for d in data if d[3] == "VALIDATION"]

    test_texts = [d[0] for d in data if d[3] == "TEST"]
    test_labels = [label2idx[d[1]] for d in data if d[3] == "TEST"]

    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels = len(all_labels))
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    train_texts_encoded = tokenizer(train_texts, padding=True, truncation=True, return_tensors="pt")
    dev_texts_encoded = tokenizer(dev_texts, padding=True, truncation=True, return_tensors="pt")
    test_texts_encoded = tokenizer(test_texts, padding=True, truncation=True, return_tensors="pt")

    train_dataset = QuillDataset(train_texts_encoded, train_labels)
    dev_dataset = QuillDataset(dev_texts_encoded, dev_labels)
    test_dataset = QuillDataset(test_texts_encoded, test_labels)

    print(f"Train items: {len(train_dataset)}")
    print(f"Dev items: {len(dev_dataset)}")
    print(f"Test items: {len(test_dataset)}")

    training_args = TrainingArguments(
        output_dir='./results',          # output directory
        num_train_epochs=EPOCHS,              # total # of training epochs
        per_device_train_batch_size=TRAIN_BATCH_SIZE,  # batch size per device during training
        per_device_eval_batch_size=64,   # batch size for evaluation
        warmup_steps=int(len(train_dataset)/TRAIN_BATCH_SIZE),  # number of warmup steps for learning rate scheduler
        weight_decay=0.01,               # strength of weight decay
        logging_dir='./logs',            # directory for storing logs
        evaluation_strategy="steps",
        eval_steps=EVAL_STEPS,
        save_steps=EVAL_STEPS,
        save_total_limit=10,
        load_best_model_at_end= True,
    )

    trainer = Trainer(
        model=model,                         # the instantiated 🤗 Transformers model to be trained
        args=training_args,                  # training arguments, defined above
        compute_metrics=compute_metrics,
        train_dataset=train_dataset,         # training dataset
        eval_dataset=dev_dataset,            # evaluation dataset
    )

    trainer.train()

    print("\n\n### Evaluation on test data ###")
    output = trainer.predict(test_dataset)

    predicted_labels = [all_labels[np.argmax(pl)] for pl in output.predictions]
    correct_labels = [all_labels[cl] for cl in output.label_ids]

    print("Accuracy:", output.metrics["eval_accuracy"])
    print(classification_report(correct_labels, predicted_labels))

    # Measure time needed for classification
    all_subdirs = [os.path.join('results/', d) for d in os.listdir('results/')
                   if os.path.isdir(os.path.join('results/', d))]
    latest_subdir = max(all_subdirs, key=os.path.getmtime)
    print("Latest:", latest_subdir)
    model = AutoModelForSequenceClassification.from_pretrained(latest_subdir)
    nlp = pipeline("sentiment-analysis", tokenizer=tokenizer, model=model)
    start = time.time()
    for text in test_texts:
        nlp(text)
    end = time.time()
    total_time = end-start

    print("Total time:", total_time, "seconds")
    print("Time per instance:", total_time/len(predicted_labels), "seconds")


if __name__ == '__main__':
    run()
