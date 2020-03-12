import torch
import numpy as np
from torch.utils.data import TensorDataset, DataLoader
from typing import List, Dict, Union

from transformers.tokenization_bert import BertTokenizer
from transformers.tokenization_distilbert import DistilBertTokenizer


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
                 label_id: Union[int or List[int]]):
        self.text = text
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.segment_ids = segment_ids
        self.label_id = label_id


def create_label_vocabulary(data: List[Dict]) -> Dict:
    """
    Creates a dictionary that maps the labels in the data to their id. This
    works for both single-label data (where the "label" property is a string),
    and multi-label data (where the "label" property is a list.

    Args:
        data: a list of data items as dicts of the form {"text": ..., "label": ...}

    Returns: a dictionary that maps label strings to label ids

    """

    label2idx = {}
    for item in data:
        if type(item["label"]) == str and item["label"] not in label2idx:
            label2idx[item["label"]] = len(label2idx)
        elif type(item["label"]) == list:
            for l in item["label"]:
                if l not in label2idx:
                    label2idx[l] = len(label2idx)

    return label2idx


def convert_data_to_input_items(examples: List[Dict], label2idx: Dict,
                                max_seq_length: int, tokenizer: BertTokenizer) -> List[BertInputItem]:
    """
    Converts a list of input examples to BertInputItems

    Args:
        examples: a list of examples as dicts of the form {"text": ..., "label": ...}
        label2idx: a dict that maps label strings to label ids
        max_seq_length: the maximum sequence length for the input items
        tokenizer: the tokenizer that will be used to tokenize the text

    Returns: a list of BertInputItems

    """

    input_items = []
    for (ex_index, ex) in enumerate(examples):

        # Create a list of token ids
        toks = tokenizer.encode(ex["text"], max_length=max_seq_length, pad_to_max_length=True)
        input_ids = toks["input_ids"]
        segment_ids = toks["token_type_ids"]
        input_mask = toks["attention_mask"]

        if type(ex["label"]) == str:
            label_id = label2idx[ex["label"]]
        elif type(ex["label"]) == list:
            label_id = np.zeros(len(label2idx))
            for label in ex["label"]:
                label_id[label2idx[label]] = 1

        input_items.append(
            BertInputItem(text=ex["text"],
                          input_ids=input_ids,
                          input_mask=input_mask,
                          segment_ids=segment_ids,
                          label_id=label_id))
    return input_items


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

    if type(input_items[0].label_id) == int:
        all_label_ids = torch.tensor([f.label_id for f in input_items], dtype=torch.long)
    elif type(input_items[0].label_id) == np.ndarray:
        all_label_ids = torch.tensor([f.label_id for f in input_items], dtype=torch.float)

    data = TensorDataset(all_input_ids, all_input_mask, all_segment_ids, all_label_ids)

    dataloader = DataLoader(data, shuffle=shuffle, batch_size=batch_size)

    return dataloader


def preprocess(data: List[Dict], model: str,
               label2idx: Dict, max_seq_length: int) -> List[BertInputItem]:
    """
    Runs the full preprocessing pipeline on a list of data items.

    Args:
        data: a list of examples as dicts of the form {"text": ..., "label": ...}
        model: the name of the BERT model
        label2idx: a dict that maps label strings to label ids
        max_seq_length: the maximum sequence length for the input items

    Returns: a list of BertInputItems
    """
    if "distilbert" in model:
        tokenizer = DistilBertTokenizer.from_pretrained(model)
    else:
        tokenizer = BertTokenizer.from_pretrained(model)
    bert_items = convert_data_to_input_items(data, label2idx, max_seq_length, tokenizer)

    return bert_items
