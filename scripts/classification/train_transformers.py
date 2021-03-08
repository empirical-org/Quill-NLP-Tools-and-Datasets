import csv
import torch

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from transformers import AutoTokenizer, BertForSequenceClassification, Trainer, TrainingArguments

input_file = "scripts/data/surge_barriers_because.tsv"
TEST_SIZE = 0.1
MODEL = "bert-base-cased"
EPOCHS = 10
EVAL_STEPS = 50
TRAIN_BATCH_SIZE = 16


def read_input(filename):

    data = []
    with open(filename) as i:
        reader = csv.reader(i, delimiter="\t")
        for line in reader:
            if len(line) == 2:
                data.append(line)

    print(f"Read {len(data)} instances")
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


data = read_input(input_file)
texts, labels = zip(*data)
all_labels = list(set(labels))
label_indices = [all_labels.index(label) for label in labels]

print(f"Number of labels: {len(all_labels)}")


train_texts, test_texts, train_labels, test_labels = train_test_split(texts,
                                                                      label_indices,
                                                                      test_size=TEST_SIZE,
                                                                      random_state=42)
train_texts, dev_texts, train_labels, dev_labels = train_test_split(train_texts,
                                                                    train_labels,
                                                                    test_size=TEST_SIZE,
                                                                    random_state=42)

model = BertForSequenceClassification.from_pretrained(MODEL, num_labels = len(all_labels))
tokenizer = AutoTokenizer.from_pretrained(MODEL)


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
    save_steps=EVAL_STEPS
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
trainer.evaluate(test_dataset)

