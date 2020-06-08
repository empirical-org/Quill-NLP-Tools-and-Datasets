import random
import re

import spacy
import pyinflect
from spacy.gold import biluo_tags_from_offsets

from spacy.tokens.token import Token

from quillnlp.grammar.constants import Dependency, Tag, POS, TokenSet, GrammarError
from quillnlp.grammar.verbs.passive import is_passive

nlp = spacy.load("en")

#Token.set_extension("replace", default=None)

# Auxiliary verb functions:


def is_past(verb):
    return verb.tag_ == Tag.SIMPLE_PAST_VERB.value


def is_future(verb):
    for child in verb.lefts:
        if child.lemma_ == "will" and \
                child.dep_ == Dependency.AUX.value and \
                child.tag_ == Tag.MODAL_VERB.value:
            return True
    return False


def is_past_perfect(verb):
    if not verb.tag_ == Tag.PAST_PARTICIPLE_VERB.value:
        return False

    for child in verb.lefts:
        if child.lemma_ == "have" and \
                child.dep_ == Dependency.AUX.value and \
                child.tag_ == Tag.SIMPLE_PAST_VERB.value:
            return True
    return False


def is_present(verb: Token):
    """ Determines if a verb form is present. """
    if is_future(verb):
        return False
    return verb.tag_ == Tag.PRESENT_OTHER_VERB.value or Tag.PRESENT_SING3_VERB.value


def create_regular_simple_past(verb):

    # TODO: doubling of consonants: run -> runned
    new_token = verb.lemma_ + "d" if verb.lemma_.endswith("e") else verb.lemma_ + "ed"
    return new_token


def get_subject(verb: Token):

    # If the verb is the root, we can look up its subject in its left children
    #if verb.dep_ == Dependency.ROOT.value:
    for token in verb.lefts:
        if token.dep_ == Dependency.SUBJECT.value or \
                token.dep_ == Dependency.PASS_SUBJECT.value:
            return token

    # otherwise we have to look up the subject of its head.
    if verb.dep_ == Dependency.AUX.value or verb.dep_ == Dependency.PASS_AUXILIARY.value:
        return get_subject(verb.head)

    return None


def get_plural(verb: Token):
    """ Finds the plural form of a verb token. """
    if verb.lemma_ == "be":
        return "are"
    else:
        return verb._.inflect(Tag.INFINITIVE.value)


def is_indefinite(noun: Token):
    """ Determines if a noun token is indefinite or not. """
    return noun.left_edge.text.lower() in TokenSet.INDEF_PRONOUNS.value


def get_past_tenses(token: Token):
    """
    This fixes a few problems with pyinflect, such as the fact that it
    only returns "was" as the past tense of "were".

    Args:
        token:

    Returns:

    """

    PAST_TENSE_MAP = {"be": set(["was", "were"]),
                      "quit": set(["quit"])}

    if token.lemma_.lower() in PAST_TENSE_MAP:
        return PAST_TENSE_MAP[token.lemma_.lower()]
    else:
        past_tense = token._.inflect(Tag.SIMPLE_PAST_VERB.value)
        if past_tense is None:
            return set()
        else:
            return set([past_tense.lower()])

# Synthetic functions


def remove_have_from_perfect_progressive(sentence):

    doc = nlp(sentence)

    new_sentence = ""
    for token in doc:
        if not (token.dep_ == Dependency.AUX.value and
                token.lemma_ == "have" and
                token.head.tag_ == Tag.PRESENT_PARTICIPLE_VERB.value):
            new_sentence += token.text_with_ws

    return new_sentence


def create_incorrect_irregular_past_tense(sentence):

    doc = nlp(sentence)

    new_sentence = ""
    for token in doc:
        if token.tag_ == Tag.SIMPLE_PAST_VERB.value:
            new_token = create_regular_simple_past(token)
            new_sentence += new_token + token.whitespace_
        else:
            new_sentence += token.text_with_ws

    return new_sentence


class VerbShiftErrorGenerator:

    name = GrammarError.VERB_SHIFT.value

    def generate(self, sentence):

        def have_same_tense(verb1, verb2):
            if verb1 is None or verb2 is None:
                return False
            elif is_past(verb1) and is_past(verb2):
                return True
            elif is_present(verb1) and is_present(verb2):
                return True
            else:
                return False

        doc = nlp(sentence)
        new_sentence = ""
        for token in doc:
            if token.dep_ == Dependency.ADVERBIAL_CLAUSE.value and \
                    is_present(token) and \
                    have_same_tense(token, token.head):

                # The problem with past->present is that we need the person of the verb
                #if token.tag_ == Tag.SIMPLE_PAST_VERB.value:
                #    new_token = token._.inflect(Tag.PRESENT_SING3_VERB.value)
                if token.tag_ == Tag.PRESENT_SING3_VERB.value:
                    new_token = token._.inflect(Tag.SIMPLE_PAST_VERB.value)
                elif token.tag_ == Tag.PRESENT_OTHER_VERB.value:
                    new_token = token._.inflect(Tag.SIMPLE_PAST_VERB.value)
                else:
                    new_token = token.text

                # Insert a space to deal with contractions, otherwise "what's" -> "whatwas"
                if len(new_sentence) > 0 and not new_sentence[-1].isspace():
                    new_sentence += " "
                new_sentence += new_token + token.whitespace_
            else:
                new_sentence += token.text_with_ws

        return new_sentence


class FutureInSubclauseErrorGenerator():

    name = GrammarError.FUTURE_IN_SUBCLAUSE

    def generate(self, sentence):

        doc = nlp(sentence)

        new_sentence = ""
        for token in doc:
            if token.dep_ == Dependency.ADVERBIAL_CLAUSE.value and is_present(token) and is_future(token.head):
                infinitive = token._.inflect(Tag.INFINITIVE.value)
                if infinitive is not None:
                    new_sentence += "will " + infinitive + token.whitespace_
                else:
                    new_sentence += token.text_with_ws
            else:
                new_sentence += token.text_with_ws

        return new_sentence


def replace_past_simple_with_past_perfect(sentence):

    doc = nlp(sentence)
    new_sentence = ""

    for token in doc:
        if token.dep_ == Dependency.ADVERBIAL_CLAUSE.value and is_past(token) and is_past_perfect(token.head):
            new_sentence += "had "
        new_sentence += token.text_with_ws

    return new_sentence


def swap_3rd_and_other_person_verb_form_after_pronoun(sentence):

    doc = nlp(sentence)

    new_sentence = ""
    for token in doc:
        if token.left_edge.pos_ == POS.PRONOUN.value and token.tag_ == Tag.PRESENT_SING3_VERB.value:
            new_sentence += token._.inflect(Tag.PRESENT_OTHER_VERB.value) + token.whitespace_
        elif token.left_edge.pos_ == POS.PRONOUN.value and token.tag_ == Tag.PRESENT_OTHER_VERB.value:
                new_sentence += token._.inflect(Tag.PRESENT_SING3_VERB.value) + token.whitespace_
        else:
            new_sentence += token.text_with_ws

    return new_sentence





