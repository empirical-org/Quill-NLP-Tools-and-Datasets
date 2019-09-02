import torch
from torch.utils.data import TensorDataset, DataLoader
from typing import List, Dict, Union

from pytorch_transformers.tokenization_bert import BertTokenizer


class BertInputItem(object):
    """ A BertInputItem contains all the information that is needed to finetune
    a Bert model.

    Attributes:
        input_ids: the ids of the input tokens
        input_mask: a list of booleans that indicates what tokens should be masked
        segment_ids: a list of segment ids for the tokens
        label_id: a label id or a list of label ids for the input
    """

    def __init__(self, input_ids: List[int],
                 input_mask: List[int],
                 segment_ids: List[int],
                 label_id: Union[int or List[int]]):
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
        elif type(item["label"]) == "list":
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
        input_ids = tokenizer.encode("[CLS] " + ex["text"] + " [SEP]")
        if len(input_ids) > max_seq_length:
            input_ids = input_ids[:max_seq_length]

        # All our tokens are in the first input segment (id 0).
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

        if type(ex["label"]) == str:
            label_id = label2idx[ex["label"]]
        elif type(ex["label"]) == list:
            label_id = [label2idx[x] for x in ex["label"]]

        input_items.append(
            BertInputItem(input_ids=input_ids,
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
    all_label_ids = torch.tensor([f.label_id for f in input_items], dtype=torch.long)
    data = TensorDataset(all_input_ids, all_input_mask, all_segment_ids, all_label_ids)

    dataloader = DataLoader(data, shuffle=shuffle, batch_size=batch_size)

    return dataloader


def preprocess(data: List[Dict], model: str,
               label2idx: Dict, max_seq_length: int,
               batch_size, shuffle=True) -> DataLoader:
    """
    Runs the full preprocessing pipeline on a list of data items.

    Args:
        data: a list of examples as dicts of the form {"text": ..., "label": ...}
        model: the name of the BERT model
        label2idx: a dict that maps label strings to label ids
        max_seq_length: the maximum sequence length for the input items
        batch_size: the batch size
        shuffle: indicates whether the data should be shuffled or not.

    Returns: a DataLoader for the input items
    """

    tokenizer = BertTokenizer.from_pretrained(model)
    bert_items = convert_data_to_input_items(data, label2idx, max_seq_length, tokenizer)
    dataloader = get_data_loader(bert_items, batch_size, shuffle)

    return dataloader