import re
from collections import namedtuple
from typing import List, Set

import time
import torch
from spacy.tokens.doc import Doc
from spacy.tokens.token import Token

from transformers import pipeline, AutoTokenizer, AutoModelWithLMHead

from quillnlp.grammar.constants import TokenSet, GrammarError, Tag
from quillnlp.grammar.verbs import agreement
from quillnlp.grammar.myspacy import nlp
from quillnlp.grammar.verbutils import has_noun_subject, has_pronoun_subject, is_passive, in_have_been_construction, \
    get_past_tenses, has_inversion, get_subject, token_has_inversion

Error = namedtuple("Error", ["text", "index", "type", "subject"])

PRESENT_VERB_TAGS = set(["VBZ", "VB", "VBP"])
OTHER_VERB_TAGS = set(["VBD", "VBN"])
ALL_VERB_TAGS = PRESENT_VERB_TAGS | OTHER_VERB_TAGS
BE_FORMS = set(["be", "am", "are", "is"])
CONTRACTED_BE_FORMS = set(["'s", "'m", "'re"])
TARGET_TOKENS = {"then": ["than"],
                 "than": ["then"],
                 "i": ["me", "my", "mine"],
                 "you": ["your", "yours"],
                 "he": ["him", "his"],
                 "she": ["her", "hers"],
                 "it": ["its"],
                 "we": ["us", "our", "ours"],
                 "they": ["them", "their", "theirs"],
                 "me": ["i"],
                 "my": ["i"],
                 "mine": ["i"],
                 "your": ["you"],
                 "yours": ["you"],
                 "him": ["he"],
                 "his": ["he"],
                 "her": ["she"],
                 "hers": ["she"],
                 "its": ["it"],
                 "us": ["we"],
                 "our": ["we"],
                 "ours": ["we"],
                 "them": ["they"],
                 "their": ["they"],
                 "theirs": ["they"],
                 "an": ["a"],
                 "a": ["an"],
                 "man": ["men"],
                 "men": ["man"],
                 "been": ["is", "are", "was"],
                 ".": ["?"],
                 ";": ["?"],
                 ":": ["?"],
                 ",": ["?"],
                 "!": ["?"]}

TOKENS2ERRORS = {"then": GrammarError.THAN_THEN.value,
                 "than": GrammarError.THAN_THEN.value,
                 "i": GrammarError.OBJECT_PRONOUN.value,
                 "you": GrammarError.OBJECT_PRONOUN.value,
                 "he": GrammarError.OBJECT_PRONOUN.value,
                 "she": GrammarError.OBJECT_PRONOUN.value,
                 "we": GrammarError.OBJECT_PRONOUN.value,
                 "they": GrammarError.OBJECT_PRONOUN.value,
                 "me": GrammarError.SUBJECT_PRONOUN.value,
                 "my": GrammarError.SUBJECT_PRONOUN.value,
                 "mine": GrammarError.SUBJECT_PRONOUN.value,
                 "your": GrammarError.SUBJECT_PRONOUN.value,
                 "yours": GrammarError.SUBJECT_PRONOUN.value,
                 "him": GrammarError.SUBJECT_PRONOUN.value,
                 "his": GrammarError.SUBJECT_PRONOUN.value,
                 "her": GrammarError.SUBJECT_PRONOUN.value,
                 "hers": GrammarError.SUBJECT_PRONOUN.value,
                 "its": GrammarError.SUBJECT_PRONOUN.value,
                 "us": GrammarError.SUBJECT_PRONOUN.value,
                 "our": GrammarError.SUBJECT_PRONOUN.value,
                 "ours": GrammarError.SUBJECT_PRONOUN.value,
                 "them": GrammarError.SUBJECT_PRONOUN.value,
                 "their": GrammarError.SUBJECT_PRONOUN.value,
                 "theirs": GrammarError.SUBJECT_PRONOUN.value,
                 "a": GrammarError.ARTICLE.value,
                 "an": GrammarError.ARTICLE.value,
                 "been": GrammarError.PASSIVE_WITH_INCORRECT_BE.value,
                 ".": GrammarError.QUESTION_MARK.value,
                 ":": GrammarError.QUESTION_MARK.value,
                 ";": GrammarError.QUESTION_MARK.value,
                 ",": GrammarError.QUESTION_MARK.value,
                 "!": GrammarError.QUESTION_MARK.value}


synonyms = {"am": "'m", "are": "'re", "is": "'s", "have": "'ve",
            "will": "'ll", "would": "'d", "wo": "will", "ca": "can"}
synonyms_reversed = {v: k for k, v in synonyms.items()}
synonyms.update(synonyms_reversed)


