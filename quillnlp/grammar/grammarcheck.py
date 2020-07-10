import re
import spacy
import lemminflect
import torch
import json

from typing import List
from collections import namedtuple
from lemminflect import getLemma

from spacy.tokens.doc import Doc
from spacy.tokens.token import Token
from transformers import BertForTokenClassification, BertTokenizer

from quillnlp.grammar.unsupervised import UnsupervisedGrammarChecker, classify_agreement_errors
from quillnlp.grammar.verbs import agreement
from quillnlp.grammar.verbutils import has_noun_subject, has_pronoun_subject, is_passive, in_have_been_construction, \
    get_past_tenses, has_inversion, get_subject, token_has_inversion
from quillnlp.models.bert.train import evaluate
from quillnlp.models.bert.preprocessing import convert_data_to_input_items, get_data_loader, NLPTask
from quillnlp.grammar.constants import *

BASE_SPACY_MODEL = "en"

Token.set_extension("grammar_errors", default=[])

statistical_error_map = {"WOMAN": GrammarError.WOMAN_WOMEN.value,
                         "ITS": GrammarError.POSSESSIVE_PRONOUN.value,
                         "THEN": GrammarError.THAN_THEN.value,
                         "POSSESSIVE": GrammarError.PLURAL_POSSESSIVE.value,
                         "CHILD": GrammarError.CHILD_CHILDREN.value,
                         "ADV": GrammarError.ADVERB.value}
                         #"VERB": GrammarError.SUBJECT_VERB_AGREEMENT.value}

error_precedence = {
    GrammarError.REPEATED_WORD.value: 8,
    GrammarError.PASSIVE_INCORRECT_PAST_TENSE_AS_PARTICIPLE.value: 5,
    GrammarError.PASSIVE_PAST_TENSE_AS_PARTICIPLE.value: 5,
    GrammarError.PASSIVE_PERFECT_WITH_INCORRECT_PARTICIPLE.value: 5,
    GrammarError.PASSIVE_WITH_INCORRECT_BE.value: 5,
    GrammarError.PASSIVE_PERFECT_WITHOUT_HAVE.value: 5,
    GrammarError.PASSIVE_WITHOUT_BE.value: 5,
    GrammarError.PERFECT_TENSE_WITHOUT_HAVE.value: 5,
    GrammarError.PERFECT_TENSE_WITH_SIMPLE_PAST.value: 5,
    GrammarError.PERFECT_PROGRESSIVE_WITH_INCORRECT_BE_WITHOUT_HAVE.value: 5,
    GrammarError.PERFECT_PROGRESSIVE_WITHOUT_HAVE.value: 5,
    GrammarError.PERFECT_TENSE_WITH_INCORRECT_SIMPLE_PAST.value: 5,
    GrammarError.YES_NO_COMMA.value: 5,
    GrammarError.POSSESSIVE_PRONOUN.value: 7,
    GrammarError.SUBJECT_PRONOUN.value: 6,
    GrammarError.OBJECT_PRONOUN.value: 6,
    GrammarError.COMMAS_IN_NUMBERS.value: 5,
    GrammarError.SPACING.value: 4,
    GrammarError.IRREGULAR_PLURAL_NOUN.value: 5,
    GrammarError.CONTRACTION.value: 5,
    GrammarError.INCORRECT_IRREGULAR_PAST_TENSE.value: 4,
    GrammarError.SVA_COLLECTIVE_NOUN.value: 3,
    GrammarError.SVA_INDEFINITE.value: 3,
    GrammarError.SVA_SIMPLE_NOUN.value: 2,
    GrammarError.SVA_PRONOUN.value: 1,
    GrammarError.QUESTION_MARK.value: 2,
    GrammarError.PUNCTUATION.value: 1,
}

participles = {
    "wake": ["waken"], #pyinflect has "woke"
    "awaken": ["awoken"],
    "work": ["worked"], #pyinflect has "wrought",
    "sew": ["sown"],
    "prove": ["proved", "proven"],
    "get": ["gotten", "got"],
    "burn": ["burned", "burnt"],
    "sunburn": ["sunburned", "sunburnt"],
    "hide": ["hidden"],
    "ring": ["ringed", "rung"],
    "learn": ["learnt", "learned"],
}

plurals = {
    "penny": ["pennies"],
    "bacteria": ["bacteria"],
    "bacterium": ["bacteria"],
    "media": ["media"],
    "medium": ["mediums", "media"],
    "mosquito": ["mosquitos", "mosquitoes"],
    "sibling": ["siblings"],
    "duckling": ["ducklings"],
    "loaf": ["loaves"],
    "half": ["halves"],
    "fish": ["fish"],
    "leaf": ["leaves"],
    "spaghetti": ["spaghetti"],
    "person": ["people"]
}

