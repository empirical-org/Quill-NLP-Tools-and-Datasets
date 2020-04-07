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
from quillnlp.models.bert.preprocessing import convert_data_to_input_items, get_data_loader
from quillnlp.grammar.constants import *

BASE_SPACY_MODEL = "en"

Word.set_extension("grammar_errors", default=[])

statistical_error_map = {"WOMAN": GrammarError.WOMAN_WOMEN,
                         "ITS": GrammarError.ITS_IT_S,
                         "THEN": GrammarError.THAN_THEN,
                         "POSSESSIVE": GrammarError.PLURAL_POSSESSIVE,
                         "CHILD": GrammarError.CHILD_CHILDREN,
                         "ADV": GrammarError.ADVERB,
                         "VERB": GrammarError.SUBJECT_VERB_AGREEMENT}

Error = namedtuple("Error", ["text", "index", "type"])


# Utility methods


def is_subject(token):
    if token.dep_.startswith(Dependency.SUBJECT):
        return True
    elif token.dep_ == Dependency.CONJUNCTION and \
            token.head.dep_.startswith(Dependency.SUBJECT):
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

    name = GrammarError.PLURAL_POSSESSIVE

    def check(self, doc: Doc) -> List[Error]:
        # TODO: this does not treat cases like "it's my cousin's" correctly.
        errors = []
        for i in range(0, len(doc) - 1):
            if doc[i].text.lower() in TokenSet.POSSESSIVE_S and \
                    (doc[i].tag_ == Tag.POSSESSIVE or
                     doc[i].pos_ == POS.PARTICIPLE) and \
                    (doc[i + 1].pos_ not in [POS.NOUN, POS.COORD_CONJ]):
                errors.append(Error(doc[i].text, doc[i].idx, self.name))
            elif doc[i].tag_ == Tag.PLURAL_NOUN and doc[i+1].pos_ == POS.NOUN:
                errors.append(Error(doc[i].text, doc[i].idx, self.name))

        return errors


class RuleBasedQuestionMarkCheck(RuleBasedGrammarCheck):
    """
    Identifies questions that do not have a question mark.
    """

    name = GrammarError.QUESTION_MARK

    def check(self, doc: Doc) -> List[Error]:
        # TODO: should also catch "Is he going to dance tonight." with AUX
        errors = []
        if doc[-1].text != Word.QUESTION_MARK:
            # Cases like: When will she come home?
            if doc[0].tag_ in QUESTION_WORD_TAGS:
                errors.append(Error(doc[-1].text, doc[-1].idx, self.name))
            # Cases like: Will he come home?
            elif doc[0].pos_ == POS.VERB and doc[0].dep_ == Dependency.AUX:
                errors.append(Error(doc[-1].text, doc[-1].idx, self.name))
            # Cases like: Is he dead?
            elif doc[0].pos_ == POS.AUX and doc[0].dep_ == Dependency.ROOT:
                errors.append(Error(doc[-1].text, doc[-1].idx, self.name))
            # Cases like: Is Laura playing softball tomorrow?
            elif doc[0].pos_ == POS.AUX and doc[0].dep_ == Dependency.AUX:
                errors.append(Error(doc[-1].text, doc[-1].idx, self.name))
            # Other cases where the subject follows its head
            else:
                for token in doc:
                    if token.dep_.startswith(Dependency.SUBJECT) and \
                            token.i > token.head.i:
                        errors.append(Error(doc[-1].text,
                                            doc[-1].idx,
                                            self.name))
                        break
                    # as soon as we meet a subject before we meet a verb,
                    # stop looking
                    elif token.dep_.startswith(Dependency.SUBJECT) and \
                            token.i < token.head.i:
                        break

        return errors


