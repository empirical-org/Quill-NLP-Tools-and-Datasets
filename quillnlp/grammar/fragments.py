import string
import random

import lemminflect

from quillgrammar.grammar.constants import GrammarError, Dependency, Tag
from quillnlp.grammar.myspacy import nlp
from quillnlp.grammar.generation import ErrorGenerator
from quillgrammar.grammar.constants import GrammarError, Dependency, Tag, POS

PUNCTUATION = set(string.punctuation)
RELATIVE_PRONOUNS = set(['that', 'which', 'where', 'who', 'why', 'when', 'whose'])


def get_all_heads(doc, token, heads_so_far=[]):

    if token.head == token:
        return []

    return heads_so_far + [token.head] + get_all_heads(doc, token.head, heads_so_far)


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
    if text[-1] == '.' and random.random() < 0.05:
        text = text[:-1] + '?'

    # Introduce some lowercased instances in the set
    if text[0].isupper() and random.random() < 0.1:
        text = text[0].lower() + text[1:]

    return text


def is_unique_past_participle(token):
    """ Checks if the token is a past participle whose form is different
    from the past tense of the same verb.
    """
    return token.tag_ == Tag.PAST_PARTICIPLE_VERB.value and \
           token._.inflect(Tag.SIMPLE_PAST_VERB.value) != token._.inflect(Tag.PAST_PARTICIPLE_VERB.value)



class FragmentWithoutVerbGenerator(ErrorGenerator):

    def __init__(self):
        pass

    def generate_from_doc(self, doc, prompt=None):

        text = ""
        entities = []
        target_token = None

        for token in doc:
            if token.pos_ == POS.VERB.value \
                    and token.head.dep_ == Dependency.ROOT.value and \
                    len(list(token.lefts)) > 0 and \
                    Dependency.SUBJECT.value in set([t.dep_ for t in token.lefts]) and \
                    len(list(token.rights)) > 0:
                target_token = token
                break

        # If there is no target token, we cannot make a relevant fragment
        relevant = target_token is not None
        if not relevant:
            return doc.text, [], relevant

        previous_whitespace = ''
        for token in doc:
            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text
            elif token == target_token or \
                    (token.pos_ in [POS.VERB.value, POS.AUX.value] and token.head == target_token):
                previous_whitespace = token.whitespace_
                continue
            else:
                text += previous_whitespace + token.text
            previous_whitespace = token.whitespace_

        return postprocess(text), entities, relevant


class FragmentWithoutAuxiliaryGenerator(ErrorGenerator):

    def __init__(self):
        pass

    def generate_from_doc(self, doc, prompt=None):

        text = ""
        entities = []
        relevant = False

        previous_whitespace = ''
        for token in doc:
            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text
            elif (token.pos_ == POS.AUX.value) \
                    and token.lemma_ == 'be' \
                    and token.head.dep_ == Dependency.ROOT.value \
                    and not token.dep_ == Dependency.ROOT.value \
                    and (token.head.dep_ != Tag.PAST_PARTICIPLE_VERB.value or is_unique_past_participle(token.head)) \
                    and not relevant:
                previous_whitespace = token.whitespace_
                relevant = True
                continue
            else:
                text += previous_whitespace + token.text
            previous_whitespace = token.whitespace_

        return postprocess(text), entities, relevant


class FragmentWithoutSubjectGenerator(ErrorGenerator):

    def __init__(self):
        pass

    def generate_from_doc(self, doc, prompt=None):

        text = ""
        entities = []
        relevant = False

        previous_whitespace = ''
        for token in doc:
            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text
            elif token.dep_ == Dependency.SUBJECT.value or token.dep_ == Dependency.PASS_SUBJECT.value:
                previous_whitespace = token.whitespace_
                relevant = True
                continue
            elif token.head.dep_ == Dependency.SUBJECT.value or token.head.dep_ == Dependency.PASS_SUBJECT.value:
                previous_whitespace = token.whitespace_
                relevant = True
                continue
            else:
                text += previous_whitespace + token.text
            previous_whitespace = token.whitespace_

        return postprocess(text), entities, relevant


