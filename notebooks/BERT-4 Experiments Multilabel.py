#!/usr/bin/env python
# coding: utf-8

# # Multilabel BERT Experiments
# 
# In this notebook we do some first experiments with BERT: we finetune a BERT model+classifier on each of our datasets separately and compute the accuracy of the resulting classifier on the test data.

# For these experiments we use the `pytorch_transformers` package. It contains a variety of neural network architectures for transfer learning and pretrained models, including BERT and XLNET.
# 
# Two different BERT models are relevant for our experiments: 
# 
# - BERT-base-uncased: a relatively small BERT model that should already give reasonable results,
# - BERT-large-uncased: a larger model for real state-of-the-art results.

# In[1]:


from multilabel import EATINGMEAT_BECAUSE_MAP, EATINGMEAT_BUT_MAP, JUNKFOOD_BECAUSE_MAP, JUNKFOOD_BUT_MAP

label_map = EATINGMEAT_BECAUSE_MAP


# In[2]:


import torch

from pytorch_transformers.tokenization_bert import BertTokenizer
from pytorch_transformers.modeling_bert import BertForSequenceClassification

BERT_MODEL = 'bert-large-uncased'
BATCH_SIZE = 16 if "base" in BERT_MODEL else 2
GRADIENT_ACCUMULATION_STEPS = 1 if "base" in BERT_MODEL else 8

tokenizer = BertTokenizer.from_pretrained(BERT_MODEL)


# ## Data
# 
# We use the same data as for all our previous experiments. Here we load the training, development and test data for a particular prompt.

# In[3]:


import ndjson
import glob
from collections import Counter

prefix = "eatingmeat_because_xl"
train_file = f"../data/interim/{prefix}_train_withprompt.ndjson"
synth_files = glob.glob(f"../data/interim/{prefix}_train_withprompt_*.ndjson")
dev_file = f"../data/interim/{prefix}_dev_withprompt.ndjson"
test_file = f"../data/interim/{prefix}_test_withprompt.ndjson"

with open(train_file) as i:
    train_data = ndjson.load(i)

synth_data = []
for f in synth_files:
    if "allsynth" in f:
        continue
    with open(f) as i:
        synth_data += ndjson.load(i)
    
with open(dev_file) as i:
    dev_data = ndjson.load(i)
    
with open(test_file) as i:
    test_data = ndjson.load(i)
    
labels = Counter([item["label"] for item in train_data])
print(labels)


# Next, we build the label vocabulary, which maps every label in the training data to an index.

# In[4]:


label2idx = {}
idx2label = {}
target_names = []
for item in label_map:
    for label in label_map[item]:
        if label not in target_names:
            idx = len(target_names)
            target_names.append(label)
            label2idx[label] = idx
            idx2label[idx] = label
    
print(label2idx)
print(idx2label)


# In[5]:


def map_to_multilabel(items):
    return [{"text": item["text"], "label": label_map[item["label"]]} for item in items]

train_data = map_to_multilabel(train_data)
dev_data = map_to_multilabel(dev_data)
test_data = map_to_multilabel(test_data)


# In[6]:


import random

def sample(train_data, synth_data, label2idx, number):
    """Sample a fixed number of items from every label from
    the training data and test data.
    """
    new_train_data = []
    for label in label2idx:
        data_for_label = [i for i in train_data if i["label"] == label]
        
        # If there is more training data than the required number,
        # take a random sample of n examples from the training data.
        if len(data_for_label) >= number:
            random.shuffle(data_for_label)
            new_train_data += data_for_label[:number]
            
        # If there is less training data than the required number,
        # combine training data with synthetic data.
        elif len(data_for_label) < number:
            
            # Automatically add all training data
            new_train_data += data_for_label
            
            # Compute the required number of additional data
            rest = number-len(data_for_label)
            
            # Collect the synthetic data for the label
            synth_data_for_label = [i for i in synth_data if i["label"] == label]
            
            # If there is more synthetic data than required, 
            # take a random sample from the synthetic data.
            if len(synth_data_for_label) > rest:
                random.shuffle(synth_data_for_label)
                new_train_data += synth_data_for_label[:rest]
            # If there is less synthetic data than required,
            # sample with replacement from this data until we have
            # the required number.
            else:
                new_train_data += random.choices(synth_data_for_label, k=rest)
        
    return new_train_data


def random_sample(train_data, train_size):
    random.shuffle(train_data)
    train_data = train_data[:TRAIN_SIZE]    