class RuleBasedArticleCheck(RuleBasedGrammarCheck):
    """
    Identifies instances where determiner "a" is followed by a vowel, or
    "an" is followed by a consonant.
    """

    name = GrammarError.ARTICLE

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc[:-1]:
            if token.pos_ == POS.DETERMINER and \
                    token.text.lower() == Word.INDEF_ARTICLE_BEFORE_CONSONANT \
                    and self._starts_with_vowel(doc[token.i + 1].text):
                errors.append(Error(token.text, token.idx, self.name))
            elif token.pos_ == POS.DETERMINER and \
                    token.text.lower() == Word.INDEF_ARTICLE_BEFORE_VOWEL \
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

    name = GrammarError.THIS_THAT

    def check(self, doc: Doc) -> List[Error]:
        # It's not straightforward to rewrite this using spaCy's noun chunks
        # as "this table over there" is not a noun chunk, but "this table" is.

        errors = []
        current_noun_phrase = []
        for token in doc:
            if token.text.lower() in TokenSet.DEMONSTRATIVES and \
                    token.pos_ == POS.DETERMINER:
                current_noun_phrase = [token]
            elif token.pos_ in POSSIBLE_POS_IN_NOUN_PHRASE:
                current_noun_phrase.append(token)
                if token.text.lower() == Word.HERE and \
                        current_noun_phrase[0].text.lower() == Word.THAT:
                    errors.append(Error(current_noun_phrase[0].text,
                                        current_noun_phrase[0].idx,
                                        self.name))
                elif token.text.lower() == Word.HERE and \
                        current_noun_phrase[0].text.lower() == Word.THOSE:
                    errors.append(Error(current_noun_phrase[0].text,
                                        current_noun_phrase[0].idx,
                                        self.name))
                elif token.text.lower() == Word.THERE and \
                        current_noun_phrase[0].text.lower() == Word.THIS:
                    errors.append(Error(current_noun_phrase[0].text,
                                        current_noun_phrase[0].idx,
                                        self.name))
                elif token.text.lower() == Word.THERE and \
                        current_noun_phrase[0].text.lower() == Word.THESE:
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

    name = GrammarError.SPACING

    def check(self, doc: Doc) -> List[Error]:
        errors = []

        # Punctuation not followed by a space
        for token in doc[:-1]:
            if token.text in TokenSet.PUNCTUATION_FOLLOWED_BY_SPACE and \
                    token.whitespace_ == "":
                errors.append(Error(token.text, token.idx, self.name))

        # Punctuation incorrectly preceded by a space
        for token in doc:
            if token.i > 0 and \
                    token.text in TokenSet.PUNCTUATION_NOT_PRECEDED_BY_SPACE and \
                    len(doc[token.i-1].whitespace_) > 0:
                errors.append(Error(token.text, token.idx, self.name))
            elif "." in token.text and re.search(r"\.\w", token.text):
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class WomanVsWomenCheck(RuleBasedGrammarCheck):
    """
    Identifies "womans" as the incorrect plural of "woman".
    """

    name = GrammarError.WOMAN_WOMEN

    def check(self, doc: Doc) -> List[Error]:
        return [Error(t.text, t.idx, self.name) for t in doc
                if t.text.lower() == Word.INCORRECT_PLURAL_WOMAN]


class ManVsMenCheck(RuleBasedGrammarCheck):
    """
    Identifies "mans" as the incorrect plural of "man".
    """

    name = GrammarError.MAN_MEN

    def check(self, doc: Doc) -> List[Error]:
        return [Error(t.text, t.idx, self.name) for t in doc
                if t.text.lower() == Word.INCORRECT_PLURAL_MAN]


class ThanVsThenCheck(RuleBasedGrammarCheck):
    """
    Identifies instances of "then" that should be "than".
    """

    name = GrammarError.THAN_THEN

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc[1:]:
            if token.text.lower() == Word.THEN and \
                    doc[token.i - 1].tag_ in COMPARATIVE_TAGS:
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class RepeatedWordCheck(RuleBasedGrammarCheck):
    """
    Identifies repeated words.
    """

    name = GrammarError.REPEATED_WORD

    def check(self, doc: Doc) -> List[Error]:
        return [Error(t.text, t.idx, self.name) for t in doc[1:] if
                t.text.lower() == doc[t.i-1].text.lower()]


class SubjectPronounCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect subject pronouns (e.g. object pronouns,
    such as "me", possessive determiners such as "my" or possessive
    pronouns such as "mine").
    """

    name = GrammarError.SUBJECT_PRONOUN

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        nonsubj_pronouns = TokenSet.OBJECT_PRONOUNS | \
            TokenSet.POSSESSIVE_DETERMINERS | \
            TokenSet.POSSESSIVE_PRONOUNS
        for token in doc:
            if is_subject(token) and token.text.lower() in nonsubj_pronouns:
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class ObjectPronounCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect object pronouns (e.g. subject pronouns, such as "I").
    """

    name = GrammarError.OBJECT_PRONOUN

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            if token.text.lower() in TokenSet.SUBJECT_PRONOUNS and \
                    not is_subject(token):
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class CommasInNumbersCheck(RuleBasedGrammarCheck):
    """
    Identifies long numbers (more than 3 digits) that miss a comma.
    """

    name = GrammarError.COMMAS_IN_NUMBERS

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            if re.search(r"^\d{4,}$", token.text) and \
                    not token.ent_type_ == EntityType.DATE:
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class CommasAfterYesNoCheck(RuleBasedGrammarCheck):
    """
    Identifies instances of yes/no that are not followed by a comma.
    """

    # TODO: "no symptoms"
    name = GrammarError.YES_NO_COMMA

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc[:-1]:
            if token.text.lower() in TokenSet.YES_NO and \
                    token.tag_ == Tag.YES_NO and \
                    not doc[token.i+1].is_punct:
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class SingularPluralNounCheck(RuleBasedGrammarCheck):
    """
    Identifies sentences where a singular determiner (a, an) has as its head a
    plural noun.
    """

    name = GrammarError.SINGULAR_PLURAL

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for noun_chunk in doc.noun_chunks:
            for token in noun_chunk:
                if token.text.lower() in TokenSet.INDEF_ARTICLES and \
                        token.dep_ == Dependency.DETERMINER and \
                        token.head.tag_ == Tag.PLURAL_NOUN:
                    errors.append(Error(token.text, token.idx, self.name))
        return errors


