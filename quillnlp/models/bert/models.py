from torch import nn
from pytorch_transformers.modeling_bert import BertPreTrainedModel, BertModel


class BertForSequenceEmbeddings(BertPreTrainedModel):
    """ A BERT model that simply returns sequence embeddings for a given input. These are
    the embeddings produced for the [CLS] token at the start of the output, which
    normally serve as input for the classification model we finetune.
    """

    def __init__(self, config):
        super(BertForSequenceEmbeddings, self).__init__(config)
        self.num_labels = config.num_labels

        self.bert = BertModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, self.config.num_labels)

        self.apply(self.init_weights)

    def forward(self, input_ids, token_type_ids=None, attention_mask=None,
                position_ids=None, head_mask=None):
        outputs = self.bert(input_ids, position_ids=position_ids, token_type_ids=token_type_ids,
                            attention_mask=attention_mask, head_mask=head_mask)
        pooled_output = outputs[1]

        pooled_output = self.dropout(pooled_output)

        return pooled_output
