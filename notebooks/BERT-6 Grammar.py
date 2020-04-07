#!/usr/bin/env python
# coding: utf-8

# In[1]:


import ndjson
import random

TRAINING_FILES = ["/home/yves/projects/Quill-NLP-Tools-and-Datasets/notw.ndjson"]
#                  "/home/yves/projects/Quill-NLP-Tools-and-Datasets/subtitles.ndjson",
#                  "/home/yves/projects/Quill-NLP-Tools-and-Datasets/wiki_errors.ndjson"]
MAX_SEQ_LENGTH = 100
TRAIN_SIZE = 2000000
TEST_SIZE = 10000
BATCH_SIZE = 32


data = []
for f in TRAINING_FILES:
    print(f)
    with open(f) as i:
        lines = ndjson.load(i)

    random.shuffle(lines)

    data.extend(lines[:int(TRAIN_SIZE/len(TRAINING_FILES))])


data = [{"text": item.get("synth_sentence", item.get("orig_sentence")), 
         "entities": item.get("entities", [])} for item in data]


# In[2]:


label2idx = {"O": 0}

for sentence in data:
    if "entities" in sentence:
        for (_, _, label) in sentence["entities"]:
            if label not in label2idx:
                label2idx[label] = len(label2idx)
            
print(label2idx)
        


# In[3]:


from typing import List

class BertInputItem(object):
    """ A BertInputItem contains all the information that is needed to finetune
    a Bert model.

    Attributes:
        input_ids: the ids of the input tokens
        input_mask: a list of booleans that indicates what tokens should be masked
        segment_ids: a list of segment ids for the tokens
        label_id: a label id or a list of label ids for the input
    """

    def __init__(self, text: str,
                 input_ids: List[int],
                 input_mask: List[int],
                 segment_ids: List[int],
                 label_ids: List[int]):
        self.text = text
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.segment_ids = segment_ids
        self.label_ids = label_ids
        

def preprocess_sequence_labelling(examples, label2idx, max_seq_length, tokenizer):
    input_items = []
    for (ex_index, ex) in enumerate(examples):

        # Create a list of token ids
        toks = tokenizer.encode_plus(ex["text"], max_length=max_seq_length, pad_to_max_length=True)
        input_ids = toks["input_ids"]
        segment_ids = toks["token_type_ids"]
        input_mask = toks["attention_mask"]
        
        tokens = tokenizer.convert_ids_to_tokens(input_ids)
        
        if "entities" not in ex:
            labels = [label2idx["O"]] * len(input_ids)
        else:
            labels = [label2idx["O"]]
            cur_index = 0
            for num, tok in enumerate(tokens[1:]):

                if num > 0 and not tok.startswith("##"):
                    cur_index += 1

                found_entity = False
                for entity in ex["entities"]:
                    if cur_index >= entity[0] and cur_index <= entity[1]:
                        labels.append(label2idx[entity[2]])
                        found_entity = True
                if not found_entity:
                    labels.append(label2idx["O"])


                if tok.startswith("##"):
                    cur_index += len(tok)-2
                else:
                    cur_index += len(tok)
        
        assert len(labels) == len(input_ids)
        
        input_items.append(
            BertInputItem(text=ex["text"],
                          input_ids=input_ids,
                          input_mask=input_mask,
                          segment_ids=segment_ids,
                          label_ids=labels))
    return input_items


# In[4]:


from transformers import BertForTokenClassification
from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained("bert-base-cased")
input_items = preprocess_sequence_labelling(data, label2idx, MAX_SEQ_LENGTH, tokenizer)


# In[5]:


import torch
import numpy as np
from torch.utils.data import TensorDataset, DataLoader

def get_data_loader(input_items: List[BertInputItem], batch_size: int, shuffle: bool=True) -> DataLoader:
    """
    Constructs a DataLoader for a list of BERT input items.

    Args:
        input_items: a list of BERT input items
        batch_size: the batch size
        shuffle: indicates whether the data should be shuffled or not.

    Returns: a DataLoader for the input items

    """
    all_input_ids = torch.tensor([f.input_ids for f in input_items], dtype=torch.long)
    all_input_mask = torch.tensor([f.input_mask for f in input_items], dtype=torch.long)
    all_segment_ids = torch.tensor([f.segment_ids for f in input_items], dtype=torch.long)
    all_label_ids = torch.tensor([f.label_ids for f in input_items], dtype=torch.long)
    
    data = TensorDataset(all_input_ids, all_input_mask, all_segment_ids, all_label_ids)

    dataloader = DataLoader(data, shuffle=shuffle, batch_size=batch_size)

    return dataloader