class CapitalizationCheck(RuleBasedGrammarCheck):
    """
    Identifies cases where a sentence does not start with a capital letter, or
    "I" is not capitalized.
    """

    name = GrammarError.CAPITALIZATION

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        if re.match("[a-z]", doc[0].text):
            doc[0]._.grammar_errors.append(GrammarError.CAPITALIZATION)
            errors.append(Error(doc[0].text, doc[0].idx, self.name))
        for token in doc[1:]:
            if token.text == "i":
                errors.append(Error(token.text, token.idx, self.name))
            elif token.pos_ == POS.PROPER_NOUN and token.text.islower():
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class ContractionCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect contractions such as "Im" and "didnt".
    """

    name = GrammarError.CONTRACTION

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            if token.text.lower() in TokenSet.INCORRECT_CONTRACTIONS:
                errors.append(Error(token.text, token.idx, self.name))
            elif token.pos_ in [POS.VERB, POS.ADVERB, POS.PARTICIPLE] and \
                    token.text.lower() in TokenSet.CONTRACTED_VERBS_WITHOUT_APOSTROPHE:
                errors.append(Error(token.text, token.idx, self.name))
        return errors


class VerbTenseCheck(RuleBasedGrammarCheck):
    """
    Identifies incorrect verb forms, such as "bringed" and "writed".
    """

    name = GrammarError.VERB_TENSE

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            # If the token is a past tense verb
            if token.pos_ == POS.VERB and not token.tag_ == Tag.MODAL_VERB:
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

    name = GrammarError.PUNCTUATION

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        if doc[-1].text not in TokenSet.END_OF_SENTENCE_PUNCTUATION:
            errors.append(Error(doc[-1].text, doc[-1].idx, self.name))
        return errors


class IrregularPluralNounsCheck(RuleBasedGrammarCheck):
    """
    Checks if the plural of a noun is formed correctly.
    Examples:
        - the plural of "deer" is "deer" (not "deers")
        - the plural of "city" is "cities" (not "citys")
    """
    name = GrammarError.IRREGULAR_PLURAL_NOUN

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            # If the token is a plural verb
            if token.tag_ == Tag.PLURAL_NOUN and \
                    token.text.lower() not in TokenSet.IRREGULAR_PLURAL_BLACKLIST:
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
    name = GrammarError.FRAGMENT

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for sentence in doc.sents:
            verb_deps = set([t.dep_ for t in sentence
                             if t.pos_ == POS.VERB or t.pos_ == POS.AUX])
            all_deps = set([t.dep_ for t in sentence])

            # If the sentence has a verb ROOT, everything is OK.
            if Dependency.ROOT in verb_deps:
                continue
            # If the sentence has a subject, everything is OK.
            elif Dependency.SUBJECT in all_deps or Dependency.PASS_SUBJECT in all_deps:
                continue
            else:
                errors.append(Error(sentence[-1].text,
                                    sentence[-1].idx,
                                    self.name))

        return errors


class PossessivePronounsErrorCheck(RuleBasedGrammarCheck):

    name = GrammarError.POSSESSIVE_PRONOUN

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:
            if token.pos_ == POS.PRONOUN and \
                    token.dep_ == Dependency.COMPOUND:
                errors.append(Error(token.text, token.idx, self.name))
            elif token.tag_ == Tag.POSSESSIVE_PRONOUN and \
                    token.dep_ == Dependency.COMPOUND:
                errors.append(Error(token.text, token.idx, self.name))
            elif token.text.lower() in TokenSet.INCORRECT_POSSESSIVE_PRONOUNS:
                errors.append(Error(token.text, token.idx, self.name))
            elif token.i < len(doc) - 1 and \
                    token.text_with_ws.lower() + doc[token.i+1].text.lower() \
                    in TokenSet.INCORRECT_POSSESSIVE_PRONOUNS:
                errors.append(Error(token.text, token.idx, self.name))

        return errors


class SubjectVerbAgreementErrorCheck(RuleBasedGrammarCheck):

    name = GrammarError.SUBJECT_VERB_AGREEMENT_RULE

    def check(self, doc: Doc) -> List[Error]:
        errors = []
        for token in doc:

            # Infinitives are allowed: in "he would like to drive", "he" is
            # the subject and infinitive "drive" is the head.
            if is_subject(token) and token.tag_ == Tag.SINGULAR_NOUN and \
                    token.head.tag_ == Tag.PRESENT_OTHER_VERB:
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

        preprocessed_sentence = convert_data_to_input_items([{"text": sentence}],
                                                            self.label2idx,
                                                            self.max_seq_length,
                                                            self.tokenizer)

        sentence_dl = get_data_loader(preprocessed_sentence, 1, shuffle=False)
        _, _, _, predicted_errors = evaluate(self.model, sentence_dl, self.device)

        stat_errors = [self.idx2label[i] for i in set(predicted_errors[0])]
        stat_errors = [Error("", 0, statistical_error_map[e]) for e in stat_errors if e in statistical_error_map]

        return rule_errors + stat_errors
