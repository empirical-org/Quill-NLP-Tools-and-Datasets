import os
import csv
import torch
import numpy as np
import ndjson
import time

from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
from transformers import AutoTokenizer, Trainer, TrainingArguments, AutoModelForSequenceClassification, pipeline

input_file = "scripts/data/shared_oceans_so.tsv"
#input_file = "data/interim/junkfood_but_withprompt.ndjson"
TEST_SIZE = 0.1
MODEL = "bert-base-uncased"
EPOCHS = 10
EVAL_STEPS = 10
TRAIN_BATCH_SIZE = 16
RANDOM_STATE = 10

print(input_file)

def read_input(filename):

    data = []
    with open(filename) as i:
        reader = csv.reader(i, delimiter="\t")
        for line in reader:
            if len(line) == 2:
                data.append(line)

    print(f"Read {len(data)} instances")
    return data


def read_input_ndjson(filename):
    data = []
    with open(filename) as i:
        for line in ndjson.load(i):
            data.append((line["text"], line["label"]))

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
        item['label'] = int(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


def evaluate_output(all_correct, all_predicted):
    correct = 0
    at_least_one = 0
    fp, fn, tp, tn = 0, 0, 0, 0
    for c, p in zip(all_correct, all_predicted):
        if sum(c == p) == len(c):
            correct +=1

        for ci, pi in zip(c, p):
            if pi == 1 and ci == 1:
                at_least_one += 1
                break

        for ci, pi in zip(c, p):
            if pi == 1 and ci == 1:
                tp += 1
                same = 1
            elif pi == 1 and ci == 0:
                fp += 1
            elif pi == 0 and ci == 1:
                fn += 1
            else:
                tn += 1
                same =1

    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    print("Data size:", len(all_predicted))
    print("P:", tp, "/", tp+fp, "=", precision)
    print("R:", tp, "/", tp+fn, "=", recall)
    print("F:", 2*precision*recall/(precision+recall))
    print("A:", correct/len(all_correct))
    print("AL1:", at_least_one/len(all_correct))


if input_file.endswith(".tsv"):
    data = read_input(input_file)
else:
    data = read_input_ndjson(input_file)

texts, labels = zip(*data)
all_labels = list(set(labels))
label_indices = [all_labels.index(label) for label in labels]

texts = np.array(texts)
label_indices = np.array(label_indices)

print(f"Number of labels: {len(all_labels)}")

tokenizer = AutoTokenizer.from_pretrained(MODEL)

kf = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
accuracies = []
predicted_labels = []
correct_labels = []
total_time = 0
for train_idx, test_idx in kf.split(texts):

    train_and_dev_texts = list(texts[train_idx])
    train_and_dev_labels = label_indices[train_idx]
    test_texts = list(texts[test_idx])
    test_labels = label_indices[test_idx]

    train_texts, dev_texts, train_labels, dev_labels = train_test_split(train_and_dev_texts,
                                                                          train_and_dev_labels,
                                                                          test_size=int(len(train_and_dev_texts)/5),
                                                                          random_state=RANDOM_STATE)

    train_texts_encoded = tokenizer(train_texts, padding=True, truncation=True, return_tensors="pt")
    dev_texts_encoded = tokenizer(dev_texts, padding=True, truncation=True, return_tensors="pt")
    test_texts_encoded = tokenizer(test_texts, padding=True, truncation=True, return_tensors="pt")

    train_dataset = QuillDataset(train_texts_encoded, train_labels)
    dev_dataset = QuillDataset(dev_texts_encoded, dev_labels)
    test_dataset = QuillDataset(test_texts_encoded, test_labels)

    model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=len(all_labels))

    training_args = TrainingArguments(
        output_dir='./results',  # output directory
        num_train_epochs=EPOCHS,  # total # of training epochs
        per_device_train_batch_size=TRAIN_BATCH_SIZE,  # batch size per device during training
        per_device_eval_batch_size=64,  # batch size for evaluation
        warmup_steps=int(len(train_dataset) / TRAIN_BATCH_SIZE),  # number of warmup steps for learning rate scheduler
        weight_decay=0.01,  # strength of weight decay
        logging_dir='./logs',  # directory for storing logs
        evaluation_strategy="steps",
        eval_steps=EVAL_STEPS,
        save_steps=EVAL_STEPS,
        save_total_limit=10,
        load_best_model_at_end=True,
    )

    trainer = Trainer(
        model=model,                         # the instantiated 🤗 Transformers model to be trained
        args=training_args,                  # training arguments, defined above
        compute_metrics=compute_metrics,
        train_dataset=train_dataset,         # training dataset
        eval_dataset=dev_dataset,            # evaluation dataset
    )

    trainer.train()

    output = trainer.predict(test_dataset)

    accuracies.append(output.metrics["eval_accuracy"])
    for pl, cl in zip(output.predictions, output.label_ids):
        predicted_labels.append(all_labels[np.argmax(pl)])
        correct_labels.append(all_labels[cl])

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
    total_time += end-start

print(accuracies)
print("Overall accuracy:", sum(accuracies)/len(accuracies))
print(classification_report(correct_labels, predicted_labels))
print("Total time:", total_time, "seconds")
print("Time per instance:", total_time/len(predicted_labels), "seconds")
