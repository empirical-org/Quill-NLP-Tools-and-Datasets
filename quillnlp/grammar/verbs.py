import random

import spacy
import pyinflect

from quillnlp.grammar.constants import Dependency, Tag, POS, TokenSet

nlp = spacy.load("en")


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


def is_present(verb):
    if is_future(verb):
        return False
    return verb.tag_ == Tag.PRESENT_OTHER_VERB.value or Tag.PRESENT_SING3_VERB.value


def create_regular_simple_past(verb):
    new_token = verb.lemma_ + "d" if verb.lemma_.endswith("e") else verb.lemma_ + "ed"
    return new_token


def get_subject(verb):

    # If the verb is the root, we can look up its subject in its left children
    if verb.dep_ == Dependency.ROOT.value:
        for token in verb.lefts:
            if token.dep_ == Dependency.SUBJECT.value or \
                    token.dep_ == Dependency.PASS_SUBJECT.value:
                return token

    # otherwise we have to look up the subject of its head.
    elif verb.dep_ == Dependency.AUX.value or verb.dep_ == Dependency.PASS_AUXILIARY.value:
        return get_subject(verb.head)

    return None


def get_plural(verb):
    if verb.lemma_ == "be":
        return "are"
    else:
        return verb._.inflect(Tag.INFINITIVE.value)


def is_indefinite(noun):
    return noun.left_edge.text.lower() in TokenSet.INDEF_ARTICLES.value


# Synthetic functions

def remove_be_from_passive(sentence):
    """ Removes the passive auxiliary 'be' from a sentence. """
    doc = nlp(sentence)

    new_sentence = ""
    for token in doc:
        if not (token.dep_ == Dependency.PASS_AUXILIARY.value and token.lemma_ == "be"):
            new_sentence += token.text_with_ws

    return new_sentence


def replace_past_participle_by_simple_past(sentence):
    """ Replaces the past participle (e.g. forgotten) by its past tense (e.g. forgot) """

    doc = nlp(sentence)

    new_sentence = ""
    for token in doc:
        if token.tag_ == Tag.PAST_PARTICIPLE_VERB.value:
            new_sentence += token._.inflect(Tag.SIMPLE_PAST_VERB.value) + token.whitespace_
        else:
            new_sentence += token.text_with_ws

    return new_sentence


def replace_past_participle_by_incorrect_simple_past(sentence):
    """ Replaces the past participle (e.g. forgotten) by its past tense (e.g. forgot) """

    doc = nlp(sentence)

    new_sentence = ""
    for token in doc:
        if token.tag_ == Tag.PAST_PARTICIPLE_VERB.value:
            new_sentence += create_regular_simple_past(token) + token.whitespace_
        else:
            new_sentence += token.text_with_ws

    return new_sentence


def remove_have_from_perfect_progressive(sentence):

    doc = nlp(sentence)

    new_sentence = ""
    for token in doc:
        if not (token.dep_ == Dependency.AUX.value and
                token.lemma_ == "have" and
                token.head.tag_ == Tag.PRESENT_PARTICIPLE_VERB.value):
            new_sentence += token.text_with_ws

    return new_sentence


def remove_have_from_perfect(sentence):

    doc = nlp(sentence)

    new_sentence = ""
    for token in doc:
        if not (token.dep_ == Dependency.AUX.value and
                token.lemma_ == "have" and
                token.head.tag_ == Tag.PAST_PARTICIPLE_VERB.value):
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


def change_tense_in_subclause(sentence):

    def have_same_tense(verb1, verb2):
        if is_past(verb1) and is_past(verb2):
            return True
        elif is_present(verb1) and is_present(verb2):
            return True
        else:
            return False

    doc = nlp(sentence)
    new_sentence = ""
    for token in doc:
        if token.dep_ == Dependency.ADVERBIAL_CLAUSE.value and have_same_tense(token, token.head):

            if token.tag_ == Tag.SIMPLE_PAST_VERB.value:
                new_token = token._.inflect(Tag.PRESENT_SING3_VERB.value)
            elif token.tag_ == Tag.PRESENT_SING3_VERB.value:
                new_token = token._.inflect(Tag.SIMPLE_PAST_VERB.value)
            elif token.tag_ == Tag.PRESENT_OTHER_VERB.value:
                new_token == token._.inflect(Tag.SIMPLE_PAST_VERB.value)
            else:
                new_token = token.text

            new_sentence += new_token + token.whitespace_
        else:
            new_sentence += token.text_with_ws

    return new_sentence


def insert_future_in_subclause(sentence):

    doc = nlp(sentence)

    new_sentence = ""
    for token in doc:
        if token.dep_ == Dependency.ADVERBIAL_CLAUSE.value and is_present(token) and is_future(token.head):
            new_sentence += "will "
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


def replace_3rd_person_verb_by_infinitive(sentence):

    doc = nlp(sentence)

    new_sentence = ""
    for token in doc:
        if token.tag_ == Tag.PRESENT_SING3_VERB.value:
            new_sentence += token.lemma_ + token.whitespace_
        else:
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


def replace_singular_by_plural_after_collective(sentence):

    doc = nlp(sentence)

    new_sentence = ""
    for token in doc:
        if token.tag_ == Tag.PRESENT_SING3_VERB.value:
            subject = get_subject(token)
            if subject is not None and subject.text.lower() in TokenSet.COLLECTIVE_NOUNS.value:
                new_sentence += get_plural(token) + token.whitespace_
            else:
                new_sentence += token.text_with_ws
        else:
            new_sentence += token.text_with_ws

    return new_sentence


def replace_singular_by_plural_after_indefinite(sentence):
    doc = nlp(sentence)
    new_sentence = ""

    for token in doc:
        if token.tag_ == Tag.PRESENT_SING3_VERB.value:
            subject = get_subject(token)
            if subject is not None and is_indefinite(subject):
                new_sentence += get_plural(token) + token.whitespace_
            else:
                new_sentence += token.text_with_ws
        else:
            new_sentence += token.text_with_ws

    return new_sentence


def swap_forms_of_be(sentence):

    doc = nlp(sentence)

    new_sentence = ""
    for token in doc:
        if token.dep_ == Dependency.PASS_AUXILIARY and token.text.lower() in TokenSet.MUTUALLY_EXCLUSIVE_BE_FORMS.value:
            other_forms_of_be = list(TokenSet.MUTUALLY_EXCLUSIVE_BE_FORMS.value - set([token.lemma_]))
            new_sentence += random.choice(other_forms_of_be) + token.whitespace_
        else:
            new_sentence += token.text_with_ws

    return new_sentence
