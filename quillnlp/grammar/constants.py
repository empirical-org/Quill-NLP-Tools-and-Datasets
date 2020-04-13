from enum import Enum

# Tag, part-of-speech and dependency constants


class Tag(Enum):
    POSSESSIVE = "POS"
    PLURAL_NOUN = "NNS"
    SINGULAR_NOUN = "NN"
    YES_NO = "UH"
    MODAL_VERB = "MD"
    PRESENT_SING3_VERB = "VBZ"
    PRESENT_OTHER_VERB = "VBP"
    INFINITIVE = "VB"
    POSSESSIVE_PRONOUN = "PRP$"
    WH_PRONOUN = "WP"
    POSSESSIVE_WH_PRONOUN = "WP$"
    WH_ADVERB = "WRB"
    WH_DETERMINER = "WDT"
    COMPARATIVE_ADJECTIVE = "JJR"
    COMPARATIVE_ADVERB = "JJR"


QUESTION_WORD_TAGS = set([Tag.WH_PRONOUN.value, Tag.POSSESSIVE_WH_PRONOUN.value,
                          Tag.WH_ADVERB.value, Tag.WH_DETERMINER.value])
COMPARATIVE_TAGS = set([Tag.COMPARATIVE_ADJECTIVE.value, Tag.COMPARATIVE_ADVERB.value])


class POS(Enum):
    PARTICIPLE = "PART"
    DETERMINER = "DET"
    ADJECTIVE = "ADJ"
    ADPOSITION = "ADP"
    NUMBER = "NUM"
    VERB = "VERB"
    ADVERB = "ADV"
    PROPER_NOUN = "PROPN"
    PRONOUN = "PRON"
    AUX = "AUX"
    NOUN = "NOUN"
    COORD_CONJ = "CCONJ"


POSSIBLE_POS_IN_NOUN_PHRASE = set([POS.NOUN.value, POS.ADJECTIVE.value,
                                   POS.NUMBER.value, POS.ADPOSITION.value,
                                   POS.ADVERB.value, POS.PRONOUN.value])


class Dependency(Enum):
    SUBJECT = "nsubj"
    PASS_SUBJECT = "nsubjpass"
    COMPOUND = "compound"
    AUX = "aux"
    ROOT = "ROOT"
    CONJUNCTION = "conj"
    DETERMINER = "det"


class EntityType(Enum):
    DATE = "DATE"

# Token constants


class Word(Enum):
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
    QUESTION_MARK = "?"

# Token set constants


class TokenSet(Enum):
    PUNCTUATION_FOLLOWED_BY_SPACE = set([".", "!", "?", ")", ";", ":", ","])
    PUNCTUATION_NOT_PRECEDED_BY_SPACE = set([".", "!", "?", ")", ";", ":", ","])
    END_OF_SENTENCE_PUNCTUATION = set([".", "!", "?"])
    INDEF_ARTICLES = set([Word.INDEF_ARTICLE_BEFORE_VOWEL.value,
                          Word.INDEF_ARTICLE_BEFORE_CONSONANT.value])
    DEMONSTRATIVES = set([Word.THIS.value, Word.THAT.value, Word.THOSE.value, Word.THESE.value])
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


class GrammarError(Enum):
    PLURAL_POSSESSIVE = "Plural versus possessive nouns"
    QUESTION_MARK = "Question marks"
    ARTICLE = "Articles"
    THIS_THAT = "This versus that"
    THESE_THOSE = "These versus those"
    SPACING = "Spacing"
    WOMAN_WOMEN = "Woman versus women"
    MAN_MEN = "Man versus men"
    THAN_THEN = "Than versus then"
    REPEATED_WORD = "Repeated word"
    SUBJECT_PRONOUN = "Subject pronouns"
    OBJECT_PRONOUN = "Object pronouns"
    POSSESSIVE_NOUN = "Possessive nouns"
    COMMAS_IN_NUMBERS = "Commas in numbers"
    YES_NO_COMMA = "Commas after yes & no"
    SINGULAR_PLURAL = "Singular and plural nouns"
    CAPITALIZATION = "Capitalization"
    CONTRACTION = "Contractions"
    ITS_IT_S = "Its versus it's"
    VERB_TENSE = "Verb tense"
    PUNCTUATION = "Punctuation"
    CHILD_CHILDREN = "Child versus children"
    ADVERB = "Adverbs versus adjectives"
    SUBJECT_VERB_AGREEMENT_STATS = "Subject-verb agreement (stats)"
    SUBJECT_VERB_AGREEMENT_RULE = "Subject-verb agreement (rule)"
    SUBJECT_VERB_AGREEMENT = "Subject-verb agreement"
    IRREGULAR_PLURAL_NOUN = "Irregular plural nouns"
    FRAGMENT = "Fragment"
    POSSESSIVE_PRONOUN = "Possessive pronouns"
