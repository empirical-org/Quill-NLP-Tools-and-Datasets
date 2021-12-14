import re

from quillgrammar.grammar.constants import GrammarError, Tag, Dependency
from quillnlp.grammar.generation import ErrorGenerator
from quillnlp.grammar.verbutils import get_perfect_progressives, in_have_been_construction, is_passive


class PerfectTenseWithoutHaveErrorGenerator(ErrorGenerator):

    name = GrammarError.PERFECT_WITHOUT_HAVE.value

    def get_candidates(self, doc):
        candidates = []
        for token in doc:
            if token.tag_ == Tag.PAST_PARTICIPLE_VERB.value and not is_passive(token):

                # We ensure the past tense is different from the past participle.
                # Otherwise removing 'have' may not result in an error.
                past_tense = token._.inflect(Tag.SIMPLE_PAST_VERB.value)
                present_tense = token._.inflect(Tag.PRESENT_OTHER_VERB.value)
                participle = token._.inflect(Tag.PAST_PARTICIPLE_VERB.value)

                if past_tense is not None and \
                        participle is not None and \
                        present_tense is not None and \
                        past_tense != participle and \
                        present_tense != participle:

                    for child in token.lefts:
                        if child.lemma_ == 'have' or child.lemma_ == "'ve":
                            candidates.append(child)

        return candidates

    def get_replacement(self, target, doc):
        return ' ' if target.text.startswith("'") else ''


class PerfectProgressiveWithoutHaveErrorGenerator(ErrorGenerator):

    name = GrammarError.PERFECT_PROGRESSIVE_WITHOUT_HAVE.value

    def get_candidates(self, doc):
        candidates = []
        for t in doc:
            if t.tag_ == Tag.PRESENT_PARTICIPLE_VERB.value and not is_passive(t):
                for child in t.lefts:
                    if child.dep_ == Dependency.AUX.value and (child.lemma_ == "have" or child.lemma_ == "'ve"):
                        candidates.append(child)
        return candidates

    def get_replacement(self, target, doc):
        return ' ' if target.text.startswith("'") else ''



class PassivePerfectWithoutHaveErrorGenerator(ErrorGenerator):

    name = GrammarError.PASSIVE_PERFECT_WITHOUT_HAVE.value

    def get_candidates(self, doc):
        candidates = []
        for t in doc:
            if t.tag_ == Tag.PAST_PARTICIPLE_VERB.value and is_passive(t):
                for child in t.lefts:
                    if child.dep_ == Dependency.AUX.value and (child.lemma_ == "have" or child.lemma_ == "'ve"):
                        candidates.append(child)

        return candidates

    def get_replacement(self, target, doc):
        return ' ' if target.text.startswith("'") else ''


class PerfectTenseWithSimplePastErrorGenerator(ErrorGenerator):

    name = GrammarError.PERFECT_TENSE_WITH_INCORRECT_PARTICIPLE.value

    def get_candidates(self, doc):
        candidates = []
        for t in doc:

            if not is_passive(t) and not t.lemma_ == "be" and \
                    t.tag_ == Tag.PAST_PARTICIPLE_VERB.value:
                simple_past = t._.inflect(Tag.SIMPLE_PAST_VERB.value)

                # We only do this for verbs whose simple past does not end in "ed"
                if simple_past is not None and simple_past != t.text:
                    candidates.append(t)
        return candidates

    def get_replacement(self, target, doc):
        return target._.inflect(Tag.SIMPLE_PAST_VERB.value)


class PassivePerfectWithIncorrectParticipleErrorGenerator(ErrorGenerator):

    name = GrammarError.PASSIVE_PERFECT_WITH_INCORRECT_PARTICIPLE.value

    def get_candidates(self, doc):
        candidates = []
        for t in doc:
            if t.tag_ == Tag.PAST_PARTICIPLE_VERB.value and is_passive(t) and in_have_been_construction(t):

                # We ensure the past tense is different from the past participle.
                past_tense = t._.inflect(Tag.SIMPLE_PAST_VERB.value)

                if past_tense is not None and past_tense.lower() != t.text.lower():
                    candidates.append(t)
        return candidates

    def get_replacement(self, target, doc):
        return target._.inflect(Tag.SIMPLE_PAST_VERB.value)


class PerfectProgressiveWithIncorrectBeAndWithoutHaveErrorGenerator(ErrorGenerator):

    name = GrammarError.PERFECT_PROGRESSIVE_WITH_INCORRECT_BE_AND_WITHOUT_HAVE.value

    def generate_from_doc(self, doc):

        perfect_progressives = get_perfect_progressives(doc)

        if len(perfect_progressives) > 0:

            first_perfect_progressive = perfect_progressives[0]

            for token in first_perfect_progressive.lefts:
                if token.lemma_ == "have":
                    token._.replace = " " if token.text.startswith("'") else ""
                elif token.text == "been":
                    token._.replace = "be"

            new_sentence = ""
            entities = []
            for token in doc:
                if token._.replace is not None and token.lemma_ == "have":
                    new_sentence += token._.replace
                elif token._.replace is not None:
                    entity_start = len(new_sentence)
                    entity_end = entity_start + len(token._.replace)
                    new_sentence += token._.replace + token.whitespace_
                    entities.append([entity_start, entity_end, self.name])
                else:
                    new_sentence += token.text_with_ws

            return new_sentence, entities, True

        else:
            return doc.text, [], False

