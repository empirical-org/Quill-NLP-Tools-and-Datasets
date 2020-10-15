import re
import lemminflect

from typing import List
from collections import namedtuple
from lemminflect import getLemma

from spacy.tokens.doc import Doc
from spacy.tokens.token import Token

from ..verbutils import has_noun_subject, has_pronoun_subject, is_passive, in_have_been_construction, \
    get_past_tenses, has_inversion, get_subject, token_has_inversion, is_perfect
from ..constants import *
from ..utils import Error

BASE_SPACY_MODEL = "en"

Token.set_extension("grammar_errors", default=[])

statistical_error_map = {"WOMAN": GrammarError.WOMAN_WOMEN.value,
                         "ITS": GrammarError.POSSESSIVE_PRONOUN.value,
                         "THEN": GrammarError.THAN_THEN.value,
                         "POSSESSIVE": GrammarError.PLURAL_VERSUS_POSSESSIVE_NOUNS.value,
                         "CHILD": GrammarError.CHILD_CHILDREN.value,
                         "ADV": GrammarError.ADVERB.value}
                         #"VERB": GrammarError.SUBJECT_VERB_AGREEMENT.value}
                         

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

    def __call__(self, doc: Doc, prompt=""):
        return self.check(doc, prompt)

    def check(self, doc: Doc, prompt="") -> List[Error]:
        raise NotImplementedError


class RuleBasedPluralVsPossessiveCheck(RuleBasedGrammarCheck):
    """
    Identifies confusion between a possessive ("cousin's") and
    a plural ("cousins")
    """

    name = GrammarError.PLURAL_VERSUS_POSSESSIVE_NOUNS.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        # TODO: this does not treat cases like "it's my cousin's" correctly.
        errors = []
        for i in range(0, len(doc) - 1):
            if doc[i].text.lower() in TokenSet.POSSESSIVE_S.value and \
                    (doc[i].tag_ == Tag.POSSESSIVE.value or
                     doc[i].pos_ == POS.PARTICIPLE.value) and \
                    doc[i-1].pos_ == POS.NOUN.value and \
                    (doc[i + 1].pos_ not in [POS.NOUN.value, POS.COORD_CONJ.value]):
                errors.append(Error(doc[i].text, doc[i].idx, self.name))
#            elif doc[i].tag_ == Tag.PLURAL_NOUN.value and doc[i+1].pos_ == POS.NOUN.value:
#                errors.append(Error(doc[i].text, doc[i].idx, self.name))

        return errors


class RuleBasedQuestionMarkCheck(RuleBasedGrammarCheck):
    """
    Identifies questions that do not have a question mark.
    """

    name = GrammarError.QUESTION_MARK.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        # TODO: should also catch "Is he going to dance tonight." with AUX
        errors = []
        if doc[-1].text != Word.QUESTION_MARK.value:
            # Cases like: When will she come home?
            #if doc[0].tag_ in QUESTION_WORD_TAGS and doc[1].pos_ == POS.VERB.value:  # change
            #    errors.append(Error(doc[-1].text, doc[-1].idx, self.name, None))
            tags = set([t.tag_ for t in doc])

            if len(tags.intersection(QUESTION_WORD_TAGS)) > 0 and has_inversion(doc):
                errors.append(Error(doc[-1].text, doc[-1].idx, self.name))

            # Cases like: Will he come home?
            elif doc[0].pos_ == POS.VERB.value and doc[0].dep_ == Dependency.AUX.value:
                errors.append(Error(doc[-1].text, doc[-1].idx, self.name))
            # Cases like: Is he dead?
            elif doc[0].pos_ == POS.AUX.value:
                subject = get_subject(doc[0])
                if subject is not None and subject.i > 0:
                    errors.append(Error(doc[-1].text, doc[-1].idx, self.name))
            # Other cases where the subject follows its head
            else:  # change
                for token in doc:
                    if token.dep_.startswith(Dependency.SUBJECT.value) and \
                            token.i > token.head.i:
                        errors.append(Error(doc[-1].text,
                                            doc[-1].idx,
                                            self.name))
                        break
                    # as soon as we meet a subject before we meet a verb,
                    # stop looking
                    elif token.dep_.startswith(Dependency.SUBJECT.value) and \
                            token.i < token.head.i:
                        break

        return errors