#train_data = sample(train_data, synth_data, label2idx, 200)
print("Train data size:", len(train_data))


# ## Model
# 
# We load the pretrained model and put it on a GPU if one is available. We also put the model in "training" mode, so that we can correctly update its internal parameters on the basis of our data sets.

# In[7]:


from torch import nn
from pytorch_transformers.modeling_bert import BertPreTrainedModel, BertModel


class BertForMultiLabelSequenceClassification(BertPreTrainedModel):
    r"""
        **labels**: (`optional`) ``torch.LongTensor`` of shape ``(batch_size,)``:
            Labels for computing the sequence classification/regression loss.
            Indices should be in ``[0, ..., config.num_labels - 1]``.
            If ``config.num_labels == 1`` a regression loss is computed (Mean-Square loss),
            If ``config.num_labels > 1`` a classification loss is computed (Cross-Entropy).
    Outputs: `Tuple` comprising various elements depending on the configuration (config) and inputs:
        **loss**: (`optional`, returned when ``labels`` is provided) ``torch.FloatTensor`` of shape ``(1,)``:
            Classification (or regression if config.num_labels==1) loss.
        **logits**: ``torch.FloatTensor`` of shape ``(batch_size, config.num_labels)``
            Classification (or regression if config.num_labels==1) scores (before SoftMax).
        **hidden_states**: (`optional`, returned when ``config.output_hidden_states=True``)
            list of ``torch.FloatTensor`` (one for the output of each layer + the output of the embeddings)
            of shape ``(batch_size, sequence_length, hidden_size)``:
            Hidden-states of the model at the output of each layer plus the initial embedding outputs.
        **attentions**: (`optional`, returned when ``config.output_attentions=True``)
            list of ``torch.FloatTensor`` (one for each layer) of shape ``(batch_size, num_heads, sequence_length, sequence_length)``:
            Attentions weights after the attention softmax, used to compute the weighted average in the self-attention heads.
    Examples::
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        model = BertForSequenceClassification.from_pretrained('bert-base-uncased')
        input_ids = torch.tensor(tokenizer.encode("Hello, my dog is cute")).unsqueeze(0)  # Batch size 1
        labels = torch.tensor([1]).unsqueeze(0)  # Batch size 1
        outputs = model(input_ids, labels=labels)
        loss, logits = outputs[:2]
    """
    def __init__(self, config):
        super(BertForMultiLabelSequenceClassification, self).__init__(config)
        self.num_labels = config.num_labels

        self.bert = BertModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, self.config.num_labels)

        self.apply(self.init_weights)

    def forward(self, input_ids, token_type_ids=None, attention_mask=None, labels=None,
                position_ids=None, head_mask=None):
        outputs = self.bert(input_ids, position_ids=position_ids, token_type_ids=token_type_ids,
                            attention_mask=attention_mask, head_mask=head_mask)
        pooled_output = outputs[1]

        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)

        outputs = (logits,) + outputs[2:]  # add hidden states and attention if they are here

        if labels is not None:
            loss_fct = nn.BCEWithLogitsLoss()
            loss = loss_fct(logits, labels)
            outputs = (loss,) + outputs

        return outputs  # (loss), logits, (hidden_states), (attentions)


# In[8]:


model = BertForMultiLabelSequenceClassification.from_pretrained(BERT_MODEL, num_labels=len(label2idx))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.train()


# ## Preprocessing
# 
# We preprocess the data by turning every example to an `InputFeatures` item. This item has all the attributes we need for finetuning BERT: 
# 
# - input ids: the ids of the tokens in the text
# - input mask: tells BERT what part of the input it should not look at (such as padding tokens)
# - segment ids: tells BERT what segment every token belongs to. BERT can take two different segments as input
# - label id: the id of this item's label

# In[ ]:


import logging
import numpy as np

logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S',
                    level = logging.INFO)
logger = logging.getLogger(__name__)

MAX_SEQ_LENGTH=100

class InputFeatures(object):
    """A single set of features of data."""

    def __init__(self, input_ids, input_mask, segment_ids, label_ids):
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.segment_ids = segment_ids
        self.label_ids = label_ids
        

