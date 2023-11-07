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
                # or \
                #     (token.pos_ in [POS.VERB.value, POS.AUX.value] and token.head == target_token):
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

            if token.tag_ in [Tag.PRESENT_OTHER_VERB.value, Tag.PRESENT_SING3_VERB.value, Tag.SIMPLE_PAST_VERB.value] \
                    and token.lemma_ != 'have':
                target_tokens.append(token)
                break

        # If there is no target token, we cannot make a relevant fragment
        relevant = len(target_tokens) > 0
        if not relevant:
            return doc.text, [], relevant

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
            if token.pos_ == POS.VERB.value or token.pos_ == POS.AUX.value:
                subject = get_subject(token, full=True)
                if subject is not None:
                    subjects_in_doc.append((token, subject))

        if len(subjects_in_doc) == 0:
            return doc.text, [], relevant

        verb, subject_to_remove = random.choice(subjects_in_doc)

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
                previous_whitespace = token.whitespace_
            elif token == target_token or \
                    token in target_token.rights or \
                    target_token in token.lefts or \
                    set(get_all_heads(doc, token)).intersection(target_token.rights):

                if token == target_token:
                    start_idx = len(text + previous_whitespace)
                    entities.append((start_idx, start_idx + len(token), 'FRAGMENT_VERB_PHRASE'))

                text += previous_whitespace + token.text
                previous_whitespace = token.whitespace_
            elif len(text) > 0:
                previous_whitespace = token.whitespace_

        text = postprocess(text.strip())


        if entities[0][0] < 0:
            print()
            print('DT', doc.text)
            print('T',text)
            print(target_token)
            print(target_token.idx)
            print(entities)
            input()

        return text, entities, relevant


class KeeperFragmentFragmentGenerator(ErrorGenerator):

    def __init__(self, dependency_to_keep, label, tag=None, exclude_tags=[]):
        self.dependency_to_keep = dependency_to_keep
        self.tag = tag
        self.label = label
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
        target_token_start_idx = None
        for token in doc:
            if prompt is not None and token.idx < len(prompt):
                text += previous_whitespace + token.text
                previous_whitespace = token.whitespace_
            elif token == target_token or target_token in get_all_heads(doc, token):
                if token == target_token:
                    target_token_start_idx = len(text+previous_whitespace)
                    entities.append((target_token_start_idx, target_token_start_idx+len(token), self.label))

                text += previous_whitespace + token.text
                previous_whitespace = token.whitespace_
            elif len(text) > 0:
                previous_whitespace = token.whitespace_

        return postprocess(text), entities, relevant


prepositionalPhraseFragmentGenerator = KeeperFragmentFragmentGenerator('prep', 'FRAGMENT_PREPOSITIONAL_PHRASE')


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
                previous_whitespace = token.whitespace_
            elif token == target_token or target_token in get_all_heads(doc, token):
                if token == target_token:
                    target_token_start_idx = len(text+previous_whitespace)
                    entities.append((target_token_start_idx, target_token_start_idx+len(token), 'FRAGMENT_INFINITIVE_PHRASE'))

                text += previous_whitespace + token.text
                previous_whitespace = token.whitespace_
            elif len(text) > 0:
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
                previous_whitespace = token.whitespace_
            elif token == target_token or target_token in get_all_heads(doc, token):
                if token == target_token:
                    target_token_start_idx = len(text+previous_whitespace)
                    entities.append((target_token_start_idx, target_token_start_idx+len(token), 'FRAGMENT_NOUN_PHRASE'))

                text += previous_whitespace + token.text
                previous_whitespace = token.whitespace_
            elif len(text) > 0:
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
                previous_whitespace = token.whitespace_
            elif token == target_token or target_token in get_all_heads(doc, token):
                if token == target_token:
                    target_token_start_idx = len(text+previous_whitespace)
                    entities.append((target_token_start_idx, target_token_start_idx+len(token), 'FRAGMENT_RELATIVE_CLAUSE'))
                text += previous_whitespace + token.text
                previous_whitespace = token.whitespace_
            elif len(text) > 0:
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
                previous_whitespace = token.whitespace_
            elif token == target_token or target_token in get_all_heads(doc, token):
                if token == target_token:
                    target_token_start_idx = len(text+previous_whitespace)
                    entities.append((target_token_start_idx, target_token_start_idx+len(token), 'FRAGMENT_DEPENDENT_CLAUSE'))
                text += previous_whitespace + token.text
                previous_whitespace = token.whitespace_
            elif len(text) > 0:
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

        heads = [t for t in doc if target_token.head == t]
        if len(heads) == 0:
            return doc.text, [], False
        head = heads[0]

        random_number = random.random()
        if target_token.head.lemma_ in self.transitive_verbs and random_number < 0.5:
            text, entities = self.remove_full_object(prompt, doc, target_token)
        else:
            text, entities = self.remove_part_of_object(prompt, doc, target_token)

        text = postprocess(text)

        if head.idx < target_token.idx:
            entities.append((head.idx, head.idx+len(head), 'FRAGMENT_NO_OBJ'))
        else:
            removed_characters = len(doc.text) - len(text)
            entities.append((head.idx-removed_characters, head.idx+len(head)-removed_characters, 'FRAGMENT_NO_OBJ'))

        return text, entities, relevant