def classify_agreement_errors(token, error_type):

    if token.tag_ == Tag.PAST_PARTICIPLE_VERB.value:
        if is_passive(token):
            return GrammarError.PASSIVE_PERFECT_WITH_INCORRECT_PARTICIPLE.value, None
        else:
            return GrammarError.PERFECT_TENSE_WITH_SIMPLE_PAST.value, None

    subject = agreement.get_subject(token, full=True)
    subject_string = " ".join([t.text.lower() for t in subject]) if subject is not None else None
    if error_type == GrammarError.SUBJECT_VERB_AGREEMENT.value:
        subject_set = set([t.text.lower() for t in subject]) if subject is not None else None
        if subject is not None and token.i < subject[0].i:
            error_type = GrammarError.SVA_INVERSION.value
        elif subject is not None and len(subject_set.intersection(TokenSet.INDEF_PRONOUNS.value)) > 0:
            error_type = GrammarError.SVA_INDEFINITE.value
        elif has_noun_subject(token):
            subject = agreement.get_subject(token, full=False)
            if subject.text.lower() in TokenSet.COLLECTIVE_NOUNS.value:
                error_type = GrammarError.SVA_COLLECTIVE_NOUN.value
            else:
                error_type = GrammarError.SVA_SIMPLE_NOUN.value
        elif has_pronoun_subject(token):
            error_type = GrammarError.SVA_PRONOUN.value

    return error_type, subject_string


class UnsupervisedGrammarChecker():

    def __init__(self):
        #self.unmasker = pipeline('fill-mask', model='bert-base-uncased', topk=100)
        self.unmasker = pipeline('fill-mask', model='albert-base-v2', topk=1000, framework="pt")
        self.nlp = nlp

    def _create_masked_sentence(self, token: Token, doc: Doc) -> str:
        masked_sentence = "".join(
            [t.text_with_ws if t != token else self.unmasker.tokenizer.mask_token + t.whitespace_ for t in doc])
        masked_sentence = masked_sentence.replace(self.unmasker.tokenizer.mask_token + "n't",
                                                  self.unmasker.tokenizer.mask_token + " not")
        return masked_sentence

    def _get_alternative_forms(self, token: Token) -> Set[str]:
        if token.text.lower() in TARGET_TOKENS:
            return TARGET_TOKENS[token.text.lower()]
        elif token.text.lower() in BE_FORMS:
            alternative_forms = set([f for f in BE_FORMS if f != token.text.lower()])
            alternative_forms.update([synonyms[f] for f in alternative_forms if f in synonyms])
        elif token.text.lower() in CONTRACTED_BE_FORMS:
            alternative_forms = set([f for f in CONTRACTED_BE_FORMS if f != token.text.lower()])
            alternative_forms.update([synonyms[f] for f in alternative_forms if f in synonyms])
        elif token.tag_ in PRESENT_VERB_TAGS:
            alternative_forms = set(
                [token._.inflect(tag) for tag in PRESENT_VERB_TAGS])
        elif token.tag_ in OTHER_VERB_TAGS:
            alternative_forms = set(
                [token._.inflect(tag) for tag in OTHER_VERB_TAGS])
        else:
            alternative_forms = set()

        if token.text.lower() in alternative_forms:
            alternative_forms.remove(token.text.lower())

        print("ALT", alternative_forms)

        return alternative_forms

    def check(self, sentence: str) -> List[Error]:

        if sentence.strip()[-1] not in TokenSet.END_OF_SENTENCE_PUNCTUATION.value:
            sentence += "."

        doc = self.nlp(sentence)

        errors = []
        for token in doc:

            # If we meet a present verb in the sentence, we check it.
            if token.tag_ in ALL_VERB_TAGS or token.text.lower() in TARGET_TOKENS:
                print("Token:", token, token.tag_)
                t1 = time.time()
                masked_sentence = self._create_masked_sentence(token, doc)
                t2 = time.time()
                predictions = self.unmasker(masked_sentence)
                t3 = time.time()
                #print(f"Masking: {t2-t1} secs")
                #print(f"Predicting: {t3-t2} secs")
                alternative_forms = self._get_alternative_forms(token)

                #print([self.unmasker.tokenizer.convert_ids_to_tokens(prediction["token"]) for prediction in predictions])

                for prediction in predictions:
                    predicted_token = self.unmasker.tokenizer.convert_ids_to_tokens(prediction["token"])
                    predicted_token = predicted_token.replace("Ġ", "")  # for Roberta tokenizer
                    predicted_token = predicted_token.replace("▁", "")  # for Albert tokenizer

                    print("Prediction:", predicted_token)

                    # If the token itself is ranked highest in the list of predictions,
                    # then it is likely correct.
                    if predicted_token.lower() == token.text.lower():
                        break

                    # If a synonym of the token is ranked highest in the list of predictions,
                    # then it is likely correct.
                    elif token.text in synonyms and synonyms[token.text] == predicted_token:
                        break

                    # If an alternative form is ranked highest in the list of predictions,
                    # then the token is likely an error.
                    elif predicted_token in alternative_forms:

                        print("Token:", token)
                        print("Prediction:", predicted_token)
                        correct_sentence = masked_sentence.replace(self.unmasker.tokenizer.mask_token,
                                                                   predicted_token)

                        correct_token = self.nlp(correct_sentence)[token.i]

                        if token.text.lower() in TOKENS2ERRORS:
                            error_type = TOKENS2ERRORS[token.text.lower()]
                            subject_string = None
                        else:
                            error_type, subject_string = classify_agreement_errors(correct_token,
                                                                                   GrammarError.SUBJECT_VERB_AGREEMENT.value)

                        errors.append(Error(token.text,
                                            token.idx,
                                            error_type,
                                            subject_string),
                                      )
                        break

        return errors