def convert_examples_to_features(examples, label2idx, max_seq_length, tokenizer, verbose=0):
    """Loads a data file into a list of `InputBatch`s."""
    
    features = []
    for (ex_index, ex) in enumerate(examples):
        
        # TODO: should deal better with sentences > max tok length
        input_ids = tokenizer.encode("[CLS] " + ex["text"] + " [SEP]")
        segment_ids = [0] * len(input_ids)
            
        # The mask has 1 for real tokens and 0 for padding tokens. Only real
        # tokens are attended to.
        input_mask = [1] * len(input_ids)

        # Zero-pad up to the sequence length.
        padding = [0] * (max_seq_length - len(input_ids))
        input_ids += padding
        input_mask += padding
        segment_ids += padding

        assert len(input_ids) == max_seq_length
        assert len(input_mask) == max_seq_length
        assert len(segment_ids) == max_seq_length

        label_ids = np.zeros(len(label2idx))
        for label in ex["label"]:
            label_ids[label2idx[label]] = 1
        
        if verbose and ex_index == 0:
            logger.info("*** Example ***")
            logger.info("text: %s" % ex["text"])
            logger.info("input_ids: %s" % " ".join([str(x) for x in input_ids]))
            logger.info("input_mask: %s" % " ".join([str(x) for x in input_mask]))
            logger.info("segment_ids: %s" % " ".join([str(x) for x in segment_ids]))
            logger.info("label:" + str(ex["label"]) + " id: " + str(label_ids))

        features.append(
                InputFeatures(input_ids=input_ids,
                              input_mask=input_mask,
                              segment_ids=segment_ids,
                              label_ids=label_ids))
    return features

train_features = convert_examples_to_features(train_data, label2idx, MAX_SEQ_LENGTH, tokenizer, verbose=0)
dev_features = convert_examples_to_features(dev_data, label2idx, MAX_SEQ_LENGTH, tokenizer)
test_features = convert_examples_to_features(test_data, label2idx, MAX_SEQ_LENGTH, tokenizer, verbose=1)


# Next, we initialize data loaders for each of our data sets. These data loaders present the data for training (for example, by grouping them into batches).

# In[ ]:


import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler

def get_data_loader(features, max_seq_length, batch_size, shuffle=True): 

    all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long)
    all_input_mask = torch.tensor([f.input_mask for f in features], dtype=torch.long)
    all_segment_ids = torch.tensor([f.segment_ids for f in features], dtype=torch.long)
    all_label_ids = torch.tensor([f.label_ids for f in features], dtype=torch.float)
    data = TensorDataset(all_input_ids, all_input_mask, all_segment_ids, all_label_ids)

    dataloader = DataLoader(data, shuffle=shuffle, batch_size=batch_size)
    
    return dataloader

train_dataloader = get_data_loader(train_features, MAX_SEQ_LENGTH, BATCH_SIZE)
dev_dataloader = get_data_loader(dev_features, MAX_SEQ_LENGTH, BATCH_SIZE)
test_dataloader = get_data_loader(test_features, MAX_SEQ_LENGTH, BATCH_SIZE, shuffle=False)


# ## Evaluation
# 
# Our evaluation method takes a pretrained model and a dataloader. It has the model predict the labels for the items in the data loader, and returns the loss, the correct labels, and the predicted labels.

# In[ ]:


from torch.nn import Sigmoid

def evaluate(model, dataloader, verbose=False):

    eval_loss = 0
    nb_eval_steps = 0
    predicted_labels, correct_labels = [], []

    for step, batch in enumerate(tqdm(dataloader, desc="Evaluation iteration")):
        batch = tuple(t.to(device) for t in batch)
        input_ids, input_mask, segment_ids, label_ids = batch

        with torch.no_grad():
            tmp_eval_loss, logits = model(input_ids, segment_ids, input_mask, label_ids)

        sig = Sigmoid()
        outputs = sig(logits).to('cpu').numpy()
        label_ids = label_ids.to('cpu').numpy()
        
        predicted_labels += list(outputs >= 0.5)        
        correct_labels += list(label_ids)
                    
        eval_loss += tmp_eval_loss.mean().item()
        nb_eval_steps += 1

    eval_loss = eval_loss / nb_eval_steps
    
    correct_labels = np.array(correct_labels)
    predicted_labels = np.array(predicted_labels)
        
    return eval_loss, correct_labels, predicted_labels


# ## Training
# 
# Let's prepare the training. We set the training parameters and choose an optimizer and learning rate scheduler.

# In[ ]:


from pytorch_transformers.optimization import AdamW, WarmupLinearSchedule

NUM_TRAIN_EPOCHS = 20
LEARNING_RATE = 1e-5
WARMUP_PROPORTION = 0.1

def warmup_linear(x, warmup=0.002):
    if x < warmup:
        return x/warmup
    return 1.0 - x