Error = namedtuple("Error", ["text", "index", "type", "subject"])


# Utility methods


def is_subject(token: Token) -> bool:
    if token.dep_.startswith(Dependency.SUBJECT.value):
        return True
    elif token.dep_ == Dependency.CONJUNCTION.value and \
            token.head.dep_.startswith(Dependency.SUBJECT.value):
        return True
    else:
        return False


def get_correct_participles(token: Token) -> bool:

    return participles.get(token.lemma_.lower(), [token._.inflect(Tag.PAST_PARTICIPLE_VERB.value)])


def get_correct_plurals(token: Token) -> bool:

    lemmas = getLemma(token.text, upos=token.pos_)

    if len(lemmas) > 0:
        lemma = lemmas[0].lower()
        if lemma in plurals:
            return plurals.get(lemma)
        else:
            plural = token._.inflect(Tag.PLURAL_NOUN.value)
            if plural is not None:
                return [plural.lower()]
    return []

# Grammar checks for individual errors


class RuleBasedGrammarCheck(object):
    """
    Abstract class for rule-based grammar checks.
    """

    name = None

    def __call__(self, doc: Doc):
        return self.check(doc)

    def check(self, doc: Doc) -> List[Error]:
        raise NotImplementedError


class RuleBasedPluralVsPossessiveCheck(RuleBasedGrammarCheck):
    """
    Identifies confusion between a possessive ("cousin's") and
    a plural ("cousins")
    """

    name = GrammarError.PLURAL_POSSESSIVE.value

    def check(self, doc: Doc) -> List[Error]:
        # TODO: this does not treat cases like "it's my cousin's" correctly.
        errors = []
        for i in range(0, len(doc) - 1):
            if doc[i].text.lower() in TokenSet.POSSESSIVE_S.value and \
                    (doc[i].tag_ == Tag.POSSESSIVE.value or
                     doc[i].pos_ == POS.PARTICIPLE.value) and \
                    doc[i-1].pos_ == POS.NOUN.value and \
                    (doc[i + 1].pos_ not in [POS.NOUN.value, POS.COORD_CONJ.value]):
                errors.append(Error(doc[i].text, doc[i].idx, self.name, None))
#            elif doc[i].tag_ == Tag.PLURAL_NOUN.value and doc[i+1].pos_ == POS.NOUN.value:
#                errors.append(Error(doc[i].text, doc[i].idx, self.name, None))

        return errors


class RuleBasedQuestionMarkCheck(RuleBasedGrammarCheck):
    """
    Identifies questions that do not have a question mark.
    """

    name = GrammarError.QUESTION_MARK.value

    def check(self, doc: Doc) -> List[Error]:
        # TODO: should also catch "Is he going to dance tonight." with AUX
        errors = []
        if doc[-1].text != Word.QUESTION_MARK.value:
            # Cases like: When will she come home?
            #if doc[0].tag_ in QUESTION_WORD_TAGS and doc[1].pos_ == POS.VERB.value:  # change
            #    errors.append(Error(doc[-1].text, doc[-1].idx, self.name, None))
            tags = set([t.tag_ for t in doc])
            if len(tags.intersection(QUESTION_WORD_TAGS)) > 0 and has_inversion(doc):
                errors.append(Error(doc[-1].text, doc[-1].idx, self.name, None))

            # Cases like: Will he come home?
            elif doc[0].pos_ == POS.VERB.value and doc[0].dep_ == Dependency.AUX.value:
                errors.append(Error(doc[-1].text, doc[-1].idx, self.name, None))
            # Cases like: Is he dead?
            elif doc[0].pos_ == POS.AUX.value:
                subject = agreement.get_subject(doc[0])
                if subject is not None and subject.i > 0:
                    errors.append(Error(doc[-1].text, doc[-1].idx, self.name, None))
            # Other cases where the subject follows its head
            else:  # change
                for token in doc:
                    if token.dep_.startswith(Dependency.SUBJECT.value) and \
                            token.i > token.head.i:
                        errors.append(Error(doc[-1].text,
                                            doc[-1].idx,
                                            self.name,
                                            None))
                        break
                    # as soon as we meet a subject before we meet a verb,
                    # stop looking
                    elif token.dep_.startswith(Dependency.SUBJECT.value) and \
                            token.i < token.head.i:
                        break
            """
            elif doc[0].pos_ == POS.AUX.value and doc[0].dep_ == Dependency.ROOT.value:
                errors.append(Error(doc[-1].text, doc[-1].idx, self.name, None))
            # Cases like: Is Laura playing softball tomorrow?
            elif doc[0].pos_ == POS.AUX.value and doc[0].dep_ == Dependency.AUX.value:
                errors.append(Error(doc[-1].text, doc[-1].idx, self.name, None))
            """


        return errors