class VerbPhraseFragmentGenerator(ErrorGenerator):

    def is_target_token(self, token):
        return token.tag_ == Tag.PRESENT_PARTICIPLE_VERB.value or \
               is_unique_past_participle(token)

    def generate_from_doc(self, doc, prompt=None):

        text = ""
        entities = []

        # Identify a target outside of the prompt
        target_token = None
        for token in doc:
            if (prompt is None or token.idx >= len(prompt)) and self.is_target_token(token):
                target_token = token
                break

        # If there is no target token, we cannot make a relevant fragment
        relevant = target_token is not None
        if not relevant:
            return doc.text, [], relevant

        # token in target_token.rights: catches 'trees' in 'we are growing trees'
        # target_token in token.lefts: catches 'robbed' in 'we have been robbed'
        # set(get_all_heads(doc, token)).intersection(target_token.rights): catches 'the' in 'we have cleaned the car'

        previous_whitespace = ''
        for token in doc:
            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text
            elif token == target_token or \
                    token in target_token.rights or \
                    target_token in token.lefts or \
                    set(get_all_heads(doc, token)).intersection(target_token.rights):

                text += previous_whitespace + token.text
                previous_whitespace = token.whitespace_
                continue
            else:
                previous_whitespace = token.whitespace_
                continue
            previous_whitespace = token.whitespace_

        return postprocess(text), entities, relevant


class KeeperFragmentFragmentGenerator(ErrorGenerator):

    def __init__(self, dependency_to_keep, tag=None, exclude_tags=[]):
        self.dependency_to_keep = dependency_to_keep
        self.tag = tag
        self.exclude_tags = exclude_tags

    def is_target_token(self, token):
        return token.dep_ == self.dependency_to_keep and \
               (self.tag is None or self.tag == token.tag_) and \
               token.tag_ not in self.exclude_tags

    def generate_from_doc(self, doc, prompt=None):

        text = ""
        entities = []

        # Identify a target word outside of the prompt
        target_token = None
        for token in doc:
            if (prompt is None or token.idx >= len(prompt)) and self.is_target_token(token):
                target_token = token
                break

        # If there is no target word, we cannot make a relevant fragment
        relevant = target_token is not None
        if not relevant:
            return doc.text, [], relevant

        # If there is a target word, we only keep the words in that have it as one of their heads
        previous_whitespace = ''
        for token in doc:

            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text
            elif token == target_token or target_token in get_all_heads(doc, token):
                text += previous_whitespace + token.text
                previous_whitespace = token.whitespace_
                continue
            else:
                previous_whitespace = token.whitespace_
                continue
            previous_whitespace = token.whitespace_

        return postprocess(text), entities, relevant


prepositionalPhraseFragmentGenerator = KeeperFragmentFragmentGenerator('prep')


class InfinitiveFragmentGenerator(ErrorGenerator):

    def is_target_token(self, token):
        return token.dep_ == 'xcomp' and \
               token.tag_ == 'VB'

    def generate_from_doc(self, doc, prompt=None):

        text = ""
        entities = []

        # Identify a target word outside of the prompt
        target_token = None
        for token in doc:
            previous_token = doc[token.i - 1] if token.i > 0 else None
            if (prompt is None or token.idx >= len(prompt)) and self.is_target_token(token) and \
                    previous_token is not None and previous_token.text.lower() == 'to':
                target_token = token
                break

        # If there is no target word, we cannot make a relevant fragment
        relevant = target_token is not None
        if not relevant:
            return doc.text, [], relevant

        # If there is a target word, we only keep the words in that have it as one of their heads
        previous_whitespace = ''
        for token in doc:

            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text
            elif token == target_token or target_token in get_all_heads(doc, token):
                text += previous_whitespace + token.text
                previous_whitespace = token.whitespace_
                continue
            else:
                previous_whitespace = token.whitespace_
                continue
            previous_whitespace = token.whitespace_

        return postprocess(text), entities, relevant


class NounPhraseFragmentGenerator(ErrorGenerator):

    def is_target_token(self, token):
        return token.dep_ == Dependency.DIRECT_OBJECT.value

    def generate_from_doc(self, doc, prompt=None):

        text = ""
        entities = []

        # Identify a target word outside of the prompt
        target_token = None
        for token in doc:
            if (prompt is None or token.idx >= len(prompt)) and self.is_target_token(token):
                target_token = token
                break

        # If there is no target word, we cannot make a relevant fragment
        relevant = target_token is not None
        if not relevant:
            return doc.text, [], relevant

        # If there is a target word, we only keep the words in that have it as one of their heads
        previous_whitespace = ''
        for token in doc:

            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text
            elif token == target_token or target_token in get_all_heads(doc, token):
                text += previous_whitespace + token.text
                previous_whitespace = token.whitespace_
                continue
            else:
                previous_whitespace = token.whitespace_
                continue
            previous_whitespace = token.whitespace_

        return postprocess(text), entities, relevant


