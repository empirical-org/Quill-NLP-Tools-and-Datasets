import random

import lemminflect

from quillnlp.grammar.constants import Tag, GrammarError
from quillnlp.grammar.generation import ErrorGenerator
from quillnlp.grammar.verbutils import has_noun_subject, \
    has_following_subject, subject_has_neither, subject_has_either, has_pronoun_subject, \
    has_indefinite_subject, has_relative_pronoun_subject



def replace_verb(token, doc):
    # present third-person singular -> other form

    if token.tag_ == Tag.PRESENT_SING3_VERB.value:
        if token.lemma_ == "be" and doc[token.i + 1].text.lower() == "n't":
            # only 'is' and 'are' can be followed by "n't"
            new_form = "are"
        elif token.lemma_ == "be":
            # most confusion will be between is and are, so are gets highest probability
            new_form = random.choice(["be", "am", "'re", "are", "are", "are"])
        else:
            new_form = token.lemma_

    # present other form -> third-person form
    elif token.tag_ == Tag.PRESENT_OTHER_VERB.value:
        if token.lemma_ == "be":
            other_forms = set(["be", "are", "am", "is", "'re", "'s"])
            if token.text.lower() in other_forms:
                other_forms.remove(token.text.lower())
            other_forms = list(other_forms)
            if "is" in other_forms:
                other_forms.extend(["is", "is", "is"])

            if doc[token.i + 1].text.lower() == "n't":
                new_form = 'is'
            else:
                new_form = random.choice(other_forms)

        # Deal with 'ain't', which has the lemma 'ai' and should not be
        # rewritten to 'aisn't'.
        elif token.text.lower() == 'ai':
            new_form = 'ai'
        # Deal with contracted forms like Im and Theyve, which miss an apostrophe
        # and do not get the correct lemma.
        elif token.i > 0 and not token.text.startswith("'") and doc[token.i-1].whitespace_ == '':
            new_form = token.text
        else:
            new_form = token._.inflect(Tag.PRESENT_SING3_VERB.value)

    # infinitive -> third-person
    elif token.tag_ == Tag.INFINITIVE.value:
        new_form = token._.inflect(Tag.PRESENT_SING3_VERB.value)

    # past: was -> were and vice versa
    elif token.tag_ == Tag.SIMPLE_PAST_VERB.value and token.lemma_ == 'be':
        new_form = 'were' if token.text.lower() == 'was' else 'was'
    else:
        new_form = None

    return new_form


class SubjectVerbAgreementWithSimpleNounErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_SIMPLE_NOUN.value

    def get_candidates(self, doc):
        return [t for t in doc if has_noun_subject(t) and not t.text.startswith("'")]

    def get_replacement(self, target, doc):
        return replace_verb(target, doc)


class SubjectVerbAgreementWithPronounErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_PRONOUN.value

    def get_candidates(self, doc):
        return [t for t in doc if has_pronoun_subject(t) and not has_relative_pronoun_subject(t) and not t.text.startswith("'")]

    def get_replacement(self, target, doc):
        return replace_verb(target, doc)


class SubjectVerbAgreementWithRelativePronounErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_RELATIVE_PRONOUN.value

    def get_candidates(self, doc):
        return [t for t in doc if has_relative_pronoun_subject(t) and not t.text.startswith("'")]

    def get_replacement(self, target, doc):
        return replace_verb(target, doc)


class SubjectVerbAgreementWithIndefinitePronounErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_INDEFINITE.value

    def get_candidates(self, doc):
        return [t for t in doc if has_indefinite_subject(t) and not t.text.startswith("'")]

    def get_replacement(self, target, doc):
        return replace_verb(target, doc)


class SubjectVerbAgreementWithInversionErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_INVERSION.value

    def get_candidates(self, doc):
        return [t for t in doc if t.tag_ in [Tag.PRESENT_SING3_VERB.value, Tag.PRESENT_OTHER_VERB.value, Tag.SIMPLE_PAST_VERB.value] and has_following_subject(t)]

    def get_replacement(self, target, doc):
        return replace_verb(target, doc)


class SubjectVerbAgreementWithNeitherNorErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_NEITHER_NOR.value

    def get_candidates(self, doc):
        return [t for t in doc if subject_has_neither(t)]

    def get_replacement(self, target, doc):
        return replace_verb(target, doc)


class SubjectVerbAgreementWithEitherOrErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_EITHER_OR.value

    def get_candidates(self, doc):
        return [t for t in doc if subject_has_either(t, doc)]

    def get_replacement(self, target, doc):
        return replace_verb(target, doc)


class IncorrectInfinitiveGenerator(ErrorGenerator):

    name = GrammarError.INCORRECT_INFINITIVE.value

    def get_candidates(self, doc):
        return [t for t in doc if t.tag_ == Tag.INFINITIVE.value]

    def get_replacement(self, target, doc):
        return replace_verb(target, doc)


class IncorrectInfinitiveIngGenerator(ErrorGenerator):

    name = GrammarError.INCORRECT_INFINITIVE_ING.value

    def get_candidates(self, doc):
        return [t for t in doc if t.tag_ == Tag.INFINITIVE.value]

    def get_replacement(self, target, doc):
        return target._.inflect(Tag.PRESENT_PARTICIPLE_VERB.value)


class IncorrectInfinitivePastGenerator(ErrorGenerator):

    name = GrammarError.INCORRECT_INFINITIVE_PAST.value

    def get_candidates(self, doc):
        return [t for t in doc if t.tag_ == Tag.INFINITIVE.value]

    def get_replacement(self, target, doc):
        if random.randint(0, 5) == 0:
            return target._.inflect(Tag.PAST_PARTICIPLE_VERB.value)
        return target._.inflect(Tag.SIMPLE_PAST_VERB.value)
