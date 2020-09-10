import spacy
import torch
import json

from typing import List

from transformers import BertForTokenClassification, BertTokenizer

from quillnlp.grammar.unsupervised import UnsupervisedGrammarChecker, classify_agreement_errors, Error
from quillnlp.grammar.verbs import agreement
from quillnlp.models.bert.train import evaluate
from quillnlp.models.bert.preprocessing import convert_data_to_input_items, get_data_loader, NLPTask
from quillnlp.grammar.constants import *
from quillnlp.grammar.rules import RuleBasedGrammarChecker, statistical_error_map, error_precedence

BASE_SPACY_MODEL = "en"


class SpaCyGrammarChecker:
    """
    A grammar checker that combines both rule-based and statistical
    grammar error checking with spaCy.
    """

    def __init__(self, model_paths: List[str]):
        if len(model_paths) > 0:
            self.model = spacy.load(model_paths[0])

            # Replace the NER pipe of our model by spaCy's standard NER pipe.
            base_spacy = spacy.load(BASE_SPACY_MODEL)
            self.model.add_pipe(base_spacy.get_pipe("ner"), 'base_ner',
                                before="ner")

        self.alternative_models = []
        if len(model_paths) > 1:
            self.alternative_models = [spacy.load(model) for model in model_paths]

        self.rule_based_checker = RuleBasedGrammarChecker()
        #self.sva_checker = UnsupervisedGrammarChecker()

    def clean_errors(self, errors: List[Error]) -> List[Error]:
        """
        Combine and clean errors. This fixes those cases in particular where
        one token has several errors and one takes precedence over the other.

        Args:
            errors:

        Returns:

        """
        errors_copy = [e for e in errors]
        for e in errors_copy:
            if e.type == GrammarError.PASSIVE_WITH_INCORRECT_BE.value and e.subject is None:
                errors.remove(e)

        if len(errors) > 0:
            #print(errors)
            errors.sort(key=lambda x: error_precedence.get(x.type, 0), reverse=True)
            return [errors[0]]
        return []

    def check(self, sentence: str) -> List[Error]:
        """
        Check a sentence for grammar errors.

        Args:
            sentence: the sentence that will be checked

        Returns: a list of errors. Every error is a tuple of (token,
                 token character offset, error type)

        """

        doc = self.model(sentence)

        # Get rule-based errors
        errors = self.rule_based_checker.check(doc)
        #errors += self.sva_checker.check(sentence)

        # Add statistical errors
        """
        for token in doc:
            # Exclude spaCy's built-in entity types
            # (characterized by upper characters)
            if token.ent_type_:
                error_type = statistical_error_map.get(token.ent_type_, token.ent_type_)
                subject = agreement.get_subject(token, full=True)
                subject_string = " ".join([t.text.lower() for t in subject]) if subject is not None else None

                if error_type.isupper():
                    continue
                elif error_type == GrammarError.SUBJECT_VERB_AGREEMENT.value and token.tag_ == Tag.SIMPLE_PAST_VERB.value:
                    continue
                elif error_type == GrammarError.SUBJECT_VERB_AGREEMENT.value:
                    error_type, subject_string = classify_agreement_errors(token, error_type)
                    #error_type, subject_string = GrammarError.SVA_SEPARATE.value, None

                errors.append(Error(token.text,
                                    token.idx,
                                    error_type,
                                    subject_string),
                              )
        """

        for (i, model) in enumerate(self.alternative_models):

            alternative_doc = model(sentence)
            for token in alternative_doc:
                if token.ent_type_:
                    error_type = statistical_error_map.get(token.ent_type_, token.ent_type_)
                    subject = agreement.get_subject(token, full=True)
                    subject_string = " ".join([t.text.lower() for t in subject]) if subject is not None else None

                    """
                    if error_type == GrammarError.SUBJECT_VERB_AGREEMENT.value:
                        if subject is not None:
                            new_sentence = subject_string + " " + token.text.lower()
                            new_doc = model(new_sentence)
                            if len(new_doc.ents) == 0:
                                continue
                    """

                    if error_type.isupper():
                        continue
                    elif error_type == GrammarError.SUBJECT_VERB_AGREEMENT.value and token.tag_ == Tag.SIMPLE_PAST_VERB.value:
                        continue
                    elif error_type == GrammarError.SUBJECT_VERB_AGREEMENT.value:
                        continue
                    #elif error_type == GrammarError.PERFECT_TENSE_WITH_SIMPLE_PAST.value:
                    #    continue
                    #    error_type, subject_string = classify_agreement_errors(token, error_type)

                    errors.append(Error(token.text,
                                        token.idx,
                                        error_type,
                                        subject_string),
                                  )

        cleaned_errors = self.clean_errors(errors)

        return cleaned_errors


class BertGrammarChecker:
    """
    A grammar checker that combines both rule-based and statistical
    grammar error checking with BERT.
    """

    def __init__(self, model_path: str, config_path: str):
        self.rule_based_checker = RuleBasedGrammarChecker()
        self.spacy_model = spacy.load(BASE_SPACY_MODEL)

        print("Loading BERT model from", model_path)
        self.device = "cpu"

        with open(config_path) as i:
            config = json.load(i)

        self.label2idx = config["labels"]
        self.max_seq_length = config["max_seq_length"]

        self.idx2label = {v:k for k,v in self.label2idx.items()}

        self.tokenizer = BertTokenizer.from_pretrained(config["base_model"])
        model_state_dict = torch.load(model_path, map_location=lambda storage, loc: storage)
        self.model = BertForTokenClassification.from_pretrained(config["base_model"],
                                                                state_dict=model_state_dict,
                                                                num_labels=len(self.label2idx))
        self.model.to(self.device)

    def check(self, sentence: str) -> List[Error]:
        """
        Check a sentence for grammar errors.

        Args:
            sentence: the sentence that will be checked

        Returns: a list of errors. Every error is a tuple of (token,
                 token character offset, error type)

        """

        # Get rule-based errors
        doc = self.spacy_model(sentence)
        rule_errors = self.rule_based_checker(doc)

        preprocessed_sentence = convert_data_to_input_items([{"text": sentence}],
                                                            self.label2idx,
                                                            self.max_seq_length,
                                                            self.tokenizer,
                                                            NLPTask.SEQUENCE_LABELING)

        sentence_dl = get_data_loader(preprocessed_sentence, 1, NLPTask.SEQUENCE_LABELING, shuffle=False)
        _, _, _, predicted_errors = evaluate(self.model, sentence_dl, self.device)

        stat_errors = [self.idx2label[i] for i in set(predicted_errors[0])]
        stat_errors = [Error("", 0, statistical_error_map[e]) for e in stat_errors if e in statistical_error_map]

        return rule_errors + stat_errors

