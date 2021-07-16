import string

from quillgrammar.grammar.constants import GrammarError, Dependency, Tag
from quillnlp.grammar.myspacy import nlp
from quillnlp.grammar.generation import ErrorGenerator
from quillgrammar.grammar.constants import GrammarError, Dependency, Tag, POS

PUNCTUATION = set(string.punctuation)


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

    return text


class FragmentWithoutVerbGenerator(ErrorGenerator):

    def __init__(self):
        pass

    def generate_from_doc(self, doc, prompt=None):

        text = ""
        entities = []
        relevant = True

        previous_whitespace = ''
        for token in doc:
            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text
            elif (token.pos_ == POS.VERB.value or token.pos_ == POS.AUX.value) \
                    and token.head.dep_ == Dependency.ROOT.value:
                previous_whitespace = token.whitespace_
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
        relevant = True

        previous_whitespace = ''
        for token in doc:
            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text
            elif token.dep_ == Dependency.SUBJECT.value or token.dep_ == Dependency.PASS_SUBJECT.value:
                previous_whitespace = token.whitespace_
                continue
            elif token.head.dep_ == Dependency.SUBJECT.value or token.head.dep_ == Dependency.PASS_SUBJECT.value:
                previous_whitespace = token.whitespace_
                continue
            else:
                text += previous_whitespace + token.text
            previous_whitespace = token.whitespace_

        return postprocess(text), entities, relevant


class KeeperFragmentFragmentGenerator(ErrorGenerator):

    def __init__(self, dependency_to_keep, tag=None):
        self.dependency_to_keep = dependency_to_keep
        self.tag = tag

    def is_target_token(self, token):
        return token.dep_ == self.dependency_to_keep and \
               (self.tag is None or self.tag == token.tag_)

    def generate_from_doc(self, doc, prompt=None):

        text = ""
        entities = []

        # Identify a preposition outside of the prompt
        target_token = None
        for token in doc:
            if (prompt is None or token.idx >= len(prompt)) and self.is_target_token(token):
                target_token = token
                break

        # If there is no preposition, we cannot make a relevant fragment
        relevant = target_token is not None
        if not relevant:
            return doc.text, [], relevant

        # If there is a preposition, we only keep the words in its prepositional phrase
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
adverbialClauseFragmentGenerator = KeeperFragmentFragmentGenerator('advcl')
relativeClauseFragmentGenerator = KeeperFragmentFragmentGenerator('relcl')
infinitiveFragmentGenerator = KeeperFragmentFragmentGenerator('xcomp', 'VB')
nounPhraseFragmentGenerator = KeeperFragmentFragmentGenerator('dobj')


class MissingObjectFragmentGenerator(ErrorGenerator):

    def __init__(self):
        pass

    def generate_from_doc(self, doc, prompt=None):

        text = ""
        entities = []

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

        # If there is a direct object, we remove all the tokens that have that direct
        # object among their heads
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

        return postprocess(text), entities, relevant