class RuleBasedArticleCheck(RuleBasedGrammarCheck):
    """
    Identifies instances where determiner "a" is followed by a vowel, or
    "an" is followed by a consonant.
    """

    name = GrammarError.ARTICLE.value

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc[:-1]:
            # if "a" before vowel
            if token.pos_ == POS.DETERMINER.value and \
                    token.text.lower() == Word.INDEF_ARTICLE_BEFORE_CONSONANT.value \
                    and self._starts_with_vowel(doc[token.i + 1].text):
                errors.append(Error(token.text, token.idx, self.name, None))
            # if "an" before consonant
            elif token.pos_ == POS.DETERMINER.value and \
                    token.text.lower() == Word.INDEF_ARTICLE_BEFORE_VOWEL.value \
                    and self._starts_with_consonant(doc[token.i + 1].text):
                errors.append(Error(token.text, token.idx, self.name, None))
        return errors

    def _starts_with_consonant(self, token: str) -> bool:
        if re.match("[bcdfgjklmnpqrstvwxz]", token, re.IGNORECASE):
            return True
        return False

    def _starts_with_vowel(self, token: str) -> bool:
        # We leave out "u", because of "a useful", etc.
        if re.match("[aeio]", token, re.IGNORECASE):
            return True
        return False


class RuleBasedThisVsThatCheck(RuleBasedGrammarCheck):
    """
    Identifies errors like "this/these X there" or "that/those X here".
    """

    name = GrammarError.THIS_THAT.value

    def check(self, doc: Doc) -> List[Error]:
        # It's not straightforward to rewrite this using spaCy's noun chunks
        # as "this table over there" is not a noun chunk, but "this table" is.

        errors = []
        current_noun_phrase = []
        for token in doc:
            if token.text.lower() in TokenSet.DEMONSTRATIVES.value and \
                    token.pos_ == POS.DETERMINER.value:
                current_noun_phrase = [token]
            elif token.pos_ in POSSIBLE_POS_IN_NOUN_PHRASE:
                current_noun_phrase.append(token)
                if token.text.lower() == Word.HERE.value and \
                        current_noun_phrase[0].text.lower() == Word.THAT.value:
                    errors.append(Error(current_noun_phrase[0].text,
                                        current_noun_phrase[0].idx,
                                        self.name,
                                        None))
                elif token.text.lower() == Word.HERE.value and \
                        current_noun_phrase[0].text.lower() == Word.THOSE.value:
                    errors.append(Error(current_noun_phrase[0].text,
                                        current_noun_phrase[0].idx,
                                        self.name,
                                        None))
                elif token.text.lower() == Word.THERE.value and \
                        current_noun_phrase[0].text.lower() == Word.THIS.value:
                    errors.append(Error(current_noun_phrase[0].text,
                                        current_noun_phrase[0].idx,
                                        self.name,
                                        None))
                elif token.text.lower() == Word.THERE.value and \
                        current_noun_phrase[0].text.lower() == Word.THESE.value:
                    errors.append(Error(current_noun_phrase[0].text,
                                        current_noun_phrase[0].idx,
                                        self.name,
                                        None))
            else:
                current_noun_phrase = []

        return errors


class RuleBasedSpacingCheck(RuleBasedGrammarCheck):
    """
    Identifies punctuation that is not followed by a space
    or that is incorrectly preceded by a space.
    """

    name = GrammarError.SPACING.value

    def check(self, doc: Doc) -> List[Error]:
        errors = []

        # Punctuation not followed by a space
        for token in doc[:-1]:
            if token.text in TokenSet.PUNCTUATION_FOLLOWED_BY_SPACE.value and \
                    token.whitespace_ == "" and not doc[token.i+1].is_punct:
                errors.append(Error(token.text, token.idx, self.name, None))

        # Punctuation incorrectly preceded by a space
        for token in doc:
            if token.i > 0 and \
                    token.text in TokenSet.PUNCTUATION_NOT_PRECEDED_BY_SPACE.value and \
                    len(doc[token.i-1].whitespace_) > 0:
                errors.append(Error(token.text, token.idx, self.name, None))
            elif "." in token.text and re.search(r"\.\w", token.text) \
                    and not re.search(r"\.\w+\.", token.text):   # exclude D.C., T.S.
                errors.append(Error(token.text, token.idx, self.name, None))
        return errors


