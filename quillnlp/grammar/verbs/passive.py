import random
import re

from quillgrammar.grammar.constants import GrammarError, Dependency, TokenSet, Tag
from quillgrammar.grammar.verbutils import is_passive
from quillnlp.grammar.generation import ErrorGenerator


# Error generators

class PassiveWithIncorrectBeErrorGenerator(ErrorGenerator):

    name = GrammarError.PASSIVE_WITH_INCORRECT_BE.value

    def token_test(self, token):
        if token.text.startswith("'"):
            return False
        elif token.dep_ == Dependency.PASS_AUXILIARY.value and \
                (token.text.lower() in TokenSet.MUTUALLY_EXCLUSIVE_BE_FORMS.value 
                or token.text.lower() in TokenSet.MUTUALLY_EXCLUSIVE_BE_FORMS_PAST.value):
            return True

    def get_candidates(self, doc):
        return [t for t in doc if self.token_test(t)]

    def get_replacement(self, target, doc):
        if target.text.lower() in TokenSet.MUTUALLY_EXCLUSIVE_BE_FORMS.value:
            other_forms_of_be = list(TokenSet.MUTUALLY_EXCLUSIVE_BE_FORMS.value - set([target.text.lower()]))
        else:
            other_forms_of_be = list(TokenSet.MUTUALLY_EXCLUSIVE_BE_FORMS_PAST.value - set([target.text.lower()]))

        return random.choice(other_forms_of_be)


class PassiveWithoutBeErrorGenerator(ErrorGenerator):

    name = GrammarError.PASSIVE_WITHOUT_BE.value

    def token_test(self, doc, token):
        if token.text.startswith("'"):
            return False
        if token.i < len(doc)-1 and doc[token.i + 1].text =='-':
            return False
        elif (token.dep_ == Dependency.PASS_AUXILIARY.value and token.lemma_ == "be"):
            return True

    def get_candidates(self, doc):
        return [t for t in doc if self.token_test(doc, t)]

    def get_replacement(self, target, doc):
        return ''


class PassivePastTenseAsParticipleErrorGenerator(ErrorGenerator):

    name = GrammarError.PASSIVE_WITH_SIMPLE_PAST_INSTEAD_OF_PARTICIPLE.value

    def get_candidates(self, doc):
        return [t for t in doc if is_passive(t) and not t.lemma_ == "be" and t.tag_ == Tag.PAST_PARTICIPLE_VERB.value]

    def get_replacement(self, target, doc):
        return target._.inflect(Tag.SIMPLE_PAST_VERB.value)

