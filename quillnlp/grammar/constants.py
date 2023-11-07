from enum import Enum

# Tag, part-of-speech and dependency constants


class Tag(Enum):
    POSSESSIVE = "POS"
    PLURAL_NOUN = "NNS"
    SINGULAR_NOUN = "NN"
    YES_NO = "UH"
    MODAL_VERB = "MD"
    PRESENT_SING3_VERB = "VBZ"
    PAST_PARTICIPLE_VERB = "VBN"
    SIMPLE_PAST_VERB = "VBD"
    PRESENT_OTHER_VERB = "VBP"
    PRESENT_PARTICIPLE_VERB = "VBG"
    INFINITIVE = "VB"
    POSSESSIVE_PRONOUN = "PRP$"
    WH_PRONOUN = "WP"
    POSSESSIVE_WH_PRONOUN = "WP$"
    WH_ADVERB = "WRB"
    WH_DETERMINER = "WDT"
    COMPARATIVE_ADJECTIVE = "JJR"
    COMPARATIVE_ADVERB = "JJR"



PRESENT_VERB_TAGS = set([Tag.PRESENT_SING3_VERB.value,
                         Tag.PRESENT_OTHER_VERB.value,
                         Tag.INFINITIVE.value])
PAST_VERB_TAGS = set([Tag.PAST_PARTICIPLE_VERB.value,
                      Tag.PAST_PARTICIPLE_VERB.value])

QUESTION_WORD_TAGS = set([Tag.WH_PRONOUN.value, Tag.POSSESSIVE_WH_PRONOUN.value,
                          Tag.WH_ADVERB.value, Tag.WH_DETERMINER.value])
COMPARATIVE_TAGS = set([Tag.COMPARATIVE_ADJECTIVE.value, Tag.COMPARATIVE_ADVERB.value])
RELATIVE_PRONOUN_TAGS = set([Tag.WH_PRONOUN.value, Tag.WH_ADVERB.value, Tag.WH_DETERMINER.value])

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
    DIRECT_OBJECT = "dobj"
    CLAUSAL_SUBJECT = "csubj"
    PASS_AUXILIARY = "auxpass"
    COMPOUND = "compound"
    AUX = "aux"
    ROOT = "ROOT"
    CONJUNCTION = "conj"
    DETERMINER = "det"
    ADVERBIAL_CLAUSE = "advcl"
    ATTRIBUTE = "attr"
    CCOMP = "ccomp"
    EXPLETIVE = "expl"


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
    PUNCTUATION_NOT_PRECEDED_BY_SPACE = set([".", "!", "?", ")", ";", ":", ",", "%"])
    END_OF_SENTENCE_PUNCTUATION = set([".", "!", "?", '"', '”', "'"])
    CLOSING_QUOTATION_MARKS = set(['"', '”', "'"])
    SINGULAR_DETERMINERS = set(["every", "none", "nothing", "each", "another", "one", "little",
                                "much"])
    INDEF_PRONOUNS = set(["every", "none", "all", "nothing", "some", "each", "any", "another",
                          "anybody", "anyone", "anything", "somebody", "other", "enough", "everyone",
                          "everybody", "everything", "something", "one", "less", "little", "much",
                          "nobody", "both", "few", "someone", "one",
                          "fewer", "many", "others", "several", "more", "such", "most", "nowhere", "everywhere"])
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
                                  "dont", "didnt", "wont", "id", "youd", "hed",
                                  "theyd", "youll", "theyll", "shell", "havent",
                                  "couldve"])
    CONTRACTED_VERBS_WITHOUT_APOSTROPHE = set(["m", "re", "s", "nt", "ll", "d", "ve"])
    # The words in the irregular plural blacklist have their own error
    # type or given an incorrect plural with pyinflect (brother=>brethren)
    IRREGULAR_PLURAL_BLACKLIST = set(["mans", "womans", "brothers"])
    POSSESSIVE_S = set(["’s", "'s", "´s"])
    INCORRECT_POSSESSIVE_PRONOUNS = set(["i's", "me's",
                                         "yous", "you's", "your's",
                                         "him's", "hims", "hes", "his's"
                                         "her's", "shes",
                                         "wes", "we's", "us's", "our's",
                                         "their's", "them's", "thems", "their's", "thiers"])
    COLLECTIVE_NOUNS = set(["group", "flock", "herd", "team", "pair", "choir", "family",
                            "mob", "line", "queue", "crew", "troop", "swarm", "bunch",
                            "circle", "troupe", "committee", "assembly", "senate", "council",
                            "fleet", "gang", "cluster", "clump", "board", "pride", "company",
                            "club", "pack", "litter", "pile", "slew", "body", "army", "host",
                            "school", "band", "crowd", "staff", "tribe", "class", "congress",
                            "audience", "parliament", "congregation", "chamber"," range",
                            "flight", "gaggle", "colony", "horde"])
    MUTUALLY_EXCLUSIVE_BE_FORMS = set(["be", "am", "are", "is", "been"])
    MUTUALLY_EXCLUSIVE_BE_FORMS_PAST = set(["was", "were"])
    BE_FORMS = set(["be", "am", "are", "is", "been", "was", "were"])
    SINGULAR_COUNT_WORDS = set(["few", "couple"])
    SINGULAR_NOUNS_THAT_LOOK_LIKE_PLURALS = set(["means", "species"])