class WomanVsWomenCheck(RuleBasedGrammarCheck):
    """
    Identifies "womans" as the incorrect plural of "woman".
    """

    name = GrammarError.WOMAN_WOMEN.value

    def check(self, doc: Doc) -> List[Error]:
        return [Error(t.text, t.idx, self.name, None) for t in doc
                if t.text.lower() == Word.INCORRECT_PLURAL_WOMAN.value]


class ManVsMenCheck(RuleBasedGrammarCheck):
    """
    Identifies "mans" as the incorrect plural of "man".
    """

    name = GrammarError.MAN_MEN.value

    def check(self, doc: Doc) -> List[Error]:
        return [Error(t.text, t.idx, self.name, t) for t in doc
                if t.text.lower() == Word.INCORRECT_PLURAL_MAN.value]


class ThanVsThenCheck(RuleBasedGrammarCheck):
    """
    Identifies instances of "then" that should be "than".
    """

    name = GrammarError.THAN_THEN.value

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc[1:]:
            if token.text.lower() == Word.THEN.value and \
                    doc[token.i - 1].tag_ in COMPARATIVE_TAGS:
                errors.append(Error(token.text, token.idx, self.name, None))
        return errors


class RepeatedWordCheck(RuleBasedGrammarCheck):
    """
    Identifies repeated words.
    """

    name = GrammarError.REPEATED_WORD.value

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for t in doc[1:]:
            if t.text.lower() != "that" and t.text.lower() == doc[t.i-1].text.lower():
                errors.append(Error(t.text, t.idx, self.name, None))
        return errors


class SubjectPronounCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect subject pronouns (e.g. object pronouns,
    such as "me", possessive determiners such as "my" or possessive
    pronouns such as "mine").
    """

    name = GrammarError.SUBJECT_PRONOUN.value

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        nonsubj_pronouns = TokenSet.OBJECT_PRONOUNS.value | \
            TokenSet.POSSESSIVE_DETERMINERS.value | \
            TokenSet.POSSESSIVE_PRONOUNS.value
        for token in doc:
            #if is_subject(token) and token.text.lower() in nonsubj_pronouns:
            #    errors.append(Error(token.text, token.idx, self.name, None))
            if (token.pos_ == POS.VERB.value or token.pos_ == POS.AUX.value) \
                    and token.tag_ != Tag.INFINITIVE.value:
                subject = get_subject(token)
                if subject is not None and subject.text.lower() in nonsubj_pronouns:
                    errors.append(Error(subject.text, subject.idx, self.name, None))

        return errors


class ObjectPronounCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect object pronouns (e.g. subject pronouns, such as "I").
    """

    name = GrammarError.OBJECT_PRONOUN.value

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            if token.text.lower() in TokenSet.SUBJECT_PRONOUNS.value and \
                    not is_subject(token):
                errors.append(Error(token.text, token.idx, self.name, None))
        return errors


class CommasInNumbersCheck(RuleBasedGrammarCheck):
    """
    Identifies long numbers (more than 3 digits) that miss a comma.
    """

    name = GrammarError.COMMAS_IN_NUMBERS.value

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            # If there are 4 digits, we have to exclude dates
            if re.search(r"^\d{4}$", token.text):
                if token.ent_type_ == EntityType.DATE.value or \
                         1900 < int(token.text) < 2200:
                    continue
                else:
                    errors.append(Error(token.text, token.idx, self.name, None))
            # Otherwise, we flag all tokens as incorrect when they have 4 digits
            # that follow each other without a comma.
            elif re.search(r"\d{4,}", token.text):
                errors.append(Error(token.text, token.idx, self.name, None))
        return errors


class CommasAfterYesNoCheck(RuleBasedGrammarCheck):
    """
    Identifies instances of yes/no that are not followed by a comma.
    """

    name = GrammarError.YES_NO_COMMA.value

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc[:-1]:
            if token.text.lower() in TokenSet.YES_NO.value and \
                    token.tag_ == Tag.YES_NO.value and \
                    not doc[token.i+1].is_punct:
                errors.append(Error(token.text, token.idx, self.name, None))
        return errors


class SingularPluralNounCheck(RuleBasedGrammarCheck):
    """
    Identifies sentences where a singular determiner (a, an) has as its head a
    plural noun.
    """

    name = GrammarError.SINGULAR_PLURAL.value

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for noun_chunk in doc.noun_chunks:
            for token in noun_chunk:
                if (token.text.lower() in ["a", "an"] or token.text.lower() in TokenSet.SINGULAR_DETERMINERS.value) and \
                        token.dep_ == Dependency.DETERMINER.value and \
                        token.head.tag_ == Tag.PLURAL_NOUN.value:
                    errors.append(Error(token.text, token.idx, self.name, None))
        return errors


class CapitalizationCheck(RuleBasedGrammarCheck):
    """
    Identifies cases where a sentence does not start with a capital letter, or
    "I" is not capitalized.
    """

    name = GrammarError.CAPITALIZATION.value

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        if re.match("[a-z]", doc[0].text):
            doc[0]._.grammar_errors.append(GrammarError.CAPITALIZATION.value)
            errors.append(Error(doc[0].text, doc[0].idx, self.name, None))
        for token in doc[1:]:
            if token.text == "i":
                errors.append(Error(token.text, token.idx, self.name, None))

            # Ideally, we'd like to check if the token is a proper noun, but
            # spacy is just not good enough at this. In the future, we may
            # have a check for capitalization statistics in a large reference
            # corpus.
            #elif token.pos_ == POS.PROPER_NOUN.value and token.text.islower():
            #    errors.append(Error(token.text, token.idx, self.name, None))
        return errors


class ContractionCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect contractions such as "Im" and "didnt".
    """

    name = GrammarError.CONTRACTION.value

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            if token.text.lower() in TokenSet.INCORRECT_CONTRACTIONS.value:
                errors.append(Error(token.text, token.idx, self.name, None))
            elif token.pos_ in [POS.VERB.value, POS.ADVERB.value, POS.PARTICIPLE.value] and \
                    token.text.lower() in TokenSet.CONTRACTED_VERBS_WITHOUT_APOSTROPHE.value:
                errors.append(Error(token.text, token.idx, self.name, None))
        return errors


class IncorrectIrregularPastTenseCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect verb forms, such as "bringed" and "writed".
    """

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            # If the token is a past tense verb
            if token.tag_ == Tag.SIMPLE_PAST_VERB.value and not token.tag_ == Tag.MODAL_VERB.value:
                past_tenses = get_past_tenses(token)

                if is_passive(token):
                    error_type = GrammarError.PASSIVE_INCORRECT_PAST_TENSE_AS_PARTICIPLE.value
                else:
                    error_type = GrammarError.INCORRECT_IRREGULAR_PAST_TENSE.value

                # We exclude 'been' to avoid confusion with Passive perfect without have
                if not token.text.lower() in past_tenses and not token.text.lower() == "been":
                    errors.append(Error(token.text, token.idx, error_type, None))
        return errors


class IncorrectParticipleCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect verb forms, such as "bringed" and "writed".
    """

    name = GrammarError.INCORRECT_PARTICIPLE.value

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:

            # If the token is a participle
            if token.tag_ == Tag.PAST_PARTICIPLE_VERB.value and \
                    not token.tag_ == Tag.MODAL_VERB.value:

                correct_participles = get_correct_participles(token)
                correct_past_tenses = get_past_tenses(token)

                if is_passive(token):
                    if in_have_been_construction(token):
                        error_type = GrammarError.PASSIVE_PERFECT_WITH_INCORRECT_PARTICIPLE.value
                    elif token.text in correct_past_tenses:
                        error_type = GrammarError.PASSIVE_PAST_TENSE_AS_PARTICIPLE.value  #TODO: sth strange here: in the second case below, it cannot be in the correct_past_tenses
                    else:
                        error_type = GrammarError.PASSIVE_WITH_INCORRECT_PARTICIPLE.value
                else:
                    error_type = GrammarError.INCORRECT_PARTICIPLE.value

                # If pyinflect does not return a verb form because it
                # does not know the lemma
                # e.g. "cutted" has unknown lemma "cutte"
                if correct_participles == [None]:
                    errors.append(Error(token.text, token.idx, error_type, None))

                # If the verb form is not the same as the one returned
                # by pyinflect
                # e.g. "bringed" instead of "brought"
                elif token.text not in correct_participles and \
                        token.text not in correct_past_tenses:
                    errors.append(Error(token.text, token.idx, error_type, None))
        return errors


class PunctuationCheck(RuleBasedGrammarCheck):
    """
    Checks if a sentence ends in a punctuation mark.
    """

    name = GrammarError.PUNCTUATION.value

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        if doc[-1].text not in TokenSet.END_OF_SENTENCE_PUNCTUATION.value:
            errors.append(Error(doc[-1].text, doc[-1].idx, self.name, None))
        # if a sentence ends in a quotation mark, the previous token also has to be
        # punctuation sign.
        elif doc[-1].text in TokenSet.CLOSING_QUOTATION_MARKS.value:
            if not (len(doc) > 1 and doc[-2].text in TokenSet.END_OF_SENTENCE_PUNCTUATION.value):
                errors.append(Error(doc[-1].text, doc[-1].idx, self.name, None))
        return errors


class IrregularPluralNounsCheck(RuleBasedGrammarCheck):
    """
    Checks if the plural of a noun is formed correctly.
    Examples:
        - the plural of "deer" is "deer" (not "deers")
        - the plural of "city" is "cities" (not "citys")
    """
    name = GrammarError.IRREGULAR_PLURAL_NOUN.value

    INCORRECT_PLURAL_SUFFIXES = set(["xs", "sss", "shs", "chs", "ys", "zs"])
    INCORRECT_PLURAL_REGEX = "(x|ss|sh|ch|zs|[^aeiou]y)s$"

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:

            if re.search(self.INCORRECT_PLURAL_REGEX, token.text.lower()):
                errors.append(Error(token.text, token.idx, self.name, None))

            # If the token is a plural verb
            elif token.tag_ == Tag.PLURAL_NOUN.value and \
                    token.text.lower() not in TokenSet.IRREGULAR_PLURAL_BLACKLIST.value:
                # If pyinflect does not return a plural form because
                # it does not know the noun
                # e.g. "wolfes" instead of "wolves"
                # if not token._.inflect(token.tag_):
                #    errors.append(Error(token.text, token.idx, self.name, token))
                # If the plural form is not the same as the one
                # returned by pyinflect
                # e.g. "deers" instead of "deer" returned by pyinflect
                correct_plurals = get_correct_plurals(token)
                if correct_plurals and \
                        token.text.lower() not in correct_plurals:
                    errors.append(Error(token.text, token.idx, self.name, None))

        return errors


class FragmentErrorCheck(RuleBasedGrammarCheck):
    """
    Identifies sentence fragments.
    """
    name = GrammarError.FRAGMENT.value

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for sentence in doc.sents:
            verb_deps = set([t.dep_ for t in sentence
                             if t.pos_ == POS.VERB.value or t.pos_ == POS.AUX.value])
            all_deps = set([t.dep_ for t in sentence])

            # If the sentence has a verb ROOT, everything is OK.
            if Dependency.ROOT.value in verb_deps:
                continue
            # If the sentence has a subject, everything is OK.
            elif Dependency.SUBJECT.value in all_deps or Dependency.PASS_SUBJECT.value in all_deps:
                continue
            else:
                errors.append(Error(sentence[-1].text,
                                    sentence[-1].idx,
                                    self.name,
                                    None))

        return errors


class PossessivePronounsErrorCheck(RuleBasedGrammarCheck):

    name = GrammarError.POSSESSIVE_PRONOUN.value

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            # Possessive pronouns with compound depencency
            if token.pos_ == POS.PRONOUN.value and \
                    token.dep_ == Dependency.COMPOUND.value:
                errors.append(Error(token.text, token.idx, self.name, None))
            elif token.tag_ == Tag.POSSESSIVE_PRONOUN.value and \
                    token.dep_ == Dependency.COMPOUND.value:
                errors.append(Error(token.text, token.idx, self.name, None))
            # Incorrect cases like "your's"
            elif token.text.lower() in TokenSet.INCORRECT_POSSESSIVE_PRONOUNS.value:
                errors.append(Error(token.text, token.idx, self.name, None))
            elif token.i < len(doc) - 1 and \
                    token.text_with_ws.lower() + doc[token.i+1].text.lower() \
                    in TokenSet.INCORRECT_POSSESSIVE_PRONOUNS.value:
                errors.append(Error(token.text, token.idx, self.name, None))

        return errors


class SubjectVerbAgreementErrorCheck(RuleBasedGrammarCheck):

    name = GrammarError.SUBJECT_VERB_AGREEMENT_RULE.value

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:

            # Infinitives are allowed: in "he would like to drive", "he" is
            # the subject and infinitive "drive" is the head.
            if is_subject(token) and token.tag_ == Tag.SINGULAR_NOUN.value and \
                    token.head.tag_ == Tag.PRESENT_OTHER_VERB.value:
                subject_lefts = [t.text.lower() for t in token.lefts] + [token.text.lower()]
                if len(set(subject_lefts).intersection(TokenSet.INDEF_PRONOUNS.value)) > 0:
                    error_type = GrammarError.SVA_INDEFINITE.value
                else:
                    error_type = GrammarError.SUBJECT_VERB_AGREEMENT_RULE.value

                errors.append(Error(token.head.text,
                                    token.head.idx,
                                    error_type,
                                    " ".join(subject_lefts)))

        return errors

# Collective grammar checks


class SubjectVerbAgreementWithCollectiveNounCheck(RuleBasedGrammarCheck):

    name = GrammarError.SVA_COLLECTIVE_NOUN.value

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            # If not third person singular
            if token.tag_ == Tag.PRESENT_OTHER_VERB.value or token.text.lower() == "were":
                subject = agreement.get_subject(token)
                if subject is not None and subject.text.lower() in TokenSet.COLLECTIVE_NOUNS.value:
                    full_subject = agreement.get_subject(token, full=True)
                    if full_subject is not None:
                        full_subject_string = " ".join([t.text.lower() for t in full_subject])
                    else:
                        full_subject_string = None
                    errors.append(Error(token.text,
                                        token.idx,
                                        self.name,
                                        full_subject_string))

        return errors


class RuleBasedGrammarChecker(object):
    """
    A grammar checker that performs all rule-based checks defined above.
    """

    def __call__(self, doc: Doc) -> List[Error]:
        return self.check(doc)

    def check(self, doc: Doc) -> List[Error]:
        grammar_checks = [
            RuleBasedPluralVsPossessiveCheck(),
            RuleBasedThisVsThatCheck(),
            RuleBasedQuestionMarkCheck(),
            RuleBasedSpacingCheck(),
            RuleBasedArticleCheck(),
            WomanVsWomenCheck(),
            ManVsMenCheck(),
            ThanVsThenCheck(),
            RepeatedWordCheck(),
            SubjectPronounCheck(),
            ObjectPronounCheck(),
            CommasInNumbersCheck(),
            CommasAfterYesNoCheck(),
            SingularPluralNounCheck(),
            CapitalizationCheck(),
            ContractionCheck(),
            IncorrectIrregularPastTenseCheck(),
            IncorrectParticipleCheck(),
            PunctuationCheck(),
            IrregularPluralNounsCheck(),
            FragmentErrorCheck(),
            PossessivePronounsErrorCheck(),
            SubjectVerbAgreementErrorCheck(),
            SubjectVerbAgreementWithCollectiveNounCheck()
            ]

        error_list = list(map(lambda x: x(doc), grammar_checks))
        error_list = [error for errors in error_list for error in errors]

        return error_list


class SpaCyGrammarChecker:
    """
    A grammar checker that combines both rule-based and statistical
    grammar error checking with spaCy.
    """

    def __init__(self, model_paths: List[str]):
        if len(model_paths) > 0:
            self.model = spacy.load(model_paths[0])

            # Replace the NER pipe of our model by spaCy's standard NER pipe.
            base_spacy = spacy.load(BASE_SPACY_MODEL)
            self.model.add_pipe(base_spacy.get_pipe("ner"), 'base_ner',
                                before="ner")

        self.alternative_models = []
        if len(model_paths) > 1:
            self.alternative_models = [spacy.load(model) for model in model_paths]

        self.rule_based_checker = RuleBasedGrammarChecker()
        self.sva_checker = UnsupervisedGrammarChecker()

    def clean_errors(self, errors: List[Error]) -> List[Error]:
        """
        Combine and clean errors. This fixes those cases in particular where
        one token has several errors and one takes precedence over the other.

        Args:
            errors:

        Returns:

        """
        errors_copy = [e for e in errors]
        for e in errors_copy:
            if e.type == GrammarError.PASSIVE_WITH_INCORRECT_BE.value and e.subject is None:
                errors.remove(e)

        if len(errors) > 0:
            #print(errors)
            errors.sort(key=lambda x: error_precedence.get(x.type, 0), reverse=True)
            return [errors[0]]
        return []

    def check(self, sentence: str) -> List[Error]:
        """
        Check a sentence for grammar errors.

        Args:
            sentence: the sentence that will be checked

        Returns: a list of errors. Every error is a tuple of (token,
                 token character offset, error type)

        """

        doc = self.model(sentence)

        # Get rule-based errors
        errors = self.rule_based_checker.check(doc)
        errors += self.sva_checker.check(sentence)

        # Add statistical errors
        """
        for token in doc:
            # Exclude spaCy's built-in entity types
            # (characterized by upper characters)
            if token.ent_type_:
                error_type = statistical_error_map.get(token.ent_type_, token.ent_type_)
                subject = agreement.get_subject(token, full=True)
                subject_string = " ".join([t.text.lower() for t in subject]) if subject is not None else None

                if error_type.isupper():
                    continue
                elif error_type == GrammarError.SUBJECT_VERB_AGREEMENT.value and token.tag_ == Tag.SIMPLE_PAST_VERB.value:
                    continue
                elif error_type == GrammarError.SUBJECT_VERB_AGREEMENT.value:
                    error_type, subject_string = classify_agreement_errors(token, error_type)
                    #error_type, subject_string = GrammarError.SVA_SEPARATE.value, None

                errors.append(Error(token.text,
                                    token.idx,
                                    error_type,
                                    subject_string),
                              )
        """

        for (i, model) in enumerate(self.alternative_models):

            alternative_doc = model(sentence)
            for token in alternative_doc:
                if token.ent_type_:
                    error_type = statistical_error_map.get(token.ent_type_, token.ent_type_)
                    subject = agreement.get_subject(token, full=True)
                    subject_string = " ".join([t.text.lower() for t in subject]) if subject is not None else None

                    """
                    if error_type == GrammarError.SUBJECT_VERB_AGREEMENT.value:
                        if subject is not None:
                            new_sentence = subject_string + " " + token.text.lower()
                            new_doc = model(new_sentence)
                            if len(new_doc.ents) == 0:
                                continue
                    """

                    if error_type.isupper():
                        continue
                    elif error_type == GrammarError.SUBJECT_VERB_AGREEMENT.value and token.tag_ == Tag.SIMPLE_PAST_VERB.value:
                        continue
                    elif error_type == GrammarError.SUBJECT_VERB_AGREEMENT.value:
                        continue
                    #elif error_type == GrammarError.PERFECT_TENSE_WITH_SIMPLE_PAST.value:
                    #    continue
                    #    error_type, subject_string = classify_agreement_errors(token, error_type)

                    errors.append(Error(token.text,
                                        token.idx,
                                        error_type,
                                        subject_string),
                                  )

        cleaned_errors = self.clean_errors(errors)

        return cleaned_errors


class BertGrammarChecker:
    """
    A grammar checker that combines both rule-based and statistical
    grammar error checking with BERT.
    """

    def __init__(self, model_path: str, config_path: str):
        self.rule_based_checker = RuleBasedGrammarChecker()
        self.spacy_model = spacy.load(BASE_SPACY_MODEL)

        print("Loading BERT model from", model_path)
        self.device = "cpu"

        with open(config_path) as i:
            config = json.load(i)

        self.label2idx = config["labels"]
        self.max_seq_length = config["max_seq_length"]

        self.idx2label = {v:k for k,v in self.label2idx.items()}

        self.tokenizer = BertTokenizer.from_pretrained(config["base_model"])
        model_state_dict = torch.load(model_path, map_location=lambda storage, loc: storage)
        self.model = BertForTokenClassification.from_pretrained(config["base_model"],
                                                                state_dict=model_state_dict,
                                                                num_labels=len(self.label2idx))
        self.model.to(self.device)

    def check(self, sentence: str) -> List[Error]:
        """
        Check a sentence for grammar errors.

        Args:
            sentence: the sentence that will be checked

        Returns: a list of errors. Every error is a tuple of (token,
                 token character offset, error type)

        """

        # Get rule-based errors
        doc = self.spacy_model(sentence)
        rule_errors = self.rule_based_checker(doc)

        preprocessed_sentence = convert_data_to_input_items([{"text": sentence}],
                                                            self.label2idx,
                                                            self.max_seq_length,
                                                            self.tokenizer,
                                                            NLPTask.SEQUENCE_LABELING)

        sentence_dl = get_data_loader(preprocessed_sentence, 1, NLPTask.SEQUENCE_LABELING, shuffle=False)
        _, _, _, predicted_errors = evaluate(self.model, sentence_dl, self.device)

        stat_errors = [self.idx2label[i] for i in set(predicted_errors[0])]
        stat_errors = [Error("", 0, statistical_error_map[e]) for e in stat_errors if e in statistical_error_map]

        return rule_errors + stat_errors