class UnsupervisedGrammarChecker2():

    def __init__(self):
        self.unmasker = pipeline('fill-mask', model='albert-large-v2', topk=100)
        self.nlp = nlp
        self.tokenizer = AutoTokenizer.from_pretrained("albert-large-v2")
        self.model = AutoModelWithLMHead.from_pretrained("albert-large-v2")

    def _get_alternative_forms(self, token: Token) -> Set[str]:
        if token.text.lower() in TARGET_TOKENS:
            return TARGET_TOKENS[token.text.lower()]
        elif token.text.lower() in BE_FORMS:
            alternative_forms = set([f for f in BE_FORMS if f != token.text.lower()])
            alternative_forms.update([synonyms[f] for f in alternative_forms if f in synonyms])
        elif token.text.lower() in CONTRACTED_BE_FORMS:
            alternative_forms = set([f for f in CONTRACTED_BE_FORMS if f != token.text.lower()])
            alternative_forms.update([synonyms[f] for f in alternative_forms if f in synonyms])
        else:
            alternative_forms = set(
                [token._.inflect(tag) for tag in PRESENT_VERB_TAGS if not tag == token.tag_])

        if token.text.lower() in alternative_forms:
            alternative_forms.remove(token.text.lower())

        return alternative_forms


    def check(self, sentence: str):

        doc = self.nlp(sentence)

        synonyms = {"am": "'m", "are": "'re", "is": "'s", "have": "'ve",
                    "will": "'ll", "would": "'d", "wo": "will", "ca": "can"}
        synonyms_reversed = {v: k for k, v in synonyms.items()}
        synonyms.update(synonyms_reversed)

        errors = []
        for token in doc:
            if token.tag_ in PRESENT_VERB_TAGS or token.text.lower() in TARGET_TOKENS:
                masked_sentence = "".join([t.text_with_ws if t != token else self.unmasker.tokenizer.mask_token + t.whitespace_ for t in doc])
                masked_sentence = masked_sentence.replace(self.unmasker.tokenizer.mask_token + "n't",
                                                          self.unmasker.tokenizer.mask_token + " not")
                #masked_sentence = re.sub(f"(?<=\S){re.escape(self.unmasker.tokenizer.mask_token)}",
                #                         f" {self.unmasker.tokenizer.mask_token}",
                #                         masked_sentence)  # it[MASK] => it [MASK]

                alternative_forms = self._get_alternative_forms(token)

                if token.text.lower() in alternative_forms:
                    alternative_forms.remove(token.text.lower())

                input = self.tokenizer.encode(masked_sentence, return_tensors="pt")
                mask_token_index = torch.where(input == self.tokenizer.mask_token_id)[1]

                token_logits = self.model(input)[0]
                mask_token_logits = token_logits[0, mask_token_index, :][0].tolist()

                predictions = []
                token_id = self.tokenizer.convert_tokens_to_ids("▁" + token.text.lower())
                predictions.append((mask_token_logits[token_id], token.text))

                if token.text.lower() in synonyms:
                    synonym = synonyms[token.text.lower()]
                    synonym_id = self.tokenizer.convert_tokens_to_ids("▁" + synonym)
                    if synonym_id is not None and synonym_id != self.tokenizer.unk_token_id:
                        predictions.append((mask_token_logits[synonym_id], synonym))

                for alternative_form in alternative_forms:
                    if alternative_form is not None:
                        alternative_form_id = self.tokenizer.convert_tokens_to_ids("▁" + alternative_form)
                        if alternative_form_id is not None and alternative_form_id != self.tokenizer.unk_token_id:
                            print(alternative_form, alternative_form_id)
                            predictions.append((mask_token_logits[alternative_form_id], alternative_form))

                predictions.sort(reverse=True)
                best_prediction = predictions[0][1]

                if best_prediction in alternative_forms:
                    correct_sentence = masked_sentence.replace(self.unmasker.tokenizer.mask_token,
                                                               best_prediction)

                    correct_token = self.nlp(correct_sentence)[token.i]

                    if token.text.lower() in TOKENS2ERRORS:
                        error_type = TOKENS2ERRORS[token.text.lower()]
                        subject_string = None
                    else:
                        error_type, subject_string = classify_agreement_errors(correct_token,
                                                                               GrammarError.SUBJECT_VERB_AGREEMENT.value)

                    errors.append(Error(token.text,
                                        token.idx,
                                        error_type,
                                        subject_string),
                                  )
        return errors
