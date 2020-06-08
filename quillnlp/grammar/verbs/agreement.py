import random

from spacy.gold import biluo_tags_from_offsets
from spacy.tokens.token import Token
from spacy.tokens.span import Span


from quillnlp.grammar.constants import Tag, GrammarError, Dependency, POS, TokenSet
from quillnlp.grammar.generation import ErrorGenerator
from quillnlp.grammar.verbutils import get_subject, get_plural, is_indefinite

import spacy
nlp = spacy.load("en")


def is_subject(token: Token):
    return token.dep_ == Dependency.SUBJECT.value or token.dep_ == Dependency.PASS_SUBJECT.value


def is_negated_with_contraction(token, sentence):
    if len(sentence) > token.i+1 and sentence[token.i+1].text == "n't":
        return True
    return False


def has_noun_subject(token: Token):
    for t in token.lefts:
        if (t.dep_ == Dependency.PASS_SUBJECT.value or t.dep_ == Dependency.SUBJECT.value) \
                and (t.pos_ == POS.NOUN.value or t.pos_ == POS.PROPER_NOUN.value):
            return True
    return False


def has_pronoun_subject(token: Token):
    for t in token.lefts:
        if (t.dep_ == Dependency.PASS_SUBJECT.value or t.dep_ == Dependency.SUBJECT.value) \
                and t.pos_ == POS.PRONOUN.value:
            return True
    return False


def subject_has_neither(verb: Token):
    subject = get_subject(verb)

    if subject is None:
        return False

    for token in subject.lefts:
        if token.text.lower() == "neither":
            return True
    return False


def subject_has_either(verb: Token, sentence: Span):
    # For some reason spaCy analyzes "either or" differently than "neither nor"
    subject = get_subject(verb)

    if subject is None:
        return False

    right_tokens = list(subject.rights)
    if len(right_tokens) > 0 and right_tokens[0].text == "or" and "either" in sentence.text.lower()[:subject.idx]:
        return True
    return False


def has_following_subject(verb: Token):
    """ Returns True if the verb's subject comes after it in the sentence,
    and false otherwise. """
    subject = get_subject(verb)
    if subject is not None and subject.idx > verb.idx:
        return True
    return False


class SubjectVerbAgreementWithSimpleNounErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_SIMPLE_NOUN.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif has_noun_subject(token) and not is_negated_with_contraction(token, doc):

                # singular -> plural
                if token.tag_ == Tag.PRESENT_SING3_VERB.value:
                    if token.lemma_ == "be":
                        new_form = random.choice(["be", "are", "am"])
                        new_form = new_form.title() if token.text.istitle() else new_form
                    else:
                        new_form = token.lemma_
                        new_form = new_form.title() if token.text.istitle() else new_form

                    new_sentence += new_form + token.whitespace_
                    entities.append((token.idx, token.idx+len(new_form), self.name))

                # plural -> singular
                elif token.tag_ == Tag.PRESENT_OTHER_VERB.value:
                    if token.lemma_ == "be":
                        new_form = random.choice(["be", "is", "am"])
                        new_form = new_form.title() if token.text.istitle() else new_form
                    else:
                        new_form = token._.inflect(Tag.PRESENT_SING3_VERB.value)

                    if new_form is not None:
                        new_sentence += new_form + token.whitespace_
                        entities.append((token.idx, token.idx+len(new_form), self.name))
                    else:
                        new_sentence += token.text_with_ws
                else:
                    new_sentence += token.text_with_ws
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class SubjectVerbAgreementWithPronounErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_PRONOUN.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws

            elif has_pronoun_subject(token) and not is_negated_with_contraction(token, doc):

                # third-person singular -> other form
                if token.tag_ == Tag.PRESENT_SING3_VERB.value:
                    if token.lemma_ == "be":
                        new_form = random.choice(["be", "are", "am"])
                    else:
                        new_form = token.lemma_
                    new_sentence += new_form + token.whitespace_
                    entities.append((token.idx, token.idx+len(new_form), self.name))

                # other form -> third-person form
                elif token.tag_ == Tag.PRESENT_OTHER_VERB.value:
                    if token.lemma_ == "be":
                        other_forms = set(["be", "are", "am", "is"]) - set(token.text.lower())
                        new_form = random.choice(list(other_forms))
                        new_form = new_form.title() if token.text.istitle() else new_form
                        new_sentence += new_form + token.whitespace_
                        entities.append((token.idx, token.idx + len(new_form), self.name))
                    else:
                        new_form = token._.inflect(Tag.PRESENT_SING3_VERB.value)
                        if new_form is not None:
                            new_sentence += new_form + token.whitespace_
                            entities.append((token.idx, token.idx + len(new_form), self.name))
                        else:
                            new_sentence += token.text_with_ws
                else:
                    new_sentence += token.text_with_ws
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class IncorrectThirdPersonWithNegationErrorGenerator(ErrorGenerator):

    name = GrammarError.VERB_INCORRECT_NEGATIVE_WITH_SIMPLE_NOUN.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif token.tag_ == Tag.PRESENT_SING3_VERB.value and \
                    is_negated_with_contraction(token, doc) and \
                    has_noun_subject(token):
                new_form = token.lemma_ if token.lemma_ != "be" else "are"
                new_form = new_form.title() if token.text.istitle() else new_form
                new_sentence += new_form + token.whitespace_
                entities.append((token.idx, token.idx+len(new_form), self.name))
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class SubjectVerbAgreementWithInversionErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_INVERSION.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif (token.tag_ == Tag.PRESENT_SING3_VERB.value or token.tag_ == Tag.PRESENT_OTHER_VERB.value) and \
                    has_following_subject(token):
                # third-person singular -> other form
                if token.tag_ == Tag.PRESENT_SING3_VERB.value:
                    if token.lemma_ == "be":
                        new_form = random.choice(["be", "are", "am"])
                        new_form = new_form.title() if token.text.istitle() else new_form
                    else:
                        new_form = token.lemma_
                        new_form = new_form.title() if token.text.istitle() else new_form
                    new_sentence += new_form + token.whitespace_

                # other form -> third-person form
                elif token.tag_ == Tag.PRESENT_OTHER_VERB.value:
                    if token.lemma_ == "be":
                        other_forms = set(["be", "are", "am", "is"]) - set(token.text.lower())
                        new_form = random.choice(list(other_forms))
                        new_form = new_form.title() if token.text.istitle() else new_form
                        new_sentence += new_form + token.whitespace_
                        entities.append((token.idx, token.idx + len(new_form), self.name))
                    else:
                        new_form = token._.inflect(Tag.PRESENT_SING3_VERB.value)
                        if new_form is not None:
                            new_sentence += new_form + token.whitespace_
                            entities.append((token.idx, token.idx + len(new_form), self.name))
                        else:
                            new_sentence += token.text_with_ws
                else:
                    new_sentence += token.text_with_ws
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class SubjectVerbAgreementWithNeitherNorErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_NEITHER_NOR.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif token.tag_ == Tag.PRESENT_SING3_VERB.value and subject_has_neither(token):
                new_form = token.lemma_ if token.lemma_ != "be" else "are"
                new_sentence += new_form + token.whitespace_
                entities.append((token.idx, token.idx+len(new_form), self.name))
            elif token.tag_ == Tag.PRESENT_OTHER_VERB.value and subject_has_neither(token):
                new_form = token._.inflect(Tag.PRESENT_SING3_VERB.value)
                new_sentence += new_form + token.whitespace_
                entities.append((token.idx, token.idx + len(new_form), self.name))
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class SubjectVerbAgreementWithEitherOrErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_EITHER_OR.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif token.tag_ == Tag.PRESENT_SING3_VERB.value and subject_has_either(token, doc):
                new_form = token.lemma_ if token.lemma_ != "be" else "are"
                new_sentence += new_form + token.whitespace_
                entities.append((token.idx, token.idx+len(new_form), self.name))
            elif token.tag_ == Tag.PRESENT_OTHER_VERB.value and subject_has_either(token, doc):
                new_form = token._.inflect(Tag.PRESENT_SING3_VERB.value)
                new_sentence += new_form + token.whitespace_
                entities.append((token.idx, token.idx + len(new_form), self.name))
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class SubjectVerbAgreementWithCollectiveNoun(ErrorGenerator):

    name = GrammarError.SVA_COLLECTIVE_NOUN.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if token.tag_ == Tag.PRESENT_SING3_VERB.value:
                subject = get_subject(token)
                if subject is not None and subject.text.lower() in TokenSet.COLLECTIVE_NOUNS.value:
                    plural = get_plural(token)
                    new_sentence += plural + token.whitespace_
                    entities.append((token.idx, token.idx + len(plural), self.name))
                else:
                    new_sentence += token.text_with_ws
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class SubjectVerbAgreementWithIndefinitePronoun(ErrorGenerator):

    name = GrammarError.SVA_INDEFINITE.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []

        for token in doc:
            if token.tag_ == Tag.PRESENT_SING3_VERB.value:
                subject = get_subject(token)
                if subject is not None and is_indefinite(subject):
                    plural = get_plural(token)
                    new_sentence += plural + token.whitespace_
                    entities.append((token.idx, token.idx + len(plural), self.name))
                else:
                    new_sentence += token.text_with_ws
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities