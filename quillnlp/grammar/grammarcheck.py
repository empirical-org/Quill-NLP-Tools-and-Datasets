import re
import spacy
import pyinflect
import torch

from typing import List
from collections import namedtuple

from spacy.tokens.doc import Doc
from spacy.tokens.token import Token
from transformers import BertForTokenClassification, BertTokenizer

from quillnlp.models.bert.train import evaluate
from quillnlp.models.bert.preprocessing import preprocess_sequence_labelling, get_data_loader

BASE_SPACY_MODEL = "en"

# Tag, part-of-speech and dependency constants

POSSESSIVE_TAG = "POS"
PARTICIPLE_POS = "PART"
DETERMINER_POS = "DET"
VERB_POS = "VERB"
ADVERB_POS = "ADV"
PROPER_NOUN_POS = "PROPN"
PRONOUN_POS = "PRON"
AUX_POS = "AUX"
NOUN_POS = "NOUN"
PLURAL_NOUN_TAG = "NNS"
SINGULAR_NOUN_TAG = "NN"
YES_NO_TAG = "UH"
MODAL_VERB_TAG = "MD"
PRESENT_SING3_VERB_TAG = "VBZ"
PRESENT_OTHER_VERB_TAG = "VBP"
INFINITIVE_TAG = "VB"
POSSESSIVE_PRONOUN_TAG = "PRP$"
QUESTION_WORD_TAGS = set(["WP", "WP$", "WRB", "WDT"])
COORD_CONJ_POS = "CCONJ"
SUBJECT_DEP = "nsubj"
PASS_SUBJECT_DEP = "nsubjpass"
COMPOUND_DEP = "compound"
AUX_DEP = "aux"
ROOT_DEP = "ROOT"
CONJUNCTION_DEP = "conj"
DETERMINER_DEP = "det"
POSSIBLE_POS_IN_NOUN_PHRASE = set(["NOUN", "ADJ", "NUM",
                                   "ADP", "ADV", "PRON"])
COMPARATIVE_TAGS = set(["RBR", "JJR"])
DATE_ENT_TYPE = "DATE"

# Token constants

INDEF_ARTICLE_BEFORE_CONSONANT = "a"
INDEF_ARTICLE_BEFORE_VOWEL = "an"
THIS = "this"
THAT = "that"
THOSE = "those"
THESE = "these"
HERE = "here"
THERE = "there"
THEN = "then"
INCORRECT_PLURAL_WOMAN = "womans"
INCORRECT_PLURAL_MAN = "mans"

# Token set constants

QUESTION_MARK = "?"
PUNCTUATION_FOLLOWED_BY_SPACE = set([".", "!", "?", ")", ";", ":", ","])
PUNCTUATION_NOT_PRECEDED_BY_SPACE = set([".", "!", "?", ")", ";", ":", ","])
END_OF_SENTENCE_PUNCTUATION = set([".", "!", "?"])
INDEF_ARTICLES = set([INDEF_ARTICLE_BEFORE_VOWEL,
                      INDEF_ARTICLE_BEFORE_CONSONANT])
DEMONSTRATIVES = set([THIS, THAT, THOSE, THESE])
# we include "i." in the subject pronouns, because spaCy often
# mistokenizes i at the end of a sentence
SUBJECT_PRONOUNS = set(["i", "he", "she", "we", "they", "i."])
OBJECT_PRONOUNS = set(["me", "him", "her", "us", "them"])
POSSESSIVE_DETERMINERS = set(["my", "your", "her", "his",
                              "its", "our", "their"])
POSSESSIVE_PRONOUNS = set(["mine", "yours", "hers", "his", "ours", "theirs"])
YES_NO = set(["yes", "no"])
INCORRECT_CONTRACTIONS = set(["im", "youre", "hes", "shes", "theyre",
                              "dont", "didnt", "wont"])
CONTRACTED_VERBS_WITHOUT_APOSTROPHE = set(["m", "re", "s", "nt"])
# The words in the irregular plural blacklist have their own error
# type or given an incorrect plural with pyinflect (brother=>brethren)
IRREGULAR_PLURAL_BLACKLIST = set(["mans", "womans", "brothers"])
POSSESSIVE_S = set(["’s", "'s", "´s"])
INCORRECT_POSSESSIVE_PRONOUNS = set(["thier's", "thiers", "them's", "yous",
                                     "hims", "our's", "their's", "your's"])

# Error type constants

PLURAL_POSSESSIVE_ERROR = "Plural versus possessive nouns"
QUESTION_MARK_ERROR = "Question marks"
ARTICLE_ERROR = "Articles"
THIS_THAT_ERROR = "This versus that"
THESE_THOSE_ERROR = "These versus those"
SPACING_ERROR = "Spacing"
WOMAN_WOMEN_ERROR = "Woman versus women"
MAN_MEN_ERROR = "Man versus men"
THAN_THEN_ERROR = "Than versus then"
REPEATED_WORD_ERROR = "Repeated word"
SUBJECT_PRONOUN_ERROR = "Subject pronouns"
OBJECT_PRONOUN_ERROR = "Object pronouns"
POSSESSIVE_NOUN_ERROR = "Possessive nouns"
COMMAS_IN_NUMBERS_ERROR = "Commas in numbers"
YES_NO_COMMA_ERROR = "Commas after yes & no"
SINGULAR_PLURAL_ERROR = "Singular and plural nouns"
CAPITALIZATION_ERROR = "Capitalization"
CONTRACTION_ERROR = "Contractions"
ITS_IT_S_ERROR = "Its versus it's"
VERB_TENSE_ERROR = "Verb tense"
PUNCTUATION_ERROR = "Punctuation"
CHILD_CHILDREN_ERROR = "Child versus children"
ADVERB_ERROR = "Adverbs versus adjectives"
SUBJECT_VERB_AGREEMENT_ERROR = "Subject-verb agreement (stats)"
SUBJECT_VERB_AGREEMENT_ERROR2 = "Subject-verb agreement (rule)"
IRREGULAR_PLURAL_NOUN_ERROR = "Irregular plural nouns"
FRAGMENT_ERROR = "Fragment"
POSSESSIVE_PRONOUN_ERROR = "Possessive pronouns"


Token.set_extension("grammar_errors", default=[])

statistical_error_map = {"WOMAN": WOMAN_WOMEN_ERROR,
                         "ITS": ITS_IT_S_ERROR,
                         "THEN": THAN_THEN_ERROR,
                         "POSSESSIVE": PLURAL_POSSESSIVE_ERROR,
                         "CHILD": CHILD_CHILDREN_ERROR,
                         "ADV": ADVERB_ERROR,
                         "VERB": SUBJECT_VERB_AGREEMENT_ERROR}

Error = namedtuple("Error", ["text", "index", "type"])


# Utility methods


def is_subject(token):
    if token.dep_.startswith(SUBJECT_DEP):
        return True
    elif token.dep_ == CONJUNCTION_DEP and \
            token.head.dep_.startswith(SUBJECT_DEP):
        return True
    else:
        return False


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

    name = PLURAL_POSSESSIVE_ERROR

    def check(self, doc: Doc) -> List[Error]:
        # TODO: this does not treat cases like "it's my cousin's" correctly.
        errors = []
        for i in range(0, len(doc) - 1):
            if doc[i].text.lower() in POSSESSIVE_S and \
                    (doc[i].tag_ == POSSESSIVE_TAG or
                     doc[i].pos_ == PARTICIPLE_POS) and \
                    (doc[i + 1].pos_ not in [NOUN_POS, COORD_CONJ_POS]):
                errors.append(Error(doc[i].text, doc[i].idx, self.name))
            elif doc[i].tag_ == PLURAL_NOUN_TAG and doc[i+1].pos_ == NOUN_POS:
                errors.append(Error(doc[i].text, doc[i].idx, self.name))

        return errors


class RuleBasedQuestionMarkCheck(RuleBasedGrammarCheck):
    """
    Identifies questions that do not have a question mark.
    """

    name = QUESTION_MARK_ERROR

    def check(self, doc: Doc) -> List[Error]:
        # TODO: should also catch "Is he going to dance tonight." with AUX
        errors = []
        if doc[-1].text != QUESTION_MARK:
            # Cases like: When will she come home?
            if doc[0].tag_ in QUESTION_WORD_TAGS:
                errors.append(Error(doc[-1].text, doc[-1].idx, self.name))
            # Cases like: Will he come home?
            elif doc[0].pos_ == VERB_POS and doc[0].dep_ == AUX_DEP:
                errors.append(Error(doc[-1].text, doc[-1].idx, self.name))
            # Cases like: Is he dead?
            elif doc[0].pos_ == AUX_POS and doc[0].dep_ == ROOT_DEP:
                errors.append(Error(doc[-1].text, doc[-1].idx, self.name))
            # Cases like: Is Laura playing softball tomorrow?
            elif doc[0].pos_ == AUX_POS and doc[0].dep_ == AUX_DEP:
                errors.append(Error(doc[-1].text, doc[-1].idx, self.name))
            # Other cases where the subject follows its head
            else:
                for token in doc:
                    if token.dep_.startswith(SUBJECT_DEP) and \
                            token.i > token.head.i:
                        errors.append(Error(doc[-1].text,
                                            doc[-1].idx,
                                            self.name))
                        break
                    # as soon as we meet a subject before we meet a verb,
                    # stop looking
                    elif token.dep_.startswith(SUBJECT_DEP) and \
                            token.i < token.head.i:
                        break

        return errors


class RuleBasedArticleCheck(RuleBasedGrammarCheck):
    """
    Identifies instances where determiner "a" is followed by a vowel, or
    "an" is followed by a consonant.
    """

    name = ARTICLE_ERROR

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc[:-1]:
            if token.pos_ == DETERMINER_POS and \
                    token.text.lower() == INDEF_ARTICLE_BEFORE_CONSONANT \
                    and self._starts_with_vowel(doc[token.i + 1].text):
                errors.append(Error(token.text, token.idx, self.name))
            elif token.pos_ == DETERMINER_POS and \
                    token.text.lower() == INDEF_ARTICLE_BEFORE_VOWEL \
                    and not self._starts_with_vowel(doc[token.i + 1].text):
                errors.append(Error(token.text, token.idx, self.name))
        return errors

    def _starts_with_vowel(self, token: str) -> bool:
        # We leave out "u", because of "a useful", etc.
        if re.match("[aeio]", token, re.IGNORECASE):
            return True
        return False


class RuleBasedThisVsThatCheck(RuleBasedGrammarCheck):
    """
    Identifies errors like "this/these X there" or "that/those X here".
    """

    name = THIS_THAT_ERROR

    def check(self, doc: Doc) -> List[Error]:
        # It's not straightforward to rewrite this using spaCy's noun chunks
        # as "this table over there" is not a noun chunk, but "this table" is.

        errors = []
        current_noun_phrase = []
        for token in doc:
            if token.text.lower() in DEMONSTRATIVES and \
                    token.pos_ == DETERMINER_POS:
                current_noun_phrase = [token]
            elif token.pos_ in POSSIBLE_POS_IN_NOUN_PHRASE:
                current_noun_phrase.append(token)
                if token.text.lower() == HERE and \
                        current_noun_phrase[0].text.lower() == THAT:
                    errors.append(Error(current_noun_phrase[0].text,
                                        current_noun_phrase[0].idx,
                                        self.name))
                elif token.text.lower() == HERE and \
                        current_noun_phrase[0].text.lower() == THOSE:
                    errors.append(Error(current_noun_phrase[0].text,
                                        current_noun_phrase[0].idx,
                                        self.name))
                elif token.text.lower() == THERE and \
                        current_noun_phrase[0].text.lower() == THIS:
                    errors.append(Error(current_noun_phrase[0].text,
                                        current_noun_phrase[0].idx,
                                        self.name))
                elif token.text.lower() == THERE and \
                        current_noun_phrase[0].text.lower() == THESE:
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

    name = SPACING_ERROR

    def check(self, doc: Doc) -> List[Error]:
        errors = []

        # Punctuation not followed by a space
        for token in doc[:-1]:
            if token.text in PUNCTUATION_FOLLOWED_BY_SPACE and \
                    token.whitespace_ == "":
                errors.append(Error(token.text, token.idx, self.name))

        # Punctuation incorrectly preceded by a space
        for token in doc:
            if token.i > 0 and \
                    token.text in PUNCTUATION_NOT_PRECEDED_BY_SPACE and \
                    len(doc[token.i-1].whitespace_) > 0:
                errors.append(Error(token.text, token.idx, self.name))
            elif "." in token.text and re.search(r"\.\w", token.text):
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class WomanVsWomenCheck(RuleBasedGrammarCheck):
    """
    Identifies "womans" as the incorrect plural of "woman".
    """

    name = WOMAN_WOMEN_ERROR

    def check(self, doc: Doc) -> List[Error]:
        return [Error(t.text, t.idx, self.name) for t in doc
                if t.text.lower() == INCORRECT_PLURAL_WOMAN]


class ManVsMenCheck(RuleBasedGrammarCheck):
    """
    Identifies "mans" as the incorrect plural of "man".
    """

    name = MAN_MEN_ERROR

    def check(self, doc: Doc) -> List[Error]:
        return [Error(t.text, t.idx, self.name) for t in doc
                if t.text.lower() == INCORRECT_PLURAL_MAN]


class ThanVsThenCheck(RuleBasedGrammarCheck):
    """
    Identifies instances of "then" that should be "than".
    """

    name = THAN_THEN_ERROR

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc[1:]:
            if token.text.lower() == THEN and \
                    doc[token.i - 1].tag_ in COMPARATIVE_TAGS:
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class RepeatedWordCheck(RuleBasedGrammarCheck):
    """
    Identifies repeated words.
    """

    name = REPEATED_WORD_ERROR

    def check(self, doc: Doc) -> List[Error]:
        return [Error(t.text, t.idx, self.name) for t in doc[1:] if
                t.text.lower() == doc[t.i-1].text.lower()]


class SubjectPronounCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect subject pronouns (e.g. object pronouns,
    such as "me", possessive determiners such as "my" or possessive
    pronouns such as "mine").
    """

    name = SUBJECT_PRONOUN_ERROR

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        nonsubj_pronouns = OBJECT_PRONOUNS | \
            POSSESSIVE_DETERMINERS | \
            POSSESSIVE_PRONOUNS
        for token in doc:
            if is_subject(token) and token.text.lower() in nonsubj_pronouns:
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class ObjectPronounCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect object pronouns (e.g. subject pronouns, such as "I").
    """

    name = OBJECT_PRONOUN_ERROR

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            if token.text.lower() in SUBJECT_PRONOUNS and \
                    not is_subject(token):
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class CommasInNumbersCheck(RuleBasedGrammarCheck):
    """
    Identifies long numbers (more than 3 digits) that miss a comma.
    """

    name = COMMAS_IN_NUMBERS_ERROR

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            if re.search(r"^\d{4,}$", token.text) and \
                    not token.ent_type_ == DATE_ENT_TYPE:
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class CommasAfterYesNoCheck(RuleBasedGrammarCheck):
    """
    Identifies instances of yes/no that are not followed by a comma.
    """

    # TODO: "no symptoms"
    name = YES_NO_COMMA_ERROR

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc[:-1]:
            if token.text.lower() in YES_NO and \
                    token.tag_ == YES_NO_TAG and \
                    not doc[token.i+1].is_punct:
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class SingularPluralNounCheck(RuleBasedGrammarCheck):
    """
    Identifies sentences where a singular determiner (a, an) has as its head a
    plural noun.
    """

    name = SINGULAR_PLURAL_ERROR

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for noun_chunk in doc.noun_chunks:
            for token in noun_chunk:
                if token.text.lower() in INDEF_ARTICLES and \
                        token.dep_ == DETERMINER_DEP and \
                        token.head.tag_ == PLURAL_NOUN_TAG:
                    errors.append(Error(token.text, token.idx, self.name))
        return errors


class CapitalizationCheck(RuleBasedGrammarCheck):
    """
    Identifies cases where a sentence does not start with a capital letter, or
    "I" is not capitalized.
    """

    name = CAPITALIZATION_ERROR

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        if re.match("[a-z]", doc[0].text):
            doc[0]._.grammar_errors.append(CAPITALIZATION_ERROR)
            errors.append(Error(doc[0].text, doc[0].idx, self.name))
        for token in doc[1:]:
            if token.text == "i":
                errors.append(Error(token.text, token.idx, self.name))
            elif token.pos_ == PROPER_NOUN_POS and token.text.islower():
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class ContractionCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect contractions such as "Im" and "didnt".
    """

    name = CONTRACTION_ERROR

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            if token.text.lower() in INCORRECT_CONTRACTIONS:
                errors.append(Error(token.text, token.idx, self.name))
            elif token.pos_ in [VERB_POS, ADVERB_POS, PARTICIPLE_POS] and \
                    token.text.lower() in CONTRACTED_VERBS_WITHOUT_APOSTROPHE:
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class VerbTenseCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect verb forms, such as "bringed" and "writed".
    """

    name = VERB_TENSE_ERROR

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            # If the token is a past tense verb
            if token.pos_ == VERB_POS and not token.tag_ == MODAL_VERB_TAG:
                # If pyinflect does not return a verb form because it
                # does not know the lemma
                # e.g. "cutted" has unknown lemma "cutte"
                if not token._.inflect(token.tag_):
                    errors.append(Error(token.text, token.idx, self.name))
                # If the verb form is not the same as the one returned
                # by pyinflect
                # e.g. "bringed" instead of "brought"
                elif not token.text == token._.inflect(token.tag_):
                    errors.append(Error(token.text, token.idx, self.name))
        return errors


class PunctuationCheck(RuleBasedGrammarCheck):
    """
    Checks if a sentence ends in a punctuation mark.
    """

    name = PUNCTUATION_ERROR

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        if doc[-1].text not in END_OF_SENTENCE_PUNCTUATION:
            errors.append(Error(doc[-1].text, doc[-1].idx, self.name))
        return errors


class IrregularPluralNounsCheck(RuleBasedGrammarCheck):
    """
    Checks if the plural of a noun is formed correctly.
    Examples:
        - the plural of "deer" is "deer" (not "deers")
        - the plural of "city" is "cities" (not "citys")
    """
    name = IRREGULAR_PLURAL_NOUN_ERROR

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            # If the token is a plural verb
            if token.tag_ == PLURAL_NOUN_TAG and \
                    token.text.lower() not in IRREGULAR_PLURAL_BLACKLIST:
                # If pyinflect does not return a plural form because
                # it does not know the noun
                # e.g. "wolfes" instead of "wolves"
                # if not token._.inflect(token.tag_):
                #    errors.append(Error(token.text, token.idx, self.name))
                # If the plural form is not the same as the one
                # returned by pyinflect
                # e.g. "deers" instead of "deer" returned by pyinflect
                if token._.inflect(token.tag_) and \
                        not token.text == token._.inflect(token.tag_):
                    errors.append(Error(token.text, token.idx, self.name))
        return errors


class FragmentErrorCheck(RuleBasedGrammarCheck):
    """
    Identifies sentence fragments.
    """
    name = FRAGMENT_ERROR

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for sentence in doc.sents:
            verb_deps = set([t.dep_ for t in sentence
                             if t.pos_ == VERB_POS or t.pos_ == AUX_POS])
            all_deps = set([t.dep_ for t in sentence])

            # If the sentence has a verb ROOT, everything is OK.
            if ROOT_DEP in verb_deps:
                continue
            # If the sentence has a subject, everything is OK.
            elif SUBJECT_DEP in all_deps or PASS_SUBJECT_DEP in all_deps:
                continue
            else:
                errors.append(Error(sentence[-1].text,
                                    sentence[-1].idx,
                                    self.name))

        return errors


class PossessivePronounsErrorCheck(RuleBasedGrammarCheck):

    name = POSSESSIVE_PRONOUN_ERROR

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            if token.pos_ == PRONOUN_POS and \
                    token.dep_ == COMPOUND_DEP:
                errors.append(Error(token.text, token.idx, self.name))
            elif token.tag_ == POSSESSIVE_PRONOUN_TAG and \
                    token.dep_ == COMPOUND_DEP:
                errors.append(Error(token.text, token.idx, self.name))
            elif token.text.lower() in INCORRECT_POSSESSIVE_PRONOUNS:
                errors.append(Error(token.text, token.idx, self.name))
            elif token.i < len(doc) - 1 and \
                    token.text_with_ws.lower() + doc[token.i+1].text.lower() \
                    in INCORRECT_POSSESSIVE_PRONOUNS:
                errors.append(Error(token.text, token.idx, self.name))

        return errors


class SubjectVerbAgreementErrorCheck(RuleBasedGrammarCheck):

    name = SUBJECT_VERB_AGREEMENT_ERROR2

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:

            # Infinitives are allowed: in "he would like to drive", "he" is
            # the subject and infinitive "drive" is the head.
            if is_subject(token) and token.tag_ == SINGULAR_NOUN_TAG and \
                    token.head.tag_ == PRESENT_OTHER_VERB_TAG:
                errors.append(Error(token.head.text,
                                    token.head.idx,
                                    self.name))

        return errors

# Collective grammar checks


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
            VerbTenseCheck(),
            PunctuationCheck(),
            IrregularPluralNounsCheck(),
            FragmentErrorCheck(),
            PossessivePronounsErrorCheck(),
            SubjectVerbAgreementErrorCheck()
            ]

        error_list = list(map(lambda x: x(doc), grammar_checks))
        error_list = [error for errors in error_list for error in errors]

        return error_list


class SpaCyGrammarChecker:
    """
    A grammar checker that combines both rule-based and statistical
    grammar error checking with spaCy.
    """

    def __init__(self, model_path: str):
        self.model = spacy.load(model_path)
        # Replace the NER pipe of our model by spaCy's standard NER pipe.
        base_spacy = spacy.load(BASE_SPACY_MODEL)
        self.model.add_pipe(base_spacy.get_pipe("ner"), 'base_ner',
                            before="ner")
        self.rule_based_checker = RuleBasedGrammarChecker()

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
        errors = self.rule_based_checker(doc)

        # Add statistical errors
        for token in doc:
            # Exclude spaCy's built-in entity types
            # (characterized by upper characters)
            if token.ent_type_ and token.ent_type_ in statistical_error_map:
                errors.append(Error(token.text,
                                    token.idx,
                                    statistical_error_map.get(token.ent_type_,
                                                              token.ent_type_))
                              )

        return errors


class BertGrammarChecker:
    """
    A grammar checker that combines both rule-based and statistical
    grammar error checking with BERT.
    """

    def __init__(self, model_path: str):
        self.rule_based_checker = RuleBasedGrammarChecker()
        self.max_seq_length = 100
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-cased")
        self.spacy_model = spacy.load(BASE_SPACY_MODEL)

        print("Loading BERT model from", model_path)
        self.device = "cpu"
        self.label2idx = {'O': 0, 'POSSESSIVE': 1, 'VERB': 2, 'ADV': 3, 'WOMAN': 4, 'ITS': 5, 'THEN': 6, 'CHILD': 7}
        self.idx2label = {v:k for k,v in self.label2idx.items()}
        model_state_dict = torch.load(model_path, map_location=lambda storage, loc: storage)
        self.model = BertForTokenClassification.from_pretrained("bert-base-cased",
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

        preprocessed_sentence = preprocess_sequence_labelling([{"text": sentence}],
                                                              self.label2idx,
                                                              self.max_seq_length,
                                                              self.tokenizer)

        sentence_dl = get_data_loader(preprocessed_sentence, 1, shuffle=False)
        _, _, _, predicted_errors = evaluate(self.model, sentence_dl, self.device)

        stat_errors = [self.idx2label[i] for i in set(predicted_errors[0])]
        stat_errors = [Error("", 0, statistical_error_map[e]) for e in stat_errors if e in statistical_error_map]

        return rule_errors + stat_errors
