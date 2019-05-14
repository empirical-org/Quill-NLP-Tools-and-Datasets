from typing import Dict
import json
import logging
import spacy
import neuralcoref

from copy import deepcopy
from overrides import overrides

from allennlp.common.file_utils import cached_path
from allennlp.data.dataset_readers.dataset_reader import DatasetReader
from allennlp.data.fields import MultiLabelField, TextField, LabelField
from allennlp.data.instance import Instance
from allennlp.data.tokenizers import Tokenizer, WordTokenizer
from allennlp.data.token_indexers.elmo_indexer import ELMoTokenCharactersIndexer
from allennlp.data.token_indexers import TokenIndexer, SingleIdTokenIndexer

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

nlp = spacy.load('en')
neuralcoref.add_to_pipe(nlp)

@DatasetReader.register("quill_responses")
class QuillResponsesDatasetReader(DatasetReader):
    """
    Reads a ndjson file with  with product reviews, and creates a
    dataset suitable for sentiment classification.

    Expected format for each input line: {"text": "text", "label": "text"}

    The output of ``read`` is a list of ``Instance`` s with the fields:
        text: ``TextField``
        label: ``MultiLabelField``

    where the ``label`` is either "pos" or "neg"

    Parameters
    ----------
    lazy : ``bool`` (optional, default=False)
        Passed to ``DatasetReader``.  If this is ``True``, training will start sooner, but will
        take longer per batch.  This also allows training with datasets that are too large to fit
        in memory.
    tokenizer : ``Tokenizer``, optional
        Tokenizer to use to split the review text into words or other kinds of tokens.
        Defaults to ``WordTokenizer()``.
    token_indexers : ``Dict[str, TokenIndexer]``, optional
        Indexers used to define input token representations. Defaults to ``{"tokens":
        SingleIdTokenIndexer()}``.
    """
    def __init__(self,
                 lazy: bool = False,
                 tokenizer: Tokenizer = None,
                 token_indexers: Dict[str, TokenIndexer] = None) -> None:
        super().__init__(lazy)
        self._tokenizer = tokenizer or WordTokenizer()
        self._token_indexers = token_indexers or {"tokens": SingleIdTokenIndexer()}

    @overrides
    def _read(self, file_path):
        with open(file_path, "r") as data_file:
            logger.info("Reading instances from lines in file at: %s", file_path)
            for line in data_file:
                line = line.strip("\n")
                if not line:
                    continue
                article_json = json.loads(line)
                text = article_json['text']
                label = article_json['label']
                yield self.text_to_instance(text, label)

    @overrides
    def text_to_instance(self, text: str, label: str = None) -> Instance:
        prompt = "Schools should not allow junk food to be sold on campus"
        print("T", text)
        doc = nlp(prompt + " " + text)
        copied_doc = spacy.tokens.Doc(nlp.vocab, words=[t.orth_ for t in doc])

        def replace_token_in_doc(doc, token_index, new_string):
            tokens = [t.orth_ for t in doc]
            tokens[token_index] = new_string
            new_doc = spacy.tokens.Doc(nlp.vocab, words=tokens)
            return new_doc

        if doc._.has_coref:
            for cluster in doc._.coref_clusters:
                if str(cluster[1]) == "they":
                    antecedent = str(cluster[0]).lower()
                    copied_doc = replace_token_in_doc(copied_doc, cluster[1].start, antecedent)

        text = copied_doc.text.strip()
        text = text.replace(prompt, "").strip()
        print("=>", text)
        tokenized_text = self._tokenizer.tokenize(text)
        text_field = TextField(tokenized_text, self._token_indexers)
        fields = {'tokens': text_field}
        if label is not None:
            fields['label'] = LabelField(label)
        return Instance(fields)