# Error type constants


class GrammarError(Enum):
    THEIR = "their_vs_there_vs_they_re"
    THEIR_THEIR_OPTIMAL = "their_vs_there_vs_they_re_their_optimal"
    THEIR_THERE_OPTIMAL = "their_vs_there_vs_they_re_there_optimal"
    THEIR_THEYRE_OPTIMAL = "their_vs_there_vs_they_re_they_re_optimal"
    TO_TWO_TOO = "to_vs_too_vs_two"
    TO_TWO_TOO_TO_OPTIMAL = "to_vs_too_vs_two_to_optimal"
    TO_TWO_TOO_TWO_OPTIMAL = "to_vs_too_vs_two_two_optimal"
    TO_TWO_TOO_TOO_OPTIMAL = "to_vs_too_vs_two_too_optimal"
    YOURE_YOUR = "you_re_vs_your"
    WHOS_WHOSE = "who_s_vs_whose"

    ACCEPT_EXCEPT = "accept_vs_except"
    AFFECT_EFFECT = "affect_vs_effect"
    PASSED_PAST = "passed_vs_past"
    LEAD_LED = "lead_vs_led"
    LOOSE_LOSE = "loose_vs_lose"
    FURTHER_FARTHER = "further_vs_farther"
    ADVISE_ADVICE = "advise_vs_advice"
    ELICIT_ILLICIT = "elicit_vs_illicit"
    COUNCIL_COUNSEL = "council_vs_counsel"
    CITE_SIGHT_SITE = "cite_vs_sight_vs_site"
    THROUGH_THREW_THRU = "through_vs_threw_vs_thru"
    APART_A_PART = "apart_vs_a_part"

    AN_AND = 'an_instead_of_and'
    I_IT = 'i_instead_of_it'
    HE_THE = 'he_instead_of_the'
    THEY_THE = 'they_instead_of_the'

    GASSES = "gases"
    PEOPLES = "peoples"
    PEOPLES_APOSTROPHE = "peoples'"
    PERSONS = "persons"
    IN_REGARDS_TO = "in_regards_to"
    MONIES = "monies"
    DECADES_WITH_APOSTROPHE = "decades_with_apostrophe"
    RESPONSE_STARTS_WITH_VERB = "response_starts_with_verb"
    PLURAL_VERSUS_POSSESSIVE_NOUNS_POSSESSIVE_OPTIMAL = "plural_versus_possessive_nouns_possessive_noun_optimal"
    PLURAL_VERSUS_POSSESSIVE_NOUNS_PLURAL_OPTIMAL = "plural_versus_possessive_nouns_plural_noun_optimal"
    QUESTION_MARK = "question_marks"
    ARTICLE = "articles"
    THIS_THAT = "this_versus_that"
    THESE_THOSE = "these_versus_those"
    SPACING = "spacing"
    WOMAN_WOMEN = "woman_versus_women"
    MAN_MEN = "man_versus_men"
    CHILD_CHILDREN = "childs_versus_children"
    THAN_THEN = "than_versus_then"
    REPEATED_WORD = "repeated_word"
    REPEATED_CONJUNCTION = "repeated_conjunction"
    SUBJECT_PRONOUN = "subject_pronouns"
    OBJECT_PRONOUN = "object_pronouns"
    POSSESSIVE_NOUN = "possessive_nouns"
    COMMAS_IN_NUMBERS = "commas_in_numbers"
    YES_NO_COMMA = "commas_after_yes_&_no"
    SINGULAR_PLURAL = "singular_and_plural_nouns"
    SINGULAR_PLURAL_NO_DETERMINER = 'singular_and_plural_nouns_no_determiner'
    SINGULAR_PLURAL_THESE_THOSE = 'singular_and_plural_nouns_these_those'
    SINGULAR_PLURAL_POSSESSIVE = "singular_and_plural_possessive"
    CAPITALIZATION = "capitalization"
    ALLCAPS = "allcaps"
    CONTRACTION = "contractions"
    ITS_IT_S = "its_versus_it_s"
    PUNCTUATION = "punctuation"
    ADVERB = "adverbs_versus_adjectives"
    SUBJECT_VERB_AGREEMENT = "subject_verb_agreement"
    IRREGULAR_PLURAL_NOUN = "irregular_plural_nouns"
    FRAGMENT = "fragment"
    FRAGMENT_NO_SUBJ = "fragment_no_subj"
    FRAGMENT_NO_VERB = "fragment_no_verb"
    POSSESSIVE_PRONOUN = "possessive_pronouns"
    VERB_SHIFT = "verb_shift"
    PASSIVE_WITHOUT_BE = "passive_without_be"
    PASSIVE_WITH_INCORRECT_PARTICIPLE = "passive_with_incorrect_participle"
    PASSIVE_WITH_INCORRECT_BE = "passive_with_incorrect_be"
    PASSIVE_WITH_SIMPLE_PAST_INSTEAD_OF_PARTICIPLE = "passive_with_simple_past_instead_of_participle"
    INCORRECT_PAST_TENSE_AS_PARTICIPLE_IN_PASSIVE = "incorrect_past_tense_as_participle_in_passive"
    PERFECT_WITHOUT_HAVE = "perfect_without_have"
    PERFECT_PROGRESSIVE_WITHOUT_HAVE = "perfect_progressive_without_have"
    PASSIVE_PERFECT_WITHOUT_HAVE = "passive_perfect_without_have"
    PASSIVE_PERFECT_WITH_INCORRECT_PARTICIPLE = "passive_perfect_with_incorrect_participle"
    PAST_TENSE_INSTEAD_OF_PARTICIPLE = "past_instead_of_participle"
    PERFECT_TENSE_WITH_INCORRECT_PARTICIPLE = "perfect_with_incorrect_participle"
    PERFECT_WITH_INCORRECT_PARTICIPLE = "perfect_with_incorrect_participle"
    PERFECT_PROGRESSIVE_WITH_INCORRECT_BE_AND_WITHOUT_HAVE = "perfect_progressive_with_incorrect_be_and_without_have"
    SIMPLE_PAST_INSTEAD_OF_PAST_PERFECT = "simple_past_instead_of_past_perfect"
    SIMPLE_PAST_INSTEAD_OF_PRESENT_PERFECT = "simple_past_instead_of_present_perfect"
    FUTURE_IN_SUBCLAUSE = "future_in_subclause"
    INCORRECT_IRREGULAR_PAST_TENSE = "incorrect_irregular_past_tense"
    INCORRECT_PARTICIPLE = "incorrect_participle"
    SVA_SIMPLE_NOUN = "subject_verb_agreement_with_simple_noun"
    SVA_PRONOUN = "subject_verb_agreement_with_personal_pronoun"
    SVA_INVERSION = "subject_verb_agreement_with_inversion"
    SVA_NEITHER_NOR = "subject_verb_agreement_with_neither_nor"
    SVA_EITHER_OR = "subject_verb_agreement_with_either_or"
    SVA_COLLECTIVE_NOUN = "subject_verb_agreement_with_collective_noun"
    SVA_INDEFINITE = "subject_verb_agreement_with_indefinite_pronoun"
    SVA_SEPARATE = "subject_verb_agreement_with_separate_subject_and_verb"
    SVA_RELATIVE_PRONOUN = "subject_verb_agreement_with_relative_pronoun"
    INCORRECT_INFINITIVE = "incorrect_infinitive"
    INCORRECT_INFINITIVE_ING = "incorrect_infinitive_ing"
    INCORRECT_INFINITIVE_PAST = "incorrect_infinitive_past"
    MISSING_PREPOSITION_AFTER_STAT = "missing_preposition_after_stat"

AGREEMENT_ERRORS = set([
    GrammarError.SVA_SIMPLE_NOUN.value,
    GrammarError.SVA_PRONOUN.value,
    GrammarError.SVA_INVERSION.value,
    GrammarError.SVA_NEITHER_NOR.value,
    GrammarError.SVA_EITHER_OR.value,
    GrammarError.SVA_COLLECTIVE_NOUN.value,
    GrammarError.SVA_INDEFINITE.value,
    GrammarError.SVA_SEPARATE.value
])
