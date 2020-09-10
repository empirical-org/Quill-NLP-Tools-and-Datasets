from grammar.constants import Tag, GrammarError, TokenSet
from grammar.verbutils import has_noun_subject, get_subject, is_passive, has_pronoun_subject, is_perfect
from grammar.utils import Error
from grammar.checks.myspacy import nlp


def classify_error(error: Error):

    doc = nlp(error.predicted_sentence)
    token = None
    for t in doc:
        if t.idx == error.index:
            token = t
    if not token:
        return error

    if token.tag_ == Tag.PAST_PARTICIPLE_VERB.value:
        if is_passive(token) and is_perfect(token):
            error.set_type(GrammarError.PASSIVE_PERFECT_WITH_INCORRECT_PARTICIPLE.value)
        elif is_passive(token):
            error.set_type(GrammarError.INCORRECT_PAST_TENSE_AS_PARTICIPLE_IN_PASSIVE.value)
        else:
            error.set_type(GrammarError.PAST_TENSE_INSTEAD_OF_PARTICIPLE.value)
        return error

    subject = get_subject(token, full=True)
    error.subject = " ".join([t.text.lower() for t in subject]) if subject is not None else None
    if error.type == GrammarError.SUBJECT_VERB_AGREEMENT.value:
        subject_set = set([t.text.lower() for t in subject]) if subject is not None else None
        if token.text.lower() in TokenSet.BE_FORMS.value and is_passive(token):
            error.set_type(GrammarError.PASSIVE_WITH_INCORRECT_BE)
        if subject is not None and token.i < subject[0].i:
            error.set_type(GrammarError.SVA_INVERSION.value)
        elif subject is not None and len(subject_set.intersection(TokenSet.INDEF_PRONOUNS.value)) > 0:
            error.set_type(GrammarError.SVA_INDEFINITE.value)
        elif has_noun_subject(token):
            subject_token = get_subject(token, full=False)
            if subject_token.text.lower() in TokenSet.COLLECTIVE_NOUNS.value:
                error.set_type(GrammarError.SVA_COLLECTIVE_NOUN.value)
            else:
                error.set_type(GrammarError.SVA_SIMPLE_NOUN.value)
        elif has_pronoun_subject(token):
            error.set_type(GrammarError.SVA_PRONOUN.value)

    return error
