import string
import random

import lemminflect

from spacy.tokens.token import Token

from quillnlp.grammar.constants import GrammarError, Dependency, Tag
from quillnlp.grammar.myspacy import nlp
from quillnlp.grammar.generation import ErrorGenerator
from quillnlp.grammar.constants import GrammarError, Dependency, Tag, POS

PUNCTUATION = set(string.punctuation)
RELATIVE_PRONOUNS = set(['that', 'which', 'where', 'who', 'why', 'when', 'whose'])

def get_all_heads(doc, token, heads_so_far=[]):

    if token.head == token:
        return []

    return heads_so_far + [token.head] + get_all_heads(doc, token.head, heads_so_far)


def get_subject(verb: Token, full=False):
    """ Get the subject of a token. If full==False, only get the word that is labelled
    with the subject dependency. If full==True, get the full subject phrase."""

    # If the verb is the root, we can look up its subject in its left children
    # if verb.dep_ == Dependency.ROOT.value:

    for token in list(reversed(list(verb.lefts))) + list(verb.rights):
        if token.dep_ == Dependency.SUBJECT.value or \
                token.dep_ == Dependency.PASS_SUBJECT.value or \
                (verb.dep_ == Dependency.CCOMP.value and token.dep_ == Dependency.ATTRIBUTE.value):
            if full:
                return list(token.lefts) + [token]
            else:
                return token

        # cases like "There is a man in the room."
        elif token.dep_ == Dependency.EXPLETIVE.value or token.dep_ == Dependency.CLAUSAL_SUBJECT.value:
            for token2 in list(reversed(list(verb.lefts))) + list(verb.rights):
                if token2.dep_ == Dependency.ATTRIBUTE.value or \
                        token2.dep_ == Dependency.DIRECT_OBJECT.value:
                    if full:
                        return list(token2.lefts) + [token2]
                    else:
                        return token2

    # If we still haven't found anything, we return the attribute
    for token in list(reversed(list(verb.lefts))) + list(verb.rights):
        if token.dep_ == Dependency.ATTRIBUTE.value:
            if full:
                return list(token.lefts) + [token]
            else:
                return token

    # otherwise we have to look up the subject of its head.
    if verb.dep_ == Dependency.AUX.value or \
            verb.dep_ == Dependency.PASS_AUXILIARY.value or \
            verb.dep_ == Dependency.CONJUNCTION.value:
        return get_subject(verb.head, full=full)

    return None


def postprocess(text):
    text = text.strip()
    if len(text) == 0:
        return text

    # Uppercase the sentence if necessary.
    if text[0].islower():
        text = text[0].upper() + text[1:]

    # Add a full stop if necessary.
    if text[-1] not in PUNCTUATION:
        text += '.'

    # Introduce some questions in the set
    # if text[-1] == '.' and random.random() < 0.05:
    #     text = text[:-1] + '?'

    # Introduce some lowercased instances in the set
    # if text[0].isupper() and random.random() < 0.1:
    #     text = text[0].lower() + text[1:]

    return text


def is_unique_past_participle(token):
    """ Checks if the token is a past participle whose form is different
    from the past tense of the same verb.
    """
    return token.tag_ == Tag.PAST_PARTICIPLE_VERB.value and \
           token._.inflect(Tag.SIMPLE_PAST_VERB.value) != token._.inflect(Tag.PAST_PARTICIPLE_VERB.value)



class FragmentWithoutVerbGenerator(ErrorGenerator):

    name = GrammarError.FRAGMENT_NO_VERB.value

    def __init__(self):
        pass

    def generate_from_doc(self, doc, prompt=None, add_optimal=False):

        text = ""
        entities = []
        target_token = None

        for token in doc:
            if prompt is not None and token.idx < len(prompt):
                continue

            # A target token has to be a present or simple past verb
            # which is the root of the sentence,
            # has one or more tokens in its left dependency tree,
            # has a subject in its left dependency tree,
            # and has one or more tokens in its right dependency tree.
            if token.tag_ in [Tag.PRESENT_OTHER_VERB.value, Tag.PRESENT_SING3_VERB.value, Tag.SIMPLE_PAST_VERB.value] \
                    and token.head.dep_ == Dependency.ROOT.value and \
                    len(list(token.lefts)) > 0 and \
                    Dependency.SUBJECT.value in set([t.dep_ for t in token.lefts]) and \
                    len(list(token.rights)) > 0:
                target_token = token
                subject = [t for t in token.lefts if t.dep_ == Dependency.SUBJECT.value][0]
                break

        # If there is no target token, we cannot make a relevant fragment
        relevant = target_token is not None
        if not relevant:
            return doc.text, [], relevant

        previous_whitespace = ''
        for token in doc:
            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text
            elif token == target_token:
                previous_whitespace = token.whitespace_
                entity = (subject.idx, subject.idx+len(subject), self.name)
                if entity not in entities:
                    entities.append(entity)
                continue
            else:
                text += previous_whitespace + token.text
            previous_whitespace = token.whitespace_

        return postprocess(text), entities, relevant


