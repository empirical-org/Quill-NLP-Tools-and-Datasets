import os
import sys

import ndjson
import click
import json
import random
import torch
import yaml

from transformers import BertForTokenClassification, BertTokenizer
from sklearn.metrics import classification_report, precision_recall_fscore_support
from sklearn.preprocessing import MultiLabelBinarizer

from quillgrammar.grammar.constants import GrammarError
from quillnlp.models.bert.train import train, evaluate
from quillnlp.models.bert.preprocessing import get_data_loader, convert_data_to_input_items, NLPTask

from tests.error_files import files

@click.command()
@click.argument('output_file')
def train_grammar_model(output_file):

    file_list = ["data/training/Passive_without_be.ndjson",
                 "data/training/Passive_perfect_without_have.ndjson",
                 "data/training/Perfect_progressive_with_incorrect_be_and_without_have.ndjson",
                 "data/training/Perfect_progressive_without_have.ndjson",
                 "data/training/Perfect_without_have.ndjson",
                 "data/training/Simple_past_instead_of_past_perfect.ndjson",
                 "data/training/Its_vs_it_s.ndjson",
                 "data/training/Plural_vs_possessive.ndjson"]

    TRAINING_FILES = ["data/training/Its_vs_it_s.ndjson",
                      "data/training/Plural_vs_possessive.ndjson"]

    TEST_ERRORS = [GrammarError.ITS_IT_S.value,
                   GrammarError.PLURAL_VERSUS_POSSESSIVE_NOUNS.value]

    MAX_SEQ_LENGTH = 100
    TRAIN_SIZE = 500000
    TEST_SIZE = 1000
    EVAL_FREQUENCY = 100
    BATCH_SIZE = 32
    BASE_MODEL = "bert-base-cased"
    MODEL_DIRECTORY = "/tmp/grammar"

    data = []
    for f in TRAINING_FILES:
        print(f)
        with open(f) as i:
            lines = ndjson.load(i)

        random.shuffle(lines)

        data.extend(lines[:int(TRAIN_SIZE / len(TRAINING_FILES))])

    print("Data size:", len(data))

    all_data = []
    for item in data:
        all_data.append({"text": item[0], "entities": item[1].get("entities", [])})
        if "original" in item[1]:
            all_data.append({"text": item[1]["original"], "entities": []})

    print("All data size:", len(all_data))

    label2idx = {"O": 0}
    for sentence in all_data:
        if "entities" in sentence:
            for (_, _, label) in sentence["entities"]:
                if label not in label2idx:
                    label2idx[label] = len(label2idx)

    print(label2idx)

    tokenizer = BertTokenizer.from_pretrained(BASE_MODEL)
    input_items = convert_data_to_input_items(all_data, label2idx, MAX_SEQ_LENGTH, tokenizer, NLPTask.SEQUENCE_LABELING)

    random.shuffle(input_items)

    test_items = input_items[-TEST_SIZE:]
    valid_items = input_items[-2 * TEST_SIZE:-TEST_SIZE]
    train_items = input_items[:-2 * TEST_SIZE]

    test_dl = get_data_loader(test_items, BATCH_SIZE, task=NLPTask.SEQUENCE_LABELING, shuffle=False)
    dev_dl = get_data_loader(valid_items, BATCH_SIZE, task=NLPTask.SEQUENCE_LABELING, shuffle=False)
    train_dl = get_data_loader(train_items, BATCH_SIZE, task=NLPTask.SEQUENCE_LABELING, shuffle=True)

    sys.path.append('../')

    model = BertForTokenClassification.from_pretrained(BASE_MODEL, num_labels=len(label2idx))
    model.to("cuda")

    config = {"labels": label2idx, "base_model": BASE_MODEL, "max_seq_length": MAX_SEQ_LENGTH}
    with open(os.path.join(MODEL_DIRECTORY, "config.json"), "w") as o:
        json.dump(config, o)

    train(model, train_dl, dev_dl, BATCH_SIZE, 32 / BATCH_SIZE, device="cuda",
          num_train_epochs=10, patience=2, eval_frequency=EVAL_FREQUENCY, output_dir=MODEL_DIRECTORY)

    # In[8]:

    output_model_file = "/tmp/grammar/model.bin"
    print("Loading model from", output_model_file)
    device = "cpu"

    model_state_dict = torch.load(output_model_file, map_location=lambda storage, loc: storage)
    model = BertForTokenClassification.from_pretrained("bert-base-cased", state_dict=model_state_dict,
                                                       num_labels=len(label2idx))
    model.to(device)

    _, _, test_correct, test_predicted = evaluate(model, test_dl, device)

    idx2label = {v:k for k,v in label2idx.items()}

    predicted_labels = []
    correct_labels = []
    for item, correct, predicted in zip(test_items, test_correct, test_predicted):
        print(item.text)
        for error in set(predicted):
            print("Found:", idx2label[error])
        pred = [idx2label[error] for error in set(predicted) if idx2label[error] != "O"]
        pred = pred if pred else ["O"]
        predicted_labels.append(pred)

        for error in set(correct):
            print("Correct:", idx2label[error])

        cor = [idx2label[error] for error in set(correct) if idx2label[error] != "O"]
        cor = cor if cor else ["O"]
        correct_labels.append(cor)

    mlb = MultiLabelBinarizer()
    correct_labels_binary = mlb.fit_transform(correct_labels)
    predicted_labels_binary = mlb.transform(predicted_labels)

    print(classification_report(correct_labels_binary,
                                predicted_labels_binary, target_names=mlb.classes_))

    p, r, f1, s = precision_recall_fscore_support(correct_labels_binary, predicted_labels_binary, beta=0.5)
    rows = zip(mlb.classes_, p, r, f1, s)
    for row in rows:
        print(row)

    with open("tests/config.yaml") as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    test_data = []
    for f in files:
        if f["error"] in TEST_ERRORS:
            with open(f["positive"]) as i:
                for line in i:
                    test_data.append((line.strip(), "", f["error"]))
            with open(f["negative"]) as i:
                for line in i:
                    test_data.append((line.strip(), "", "Correct"))

    test_items = [{"text": item[0], "entities": []} for item in test_data]
    test_items = convert_data_to_input_items(test_items, label2idx, MAX_SEQ_LENGTH, tokenizer, NLPTask.SEQUENCE_LABELING)
    test2_dl = get_data_loader(test_items, BATCH_SIZE, task=NLPTask.SEQUENCE_LABELING, shuffle=False)

    _, _, _, test_predicted = evaluate(model, test2_dl, device)

    correct_labels = []
    predicted_labels = []

    for item, pred in zip(test_data, test_predicted):
        correct_label = item[2]
        predicted_label = set(pred)
        predicted_labels_to_add = []
        for l in predicted_label:
            if idx2label[l] == "O":
                predicted_labels_to_add.append("Correct")
            else:
                predicted_labels_to_add.append(idx2label[l])

        if len(predicted_labels_to_add) > 1 and "Correct" in predicted_labels_to_add:
            predicted_labels_to_add.remove("Correct")

        print(item[0])
        print("Correct:", correct_label)
        print("Predicted:", predicted_labels_to_add)

        correct_labels.append([correct_label])
        predicted_labels.append(predicted_labels_to_add)

    mlb = MultiLabelBinarizer()
    correct_labels_binary = mlb.fit_transform(correct_labels)
    predicted_labels_binary = mlb.transform(predicted_labels)

    print(classification_report(correct_labels_binary,
                                predicted_labels_binary, target_names=mlb.classes_))

    p, r, f1, s = precision_recall_fscore_support(correct_labels_binary, predicted_labels_binary, beta=0.5)
    rows = zip(mlb.classes_, p, r, f1, s)
    for row in rows:
        print(row)


if __name__ == "__main__":
    train_grammar_model()

