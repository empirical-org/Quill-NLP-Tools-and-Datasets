from typing import Dict

from .constants import Tag, GrammarError, TokenSet
from .verbutils import has_noun_subject, get_subject, is_passive, has_pronoun_subject, is_perfect
from .utils import Error
from .checks.myspacy import nlp


def comma_between_subject_and_verb(subject, predicted_token, doc):
    if subject is None:
        return False

    last_subject_index = subject[-1].i
    for token in doc[last_subject_index + 1:predicted_token.i]:
        if token.text == ",":
            return True
    return False


def classify_error(error: Error, config: Dict):

    if error.predicted_sentence is not None:
        doc = nlp(error.predicted_sentence)
    else:
        doc = error.document

    predicted_token = None
    for t in doc:
        if t.idx == error.index:
            predicted_token = t
    if not predicted_token:
        return error

    if predicted_token.tag_ == Tag.PAST_PARTICIPLE_VERB.value:
        if is_passive(predicted_token) and is_perfect(predicted_token):
            error.set_type(GrammarError.PASSIVE_PERFECT_WITH_INCORRECT_PARTICIPLE.value, config)
        elif is_passive(predicted_token):
            error.set_type(GrammarError.INCORRECT_PAST_TENSE_AS_PARTICIPLE_IN_PASSIVE.value, config)
        else:
            error.set_type(GrammarError.PAST_TENSE_INSTEAD_OF_PARTICIPLE.value, config)
        return error

    subject = get_subject(predicted_token, full=True)
    error.subject = " ".join([t.text.lower() for t in subject]) if subject is not None else None

    if error.type == GrammarError.SUBJECT_VERB_AGREEMENT.value:
        if predicted_token.tag_ == Tag.SIMPLE_PAST_VERB.value:
            return None

        subject_set = set([t.text.lower() for t in subject]) if subject is not None else None

        if comma_between_subject_and_verb(subject, predicted_token, doc):
            error.set_type(GrammarError.SVA_SEPARATE.value, config)
        elif predicted_token.text.lower() in TokenSet.BE_FORMS.value and is_passive(predicted_token):
            error.set_type(GrammarError.PASSIVE_WITH_INCORRECT_BE.value, config)
        elif subject is not None and predicted_token.i < subject[0].i:
            error.set_type(GrammarError.SVA_INVERSION.value, config)
        elif subject is not None and len(subject_set.intersection(TokenSet.INDEF_PRONOUNS.value)) > 0:
            error.set_type(GrammarError.SVA_INDEFINITE.value, config)
        elif has_noun_subject(predicted_token):
            subject_token = get_subject(predicted_token, full=False)
            if subject_token.text.lower() in TokenSet.COLLECTIVE_NOUNS.value:
                error.set_type(GrammarError.SVA_COLLECTIVE_NOUN.value, config)
            else:
                error.set_type(GrammarError.SVA_SIMPLE_NOUN.value, config)
        elif has_pronoun_subject(predicted_token):
            error.set_type(GrammarError.SVA_PRONOUN.value, config)
        else:
            return None

    return error