# In[6]:


import random

random.shuffle(input_items)

test_items = input_items[-TEST_SIZE:]
valid_items = input_items[-2*TEST_SIZE:-TEST_SIZE]
train_items = input_items[:-2*TEST_SIZE]

test_dl = get_data_loader(test_items, BATCH_SIZE, shuffle=False)
dev_dl = get_data_loader(valid_items, BATCH_SIZE, shuffle=False)
train_dl = get_data_loader(train_items, BATCH_SIZE, shuffle=True)


# In[7]:


import sys
sys.path.append('../')

from quillnlp.models.bert.train import train
from transformers import BertModel

model = BertForTokenClassification.from_pretrained("bert-base-cased", num_labels=len(label2idx))
model.to("cuda")

train(model, train_dl, dev_dl, BATCH_SIZE, 32/BATCH_SIZE, device="cuda", num_train_epochs=10, patience=2)


# In[8]:


from quillnlp.models.bert.train import evaluate

output_model_file = "/tmp/model.bin"
print("Loading model from", output_model_file)
device="cpu"

model_state_dict = torch.load(output_model_file, map_location=lambda storage, loc: storage)
model = BertForTokenClassification.from_pretrained("bert-base-cased", state_dict=model_state_dict, num_labels=len(label2idx))
model.to(device)

#_, train_correct, train_predicted = evaluate(model, train_dataloader)
#_, dev_correct, dev_predicted = evaluate(model, dev_dataloader)
_, _, test_correct, test_predicted = evaluate(model, test_dl, device)


# In[9]:


idx2label = {v:k for k,v in label2idx.items()}

for item, correct, predicted in zip(test_items, test_correct, test_predicted):
    print(item.text)
    for error in set(predicted):
        print("Found:", idx2label[error])
    for error in set(correct):
        print("Correct:", idx2label[error])
    


# In[10]:


# Read error input

error_map = {'POSSESSIVE': 'Plural versus possessive nouns', 
             'VERB': 'Subject-verb agreement', 
             'ADV': 'Adverbs versus adjectives', 
             'ITS': "Its versus it's", 
             'THEN': 'Than versus then'}

data = []
with open("tests/data/grammar_valid.tsv") as i:
    for line in i:
        line = line.strip().split("\t")
        if len(line) == 3:
            data.append(line)

results = {}
for (error_type, correct_sentence, incorrect_sentence) in data:
    if error_type not in results:
        results[error_type] = {"cc": 0, "ci": 0, "ic": 0, "ii": 0}

    correct_features = preprocess_sequence_labelling([{"text": correct_sentence}], 
                                                     label2idx, MAX_SEQ_LENGTH, tokenizer)

    incorrect_features = preprocess_sequence_labelling([{"text": incorrect_sentence}],
                                                       label2idx, MAX_SEQ_LENGTH, tokenizer)

    correct_dl = get_data_loader(correct_features, 1, shuffle=False)
    incorrect_dl = get_data_loader(incorrect_features, 1, shuffle=False)
    
    _, _, _, correct_predicted = evaluate(model, correct_dl, device)
    _, _, _, incorrect_predicted = evaluate(model, incorrect_dl, device)
        
    errors = [idx2label[i] for i in set(correct_predicted[0])]
    errors = [error_map[e] for e in errors if e in error_map]
    print(correct_sentence)
    print(errors)

    if len(errors) == 0:
        results[error_type]["cc"] += 1
    else:
        results[error_type]["ci"] += 1

    errors = [idx2label[i] for i in set(incorrect_predicted[0])]
    errors = [error_map[e] for e in errors if e in error_map]
    print(incorrect_sentence)
    print(errors)

    if len(errors) == 0:
        results[error_type]["ic"] += 1
    else:
        results[error_type]["ii"] += 1


# In[11]:


results


# In[12]:


for error_type in results:
    correct = results[error_type]["cc"] + results[error_type]["ii"]
    incorrect = results[error_type]["ic"] + results[error_type]["ci"]

    precision = results[error_type]["cc"]/ (results[error_type]["cc"] + results[error_type]["ic"])
    recall = results[error_type]["cc"] / (results[error_type]["cc"] + results[error_type]["ci"])
    fscore = 2*precision*recall/(precision+recall)

    print(error_type, precision, recall, fscore)


# In[ ]:




