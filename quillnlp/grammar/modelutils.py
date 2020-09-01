import re
from collections import namedtuple
from typing import List, Set

import time
from spacy.tokens.doc import Doc
from spacy.tokens.token import Token
import lemminflect

from transformers import pipeline, AutoTokenizer, AutoModelWithLMHead

from quillnlp.grammar.constants import TokenSet, GrammarError, Tag, POS
from quillnlp.grammar.verbs import agreement
from quillnlp.grammar.myspacy import nlp
from quillnlp.grammar.verbutils import has_noun_subject, has_pronoun_subject, is_passive, in_have_been_construction, \
    get_past_tenses, has_inversion, get_subject, token_has_inversion

Error = namedtuple("Error", ["text", "index", "type", "subject"])

PRESENT_VERB_TAGS = set(["VBZ", "VB", "VBP"])
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
                 "it": GrammarError.SUBJECT_PRONOUN.value,
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

TARGET_OPEN_TAG = "<target>"
TARGET_CLOSE_TAG = "</target>"

def make_request(sentence: str, prompt=""):
    request = {
        "sentence": sentence,
        "targets": []
    }

    prompt_char_length = len(prompt)

    for token in nlp(sentence):

        if token.idx < prompt_char_length:
            continue

        alternative_forms = None

        if token.text.lower() in TARGET_TOKENS:
            alternative_forms = TARGET_TOKENS.get(token.text.lower())
        elif token.text.lower() in BE_FORMS:
            alternative_forms = set([f for f in BE_FORMS if f != token.text.lower()])
            alternative_forms.update([synonyms[f] for f in alternative_forms if f in synonyms])
        elif token.text.lower() in CONTRACTED_BE_FORMS:
            alternative_forms = set([f for f in CONTRACTED_BE_FORMS if f != token.text.lower()])
            alternative_forms.update([synonyms[f] for f in alternative_forms if f in synonyms])
        elif token.pos_ == POS.VERB.value:
            alternative_forms = set(
                [token._.inflect(tag) for tag in PRESENT_VERB_TAGS if not tag == token.tag_])

        if alternative_forms:
            request["targets"].append({
                "token": token.text.lower(),
                "start": token.idx,
                "alternatives": list(alternative_forms),
            })

    return request


def create_masked_sentences(sentence, tokenizer):
    for match in re.finditer(f"{TARGET_OPEN_TAG}.+?{TARGET_CLOSE_TAG}", sentence):
        target_token = match.group(0).replace(TARGET_OPEN_TAG, "").replace(TARGET_CLOSE_TAG, "")
        masked_sentence = sentence[:match.start()] + tokenizer.mask_token + sentence[match.end():]
        masked_sentence = masked_sentence.replace(TARGET_OPEN_TAG, "").replace(TARGET_CLOSE_TAG, "")
        yield {"token": target_token,
               "masked_sentence": masked_sentence,
               "alternatives": TARGET_TOKENS[target_token.lower()]}



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


def classify_agreement_errors(token, error_type):

    if token.tag_ == Tag.PAST_PARTICIPLE_VERB.value:
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



    def check(self, sentence: str) -> List[Error]:

        if sentence.strip()[-1] not in TokenSet.END_OF_SENTENCE_PUNCTUATION.value:
            sentence += "."

        doc = self.nlp(sentence)

        errors = []
        for token in doc:

            # If we meet a present verb in the sentence, we check it.
            if token.tag_ in PRESENT_VERB_TAGS or token.text.lower() in TARGET_TOKENS:
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