num_train_steps = int(len(train_data) / BATCH_SIZE / GRADIENT_ACCUMULATION_STEPS * NUM_TRAIN_EPOCHS)

param_optimizer = list(model.named_parameters())
no_decay = ['bias', 'LayerNorm.bias', 'LayerNorm.weight']
optimizer_grouped_parameters = [
    {'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
    {'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
    ]

optimizer = AdamW(optimizer_grouped_parameters, lr=LEARNING_RATE, correct_bias=False)
scheduler = WarmupLinearSchedule(optimizer, warmup_steps=100, t_total=num_train_steps)


# Now we do the actual training. In each epoch, we present the model with all training data and compute the loss on the training set and the development set. We save the model whenever the development loss improves. We end training when we haven't seen an improvement of the development loss for a specific number of epochs (the patience). 
# 
# Optionally, we use gradient accumulation to accumulate the gradient for several training steps. This is useful when we want to use a larger batch size than our current GPU allows us to do.

# In[ ]:


import os
from tqdm import trange
from tqdm import tqdm
from sklearn.metrics import classification_report, precision_recall_fscore_support

OUTPUT_DIR = "/tmp/"
MODEL_FILE_NAME = "pytorch_model.bin"
PATIENCE = 5

global_step = 0
model.train()
loss_history = []
best_epoch = 0
for epoch in trange(int(NUM_TRAIN_EPOCHS), desc="Epoch"):
    tr_loss = 0
    nb_tr_examples, nb_tr_steps = 0, 0
    for step, batch in enumerate(tqdm(train_dataloader, desc="Training iteration")):
        batch = tuple(t.to(device) for t in batch)
        input_ids, input_mask, segment_ids, label_ids = batch
        outputs = model(input_ids, segment_ids, input_mask, label_ids)
        loss = outputs[0]
        
        if GRADIENT_ACCUMULATION_STEPS > 1:
            loss = loss / GRADIENT_ACCUMULATION_STEPS

        loss.backward()

        tr_loss += loss.item()
        nb_tr_examples += input_ids.size(0)
        nb_tr_steps += 1
        if (step + 1) % GRADIENT_ACCUMULATION_STEPS == 0:
            lr_this_step = LEARNING_RATE * warmup_linear(global_step/num_train_steps, WARMUP_PROPORTION)
            for param_group in optimizer.param_groups:
                param_group['lr'] = lr_this_step
            optimizer.step()
            optimizer.zero_grad()
            global_step += 1

    dev_loss, _, _ = evaluate(model, dev_dataloader)
    
    print("Loss history:", loss_history)
    print("Dev loss:", dev_loss)
    
    if len(loss_history) == 0 or dev_loss < min(loss_history):
        model_to_save = model.module if hasattr(model, 'module') else model
        output_model_file = os.path.join(OUTPUT_DIR, MODEL_FILE_NAME)
        torch.save(model_to_save.state_dict(), output_model_file)
        best_epoch = epoch
    
    if epoch-best_epoch >= PATIENCE: 
        print("No improvement on development set. Finish training.")
        break
        
    
    loss_history.append(dev_loss)


# ## Results
# 
# We load the pretrained model, set it to evaluation mode and compute its performance on the training, development and test set. We print out an evaluation report for the test set.
# 
# Note that different runs will give slightly different results.

# In[ ]:


from tqdm import tqdm_notebook as tqdm

output_model_file = "/tmp/pytorch_model.bin"
print("Loading model from", output_model_file)
device="cpu"

model_state_dict = torch.load(output_model_file, map_location=lambda storage, loc: storage)
model = BertForMultiLabelSequenceClassification.from_pretrained(BERT_MODEL, state_dict=model_state_dict, num_labels=len(label2idx))
model.to(device)

model.eval()
_, test_correct, test_predicted = evaluate(model, test_dataloader, verbose=True)


# In[ ]:


all_correct = 0
fp, fn, tp, tn = 0, 0, 0, 0
for c, p in zip(test_correct, test_predicted):
    if sum(c == p) == len(c):
        all_correct +=1
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
print("P:", precision)
print("R:", recall)
print("A:", all_correct/len(test_correct))


# In[ ]:


for item, predicted, correct in zip(test_data, test_predicted, test_correct):
    correct_labels = [idx2label[i] for i, l in enumerate(correct) if l == 1]
    predicted_labels = [idx2label[i] for i, l in enumerate(predicted) if l == 1]
    print("{}#{}#{}".format(item["text"], ";".join(correct_labels), ";".join(predicted_labels)))


# In[ ]:




