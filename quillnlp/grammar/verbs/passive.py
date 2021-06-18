import random
import re

from quillgrammar.grammar.constants import GrammarError, Dependency, TokenSet, Tag
from quillgrammar.grammar.verbutils import is_passive
from quillnlp.grammar.generation import ErrorGenerator


# Error generators

class PassiveWithIncorrectBeErrorGenerator(ErrorGenerator):

    name = GrammarError.PASSIVE_WITH_INCORRECT_BE.value

    def generate_from_doc(self, doc, p=0.5):

        new_sentence = ""
        entities = []
        relevant = False
        for token in doc:
            # TODO: right now we leave out contractions because they
            # lead to replacement problems
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif token.dep_ == Dependency.PASS_AUXILIARY.value and \
                    (token.text.lower() in TokenSet.MUTUALLY_EXCLUSIVE_BE_FORMS.value
                    or token.text.lower() in TokenSet.MUTUALLY_EXCLUSIVE_BE_FORMS_PAST.value):
                relevant = True
                if random.random() < p:
                    if token.text.lower() in TokenSet.MUTUALLY_EXCLUSIVE_BE_FORMS.value:
                        other_forms_of_be = list(TokenSet.MUTUALLY_EXCLUSIVE_BE_FORMS.value - set([token.text.lower()]))
                    else:
                        other_forms_of_be = list(TokenSet.MUTUALLY_EXCLUSIVE_BE_FORMS_PAST.value - set([token.text.lower()]))
                    new_be_form = random.choice(other_forms_of_be)
                    next_token = doc[token.i+1]
                    if next_token.text == "n't":
                        new_sentence += new_be_form + " "
                    else:
                        new_sentence += new_be_form + token.whitespace_
                    entities.append((token.idx, token.idx + len(new_be_form), self.name))

                else:
                    new_sentence += token.text_with_ws

            else:
                new_sentence += token.text_with_ws

        new_sentence = re.sub(" n't", " not", new_sentence)

        return new_sentence, entities, relevant


class PassiveWithoutBeErrorGenerator(ErrorGenerator):

    name = GrammarError.PASSIVE_WITHOUT_BE.value

    def generate_from_doc(self, doc, p=0.5):
        """ Removes the passive auxiliary 'be' from a sentence. """

        new_sentence = ""
        entities = []
        relevant = False

        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            # TODO: right now we leave out contractions because they
            # lead to replacement problems
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif (token.dep_ == Dependency.PASS_AUXILIARY.value and token.lemma_ == "be"):
                relevant = True
                next_token = doc[token.i + 1]

                # Exclude cases like to-be-read, where the next token is '-'
                if next_token.text != "-" and random.random() < p:
                    start_index = len(new_sentence)
                    entities.append((start_index, start_index + len(next_token), self.name))
                else:
                    new_sentence += token.text_with_ws
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities, relevant


class PassivePastTenseAsParticipleErrorGenerator(ErrorGenerator):

    name = GrammarError.PASSIVE_WITH_SIMPLE_PAST_INSTEAD_OF_PARTICIPLE.value

    def generate_from_doc(self, doc):
        """ Replaces the past participle (e.g. forgotten) by its past tense (e.g. forgot) """

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws

            elif is_passive(token) and not token.lemma_ == "be" and token.tag_ == Tag.PAST_PARTICIPLE_VERB.value:
                past_tense = token._.inflect(Tag.SIMPLE_PAST_VERB.value)
                if past_tense is not None:
                    new_sentence += past_tense + token.whitespace_
                    entities.append([token.idx,
                                     token.idx+len(past_tense),
                                     self.name])
                else:
                    new_sentence += token.text_with_ws
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities

