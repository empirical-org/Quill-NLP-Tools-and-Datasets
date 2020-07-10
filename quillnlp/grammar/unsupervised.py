from collections import namedtuple

import spacy

from transformers import pipeline

from quillnlp.grammar.constants import TokenSet, GrammarError, Tag
from quillnlp.grammar.verbs import agreement
from quillnlp.grammar.spacy import nlp
from quillnlp.grammar.verbutils import has_noun_subject, has_pronoun_subject, is_passive, in_have_been_construction, \
    get_past_tenses, has_inversion, get_subject, token_has_inversion

Error = namedtuple("Error", ["text", "index", "type", "subject"])


def classify_agreement_errors(token, error_type):

    if token.tag_ == Tag.PAST_PARTICIPLE_VERB.value:
        return GrammarError.PERFECT_TENSE_WITH_SIMPLE_PAST.value

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
        self.unmasker = pipeline('fill-mask', model='bert-base-uncased', topk=100)
        self.nlp = nlp

    def check(self, sentence: str):

        doc = self.nlp(sentence)

        present_verb_tags = set(["VBZ", "VB", "VBP"])
        synonyms = {"am": "'m", "are": "'re", "is": "'s", "have": "'ve",
                    "will": "'ll", "would": "'d", "wo": "will", "ca": "can"}
        synonyms_reversed = {v: k for k, v in synonyms.items()}
        synonyms.update(synonyms_reversed)

        errors = []
        for token in doc:
            if token.tag_ in present_verb_tags:
                masked_sentence = "".join([t.text_with_ws if t != token else self.unmasker.tokenizer.mask_token + t.whitespace_ for t in doc])
                masked_sentence = masked_sentence.replace(self.unmasker.tokenizer.mask_token + "n't",
                                                          self.unmasker.tokenizer.mask_token + " not")
                predictions = self.unmasker(masked_sentence)

                be_forms = set(["be", "am", "are", "is"])
                contracted_be_forms = set(["'s", "'m", "'re"])
                if token.text.lower() in be_forms:
                    alternative_forms = set([f for f in be_forms if f != token.text.lower()])
                    alternative_forms.update([synonyms[f] for f in alternative_forms if f in synonyms])
                elif token.text.lower() in contracted_be_forms:
                    alternative_forms = set([f for f in contracted_be_forms if f != token.text.lower()])
                    alternative_forms.update([synonyms[f] for f in alternative_forms if f in synonyms])
                else:
                    alternative_forms = set(
                        [token._.inflect(tag) for tag in present_verb_tags if not tag == token.tag_])

                for prediction in predictions:
                    predicted_token = self.unmasker.tokenizer.convert_ids_to_tokens(prediction["token"])
                    predicted_token = predicted_token.replace("Ġ", "") # for Roberta tokenizer
                    if predicted_token == token.text:
                        break
                    elif token.text in synonyms and synonyms[token.text] == predicted_token:
                        break
                    elif predicted_token in alternative_forms:

                        # needs
                        correct_sentence = masked_sentence.replace(self.unmasker.tokenizer.mask_token,
                                                                   predicted_token)

                        correct_token = self.nlp(correct_sentence)[token.i]

                        #subject = agreement.get_subject(token, full=True)
                        #subject_string = " ".join([t.text.lower() for t in subject]) if subject is not None else None

                        error_type, subject_string = classify_agreement_errors(correct_token, GrammarError.SUBJECT_VERB_AGREEMENT.value)

                        errors.append(Error(token.text,
                                            token.idx,
                                            error_type,
                                            subject_string),
                                      )
                        break

        return errors