class RelativeClauseFragmentGenerator(ErrorGenerator):

    def is_target_token(self, token):
        return token.dep_ == 'relcl' and \
               token.tag_ not in ['VB']

    def generate_from_doc(self, doc, prompt=None):

        text = ""
        entities = []

        # Identify a target word outside of the prompt
        target_token = None
        for token in doc:
            if (prompt is None or token.idx >= len(prompt)) and self.is_target_token(token):
                target_token = token
                break

        # If there is no target word, we cannot make a relevant fragment
        relevant = target_token is not None
        if not relevant:
            return doc.text, [], relevant

        # If there is a target word, we only keep the words in that have it as one of their heads
        previous_whitespace = ''
        for token in doc:

            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text
            elif token == target_token or target_token in get_all_heads(doc, token):
                text += previous_whitespace + token.text
                previous_whitespace = token.whitespace_
                continue
            else:
                previous_whitespace = token.whitespace_
                continue
            previous_whitespace = token.whitespace_

        if text.split()[0].lower() not in RELATIVE_PRONOUNS:
            return doc.text, [], False

        return postprocess(text), entities, relevant


class DependentClauseFragmentGenerator(ErrorGenerator):

    def generate_from_doc(self, doc, prompt=None):

        text = ""
        entities = []

        # Identify a target word outside of the prompt
        target_token = None
        for token in doc:
            if (prompt is None or token.idx >= len(prompt)) and \
                (token.dep_ == 'advmod' or token.dep_ == 'mark') and \
                not token.pos_ == POS.ADVERB.value and \
                token.head.pos_ == POS.VERB.value and \
                token.head.i > token.i and \
                token.text.lower() != 'that' and token.text.lower() != 'to' and \
                not token.head.tag_ == Tag.INFINITIVE.value:
                    target_token = token.head
                    break

        # If there is no target word, we cannot make a relevant fragment
        relevant = target_token is not None
        if not relevant:
            return doc.text, [], relevant

        # If there is a target word, we only keep the words in that have it as one of their heads
        previous_whitespace = ''
        for token in doc:

            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text
            elif token == target_token or target_token in get_all_heads(doc, token):
                text += previous_whitespace + token.text
                previous_whitespace = token.whitespace_
                continue
            else:
                previous_whitespace = token.whitespace_
                continue
            previous_whitespace = token.whitespace_

        return postprocess(text), entities, relevant

class MissingObjectFragmentGenerator(ErrorGenerator):

    def __init__(self, transitives):
        self.transitive_verbs = transitives
        pass

    def remove_full_object(self, prompt, doc, target_token):
        text = ""
        entities = []
        previous_whitespace = ''
        for token in doc:
            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text
            elif token == target_token or target_token in get_all_heads(doc, token):
                previous_whitespace = token.whitespace_
                continue
            else:
                text += previous_whitespace + token.text
            previous_whitespace = token.whitespace_
        return text, entities

    def remove_part_of_object(self, prompt, doc, target_token):
        text = ""
        entities = []
        previous_whitespace = ''
        for token in doc:
            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text
            elif token == target_token:
                previous_whitespace = token.whitespace_
                continue
            else:
                text += previous_whitespace + token.text
            previous_whitespace = token.whitespace_
        return text, entities

    def generate_from_doc(self, doc, prompt=None):

        # Identify a direct object outside of the prompt
        target_token = None
        for token in doc:
            if (prompt is None or token.idx >= len(prompt)) and token.dep_ == 'dobj':
                target_token = token
                break

        # If there is no direct object, we cannot make a relevant fragment
        relevant = target_token is not None
        if not relevant:
            return doc.text, [], relevant

        random_number = random.random()
        if target_token.head.lemma_ in self.transitive_verbs and random_number < 0.5:
            text, entities = self.remove_full_object(prompt, doc, target_token)
        else:
            text, entities = self.remove_part_of_object(prompt, doc, target_token)


        return postprocess(text), entities, relevant