class RuleBasedArticleCheck(RuleBasedGrammarCheck):
    """
    Identifies instances where determiner "a" is followed by a vowel, or
    "an" is followed by a consonant.
    """

    name = GrammarError.ARTICLE.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        errors = []
        for token in doc[:-1]:
            # if "a" before vowel
            if token.pos_ == POS.DETERMINER.value and \
                    token.text.lower() == Word.INDEF_ARTICLE_BEFORE_CONSONANT.value \
                    and self._starts_with_vowel(doc[token.i + 1].text):
                errors.append(Error(token.text, token.idx, self.name))
            # if "an" before consonant
            elif token.pos_ == POS.DETERMINER.value and \
                    token.text.lower() == Word.INDEF_ARTICLE_BEFORE_VOWEL.value \
                    and self._starts_with_consonant(doc[token.i + 1].text):
                errors.append(Error(token.text, token.idx, self.name))
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

    def check(self, doc: Doc, prompt="") -> List[Error]:
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
                                        self.name))
                elif token.text.lower() == Word.HERE.value and \
                        current_noun_phrase[0].text.lower() == Word.THOSE.value:
                    errors.append(Error(current_noun_phrase[0].text,
                                        current_noun_phrase[0].idx,
                                        self.name))
                elif token.text.lower() == Word.THERE.value and \
                        current_noun_phrase[0].text.lower() == Word.THIS.value:
                    errors.append(Error(current_noun_phrase[0].text,
                                        current_noun_phrase[0].idx,
                                        self.name))
                elif token.text.lower() == Word.THERE.value and \
                        current_noun_phrase[0].text.lower() == Word.THESE.value:
                    errors.append(Error(current_noun_phrase[0].text,
                                        current_noun_phrase[0].idx,
                                        self.name))
            else:
                current_noun_phrase = []

        return errors


class RuleBasedSpacingCheck(RuleBasedGrammarCheck):
    """
    Identifies punctuation that is not followed by a space
    or that is incorrectly preceded by a space.
    """

    name = GrammarError.SPACING.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        errors = []

        # Punctuation not followed by a space
        for token in doc[:-1]:
            if token.text in TokenSet.PUNCTUATION_FOLLOWED_BY_SPACE.value and \
                    token.whitespace_ == "" and not doc[token.i+1].is_punct:
                errors.append(Error(token.text, token.idx, self.name))

        # Punctuation incorrectly preceded by a space
        for token in doc:
            if token.i > 0 and \
                    token.text in TokenSet.PUNCTUATION_NOT_PRECEDED_BY_SPACE.value and \
                    len(doc[token.i-1].whitespace_) > 0:
                errors.append(Error(token.text, token.idx, self.name))

            # If a token contains a . followed by a letter, and this letter is not followed
            # by a space itself, it is also an error. This catches cases like
            # We went home.He did not.
            elif "." in token.text and re.search(r"\.[A-Z]", token.text) \
                    and not re.search(r"\.[A-Z]+\.", token.text):   # exclude D.C., T.S.
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class WomanVsWomenCheck(RuleBasedGrammarCheck):
    """
    Identifies "womans" as the incorrect plural of "woman".
    """

    name = GrammarError.WOMAN_WOMEN.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        return [Error(t.text, t.idx, self.name) for t in doc
                if t.text.lower() == Word.INCORRECT_PLURAL_WOMAN.value]


class ManVsMenCheck(RuleBasedGrammarCheck):
    """
    Identifies "mans" as the incorrect plural of "man".
    """

    name = GrammarError.MAN_MEN.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        return [Error(t.text, t.idx, self.name) for t in doc
                if t.text.lower() == Word.INCORRECT_PLURAL_MAN.value]


class ThanVsThenCheck(RuleBasedGrammarCheck):
    """
    Identifies instances of "then" that should be "than".
    """

    name = GrammarError.THAN_THEN.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        errors = []
        for token in doc[1:]:
            if token.text.lower() == Word.THEN.value and \
                    doc[token.i - 1].tag_ in COMPARATIVE_TAGS:
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class RepeatedWordCheck(RuleBasedGrammarCheck):
    """
    Identifies repeated words.
    """

    name = GrammarError.REPEATED_WORD.value

    exclude_words = set(["that", "had"])

    def check(self, doc: Doc, prompt="") -> List[Error]:
        errors = []
        for t in doc[1:]:
            if t.text.lower() not in self.exclude_words and t.text.lower() == doc[t.i-1].text.lower():
                errors.append(Error(t.text, t.idx, self.name))
        return errors


class SubjectPronounCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect subject pronouns (e.g. object pronouns,
    such as "me", possessive determiners such as "my" or possessive
    pronouns such as "mine").
    """

    name = GrammarError.SUBJECT_PRONOUN.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        errors = []
        nonsubj_pronouns = TokenSet.OBJECT_PRONOUNS.value | \
            TokenSet.POSSESSIVE_DETERMINERS.value | \
            TokenSet.POSSESSIVE_PRONOUNS.value
        for token in doc:
            #if is_subject(token) and token.text.lower() in nonsubj_pronouns:
            #    errors.append(Error(token.text, token.idx, self.name, None))
            if (token.pos_ == POS.VERB.value or token.pos_ == POS.AUX.value) \
                    and token.tag_ != Tag.INFINITIVE.value:
                subject = get_subject(token, full=True)
                if subject and len(subject) == 1 and subject[0].text.lower() in nonsubj_pronouns:
                    errors.append(Error(subject[0].text, subject[0].idx, self.name))

        return errors


class ObjectPronounCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect object pronouns (e.g. subject pronouns, such as "I").
    """

    name = GrammarError.OBJECT_PRONOUN.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        errors = []
        for token in doc:
            if token.text.lower() in TokenSet.SUBJECT_PRONOUNS.value and \
                    not is_subject(token):
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class CommasInNumbersCheck(RuleBasedGrammarCheck):
    """
    Identifies long numbers (more than 3 digits) that miss a comma.
    """

    name = GrammarError.COMMAS_IN_NUMBERS.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        errors = []
        for token in doc:
            # If there are 4 digits, we have to exclude dates
            if re.search(r"^\d{4}$", token.text):
                if token.ent_type_ == EntityType.DATE.value or \
                         1900 < int(token.text) < 2200:
                    continue
                else:
                    errors.append(Error(token.text, token.idx, self.name))
            # Otherwise, we flag all tokens as incorrect when they have 4 digits
            # that follow each other without a comma, unless they end in "s",
            # as in "the 1800s".
            elif re.search(r"\d{4,}", token.text) and not token.text.endswith("s"):
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class CommasAfterYesNoCheck(RuleBasedGrammarCheck):
    """
    Identifies instances of yes/no that are not followed by a comma.
    """

    name = GrammarError.YES_NO_COMMA.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        errors = []
        for token in doc[:-1]:
            if token.text.lower() in TokenSet.YES_NO.value and \
                    token.tag_ == Tag.YES_NO.value and \
                    not doc[token.i+1].is_punct:
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class SingularPluralNounCheck(RuleBasedGrammarCheck):
    """
    Identifies sentences where a singular determiner (a, an) has as its head a
    plural noun.
    """

    name = GrammarError.SINGULAR_PLURAL.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        errors = []
        for noun_chunk in doc.noun_chunks:
            for token in noun_chunk:
                if (token.text.lower() in ["a", "an"] or token.text.lower() in TokenSet.SINGULAR_DETERMINERS.value) and \
                        token.dep_ == Dependency.DETERMINER.value and \
                        token.head.tag_ == Tag.PLURAL_NOUN.value:
                    errors.append(Error(token.text, token.idx, self.name))
        return errors


class CapitalizationCheck(RuleBasedGrammarCheck):
    """
    Identifies cases where a sentence does not start with a capital letter, or
    "I" is not capitalized. Also identifies uses of allcaps.
    """

    name = GrammarError.CAPITALIZATION.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        errors = []

        if re.match("[a-z]", doc[0].text):
            doc[0]._.grammar_errors.append(GrammarError.CAPITALIZATION.value)
            errors.append(Error(doc[0].text, doc[0].idx, self.name))
        for token in doc[1:]:
            if token.text == "i":
                errors.append(Error(token.text, token.idx, self.name))

            # Ideally, we'd like to check if the token is a proper noun, but
            # spaCy is just not good enough at this. In the future, we may
            # have a check for capitalization statistics in a large reference
            # corpus.
            #elif token.pos_ == POS.PROPER_NOUN.value and token.text.islower():
            #    errors.append(Error(token.text, token.idx, self.name, None))

        doc_without_prompt = doc.text[len(prompt):]
        if doc_without_prompt.isupper():
            errors.append(Error(doc_without_prompt, len(prompt), self.name))

        return errors


class ContractionCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect contractions such as "Im" and "didnt".
    """

    name = GrammarError.CONTRACTION.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        errors = []
        for token in doc:
            # If the token is in our list of incorrect contractions,
            # it's an error
            if token.text.lower() in TokenSet.INCORRECT_CONTRACTIONS.value:
                errors.append(Error(token.text, token.idx, self.name))

            # If the token is a contracted verb without an apostrophe,
            # it's an error, unless it is followed by a "-", as in "re-open".
            elif token.pos_ in [POS.VERB.value, POS.ADVERB.value, POS.PARTICIPLE.value] and \
                    token.text.lower() in TokenSet.CONTRACTED_VERBS_WITHOUT_APOSTROPHE.value and \
                    not (len(doc) > token.i+1 and doc[token.i+1].text == "-"):
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class IncorrectIrregularPastTenseCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect verb forms, such as "bringed" and "writed".
    """

    name = GrammarError.INCORRECT_IRREGULAR_PAST_TENSE.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        errors = []
        for token in doc:
            # If the token is a past tense verb
            if token.tag_ == Tag.SIMPLE_PAST_VERB.value:
                past_tenses = get_past_tenses(token)

                if is_passive(token):
                    error_type = GrammarError.INCORRECT_PAST_TENSE_AS_PARTICIPLE_IN_PASSIVE.value
                else:
                    error_type = GrammarError.INCORRECT_IRREGULAR_PAST_TENSE.value

                # We exclude 'been' to avoid confusion with Passive perfect without have
                if not token.text.lower() in past_tenses and not token.text.lower() == "been":
                    errors.append(Error(token.text, token.idx, error_type))
        return errors


class IncorrectParticipleCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect verb forms, such as "bringed" and "writed".
    """

    name = GrammarError.INCORRECT_PARTICIPLE.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
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
                        error_type = GrammarError.PASSIVE_WITH_SIMPLE_PAST_INSTEAD_OF_PARTICIPLE.value  #TODO: sth strange here: in the second case below, it cannot be in the correct_past_tenses
                    else:
                        error_type = GrammarError.PASSIVE_WITH_INCORRECT_PARTICIPLE.value
                elif is_perfect(token):
                    error_type = GrammarError.PERFECT_TENSE_WITH_INCORRECT_SIMPLE_PAST.value
                else:
                    error_type = GrammarError.PERFECT_WITH_INCORRECT_PARTICIPLE.value

                # If pyinflect does not return a verb form because it
                # does not know the lemma
                # e.g. "cutted" has unknown lemma "cutte"
                if correct_participles == [None]:
                    errors.append(Error(token.text, token.idx, error_type))

                # If the verb form is not the same as the one returned
                # by pyinflect
                # e.g. "bringed" instead of "brought"
                elif token.text not in correct_participles and \
                        token.text not in correct_past_tenses:
                    errors.append(Error(token.text, token.idx, error_type))
        return errors


class PunctuationCheck(RuleBasedGrammarCheck):
    """
    Checks if a sentence ends in a punctuation mark.
    """

    name = GrammarError.PUNCTUATION.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        errors = []
        if doc[-1].text not in TokenSet.END_OF_SENTENCE_PUNCTUATION.value:
            errors.append(Error(doc[-1].text, doc[-1].idx, self.name))
        # if a sentence ends in a quotation mark, the previous token also has to be
        # punctuation sign.
        elif doc[-1].text in TokenSet.CLOSING_QUOTATION_MARKS.value:
            if not (len(doc) > 1 and doc[-2].text in TokenSet.END_OF_SENTENCE_PUNCTUATION.value):
                errors.append(Error(doc[-1].text, doc[-1].idx, self.name))
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

    def check(self, doc: Doc, prompt="") -> List[Error]:
        errors = []
        for token in doc:

            if re.search(self.INCORRECT_PLURAL_REGEX, token.text.lower()):
                errors.append(Error(token.text, token.idx, self.name))

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
                    errors.append(Error(token.text, token.idx, self.name))

        return errors


class FragmentErrorCheck(RuleBasedGrammarCheck):
    """
    Identifies sentence fragments.
    """
    name = GrammarError.FRAGMENT.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
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
                                    self.name))

        return errors


class PossessivePronounsErrorCheck(RuleBasedGrammarCheck):

    name = GrammarError.POSSESSIVE_PRONOUN.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        errors = []
        for token in doc:
            # Possessive pronouns with compound depencency
            if token.pos_ == POS.PRONOUN.value and \
                    token.dep_ == Dependency.COMPOUND.value:
                errors.append(Error(token.text, token.idx, self.name))
            elif token.tag_ == Tag.POSSESSIVE_PRONOUN.value and \
                    token.dep_ == Dependency.COMPOUND.value:
                errors.append(Error(token.text, token.idx, self.name))
            # Incorrect cases like "your's"
            elif token.text.lower() in TokenSet.INCORRECT_POSSESSIVE_PRONOUNS.value:
                errors.append(Error(token.text, token.idx, self.name))
            elif token.i < len(doc) - 1 and \
                    token.text_with_ws.lower() + doc[token.i+1].text.lower() \
                    in TokenSet.INCORRECT_POSSESSIVE_PRONOUNS.value:
                errors.append(Error(token.text, token.idx, self.name))

        return errors


class SubjectVerbAgreementErrorCheck(RuleBasedGrammarCheck):

    name = GrammarError.SUBJECT_VERB_AGREEMENT_RULE.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
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
                                    subject=" ".join(subject_lefts)))

        return errors

# Collective grammar checks


class SubjectVerbAgreementWithCollectiveNounCheck(RuleBasedGrammarCheck):

    name = GrammarError.SVA_COLLECTIVE_NOUN.value

    def check(self, doc: Doc, prompt="") -> List[Error]:
        errors = []
        for token in doc:
            # If not third person singular
            if token.tag_ == Tag.PRESENT_OTHER_VERB.value or token.text.lower() == "were":
                subject = get_subject(token)
                if subject is not None and subject.text.lower() in TokenSet.COLLECTIVE_NOUNS.value:
                    full_subject = get_subject(token, full=True)
                    if full_subject is not None:
                        full_subject_string = " ".join([t.text.lower() for t in full_subject])
                    else:
                        full_subject_string = None
                    errors.append(Error(token.text,
                                        token.idx,
                                        self.name,
                                        subject=full_subject_string))

        return errors


class RuleBasedGrammarChecker(object):
    """
    A grammar checker that performs all rule-based checks defined above.
    """

    candidate_checks = {
        RuleBasedPluralVsPossessiveCheck.name: RuleBasedPluralVsPossessiveCheck(),
        RuleBasedThisVsThatCheck.name: RuleBasedThisVsThatCheck(),
        RuleBasedQuestionMarkCheck.name: RuleBasedQuestionMarkCheck(),
        RuleBasedSpacingCheck.name: RuleBasedSpacingCheck(),
        RuleBasedArticleCheck.name: RuleBasedArticleCheck(),
        WomanVsWomenCheck.name: WomanVsWomenCheck(),
        ManVsMenCheck.name: ManVsMenCheck(),
        ThanVsThenCheck.name: ThanVsThenCheck(),
        RepeatedWordCheck.name: RepeatedWordCheck(),
        SubjectPronounCheck.name: SubjectPronounCheck(),
        ObjectPronounCheck.name: ObjectPronounCheck(),
        CommasInNumbersCheck.name: CommasInNumbersCheck(),
        CommasAfterYesNoCheck.name: CommasAfterYesNoCheck(),
        SingularPluralNounCheck.name: SingularPluralNounCheck(),
        CapitalizationCheck.name: CapitalizationCheck(),
        ContractionCheck.name: ContractionCheck(),
        IncorrectIrregularPastTenseCheck.name: IncorrectIrregularPastTenseCheck(),
        IncorrectParticipleCheck.name: IncorrectParticipleCheck(),
        PunctuationCheck.name: PunctuationCheck(),
        IrregularPluralNounsCheck.name: IrregularPluralNounsCheck(),
        FragmentErrorCheck.name: FragmentErrorCheck(),
        PossessivePronounsErrorCheck.name: PossessivePronounsErrorCheck(),
        SubjectVerbAgreementWithCollectiveNounCheck.name: SubjectVerbAgreementWithCollectiveNounCheck()
    }

    def __init__(self, config={}):
        self.unclassified = False
        self.name = "rules"

        self.grammar_checks = set([
            self.candidate_checks.get(check) for check in config["errors"] if check in self.candidate_checks
        ])

        print("Initialized rule-based Error Check for these errors:")
        for check in self.candidate_checks:
            if self.candidate_checks.get(check) in self.grammar_checks:
                print(f"[x] {check}")
            else:
                print(f"[ ] {check}")

    def __call__(self, doc: Doc) -> List[Error]:
        return self.check(doc)

    def check(self, doc: Doc, prompt: str = "") -> List[Error]:

        error_list = list(map(lambda x: x(doc, prompt), self.grammar_checks))
        error_list = [error for errors in error_list for error in errors
                      if error.index > len(prompt)-1]

        for error in error_list:
            error.model = self.name

        return error_list