class FragmentWithoutAuxiliaryGenerator(ErrorGenerator):

    name = GrammarError.FRAGMENT_NO_VERB.value

    def __init__(self):
        pass

    def generate_from_doc(self, doc, prompt=None, add_optimal=False):

        text = ""
        entities = []
        relevant = False

        previous_whitespace = ''
        for token in doc:
            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text

            # The target token must be an auxiliary
            # of the verb 'be',
            # whose head is the root of the sentence.
            # If its head is a past participle, this past participle form may not be
            # identical to the simple past form of the same verb. Otherwise deleting
            # the auxiliary 'be' will simply result in a simple past sentence
            # rather than a fragment.
            elif token.dep_.startswith('aux') \
                    and token.lemma_ == 'be' \
                    and token.head.dep_ == Dependency.ROOT.value \
                    and not token.dep_ == Dependency.ROOT.value \
                    and (token.head.tag_ != Tag.PAST_PARTICIPLE_VERB.value or is_unique_past_participle(token.head)) \
                    and not relevant:

                if token.head.idx < token.idx:
                    entity = (token.head.idx, token.head.idx+len(token.head), self.name)
                else:
                    removed_characters = len(token.text) + len(previous_whitespace)
                    entity = (token.head.idx-removed_characters, token.head.idx+len(token.head)-removed_characters, self.name)

                previous_whitespace = token.whitespace_
                relevant = True

                if entity not in entities:
                    entities.append(entity)

                continue
            else:
                text += previous_whitespace + token.text
            previous_whitespace = token.whitespace_

        return postprocess(text), entities, relevant


class FragmentWithoutVerbOrAuxGenerator(ErrorGenerator):

    name = GrammarError.FRAGMENT_NO_VERB.value

    def __init__(self):
        pass

    def generate_from_doc(self, doc, prompt=None, add_optimal=False):

        text = ""
        entities = []
        target_tokens = []

        for token in doc:
            if token.i == 0:
                continue

            if prompt is not None and token.idx < len(prompt):
                continue

            # A token is a target if it is a present or simple past form of a verb (except to be).
            if token.tag_ in [Tag.PRESENT_OTHER_VERB.value, Tag.PRESENT_SING3_VERB.value, Tag.SIMPLE_PAST_VERB.value] \
                    and token.lemma_ != 'have':
                target_tokens.append(token)
                break

        # If there is no target token, we cannot make a relevant fragment
        relevant = len(target_tokens) > 0
        if not relevant:
            return doc.text, [], relevant

        # Select a random target token and remove it
        target_token = random.choice(target_tokens)
        previous_whitespace = ''
        for token in doc:
            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text
            elif token == target_token:
                previous_whitespace = token.whitespace_
                entity = (doc[token.i-1].idx, doc[token.i-1].idx+len(doc[token.i-1]), self.name)
                if entity not in entities:
                    entities.append(entity)
                continue
            else:
                text += previous_whitespace + token.text
            previous_whitespace = token.whitespace_

        return postprocess(text), entities, relevant


class FragmentWithoutSubjectGenerator(ErrorGenerator):

    name = GrammarError.FRAGMENT_NO_SUBJ.value

    def __init__(self):
        pass

    def generate_from_doc(self, doc, prompt=None, add_optimal=False):

        text = ""
        entities = []
        relevant = False

        subjects_in_doc = []
        for token in doc:
            if prompt is not None and token.idx < len(prompt):
                continue
            if token.text.startswith("'"):
                continue

            # If the token is a verb, its subject is a candidate for removal.
            if token.pos_ == POS.VERB.value or token.pos_ == POS.AUX.value:
                subject = get_subject(token, full=True)
                if subject is not None:
                    subjects_in_doc.append((token, subject))

        if len(subjects_in_doc) == 0:
            return doc.text, [], relevant

        # Choose a random subject to remove
        verb, subject_to_remove = random.choice(subjects_in_doc)

        # Remove the subject.
        previous_whitespace = ''
        for token in doc:
            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text
            elif token in subject_to_remove:
                previous_whitespace = token.whitespace_
                relevant = True
                continue
            else:
                text += previous_whitespace + token.text
            previous_whitespace = token.whitespace_

        text = text.strip()

        if verb.idx < subject_to_remove[0].idx:
            entity = (verb.idx, verb.idx+len(verb), self.name)
        else:
            removed_characters = len(doc.text) - len(text)
            entity = (verb.idx-removed_characters, verb.idx+len(verb)-removed_characters, self.name)
        entities.append(entity)

        return postprocess(text), entities, relevant
