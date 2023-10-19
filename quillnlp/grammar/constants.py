from enum import Enum

# Tag, part-of-speech and dependency constants


class Tag(Enum):
    POSSESSIVE = "POS"
    PLURAL_NOUN = "NNS"
    PLURAL_PROPER_NOUN = "NNS"
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
    ADJECTIVE = "JJ"
    COMPARATIVE_ADJECTIVE = "JJR"
    COMPARATIVE_ADVERB = "JJR"
    PREPOSITION = "IN"

PRESENT_VERB_TAGS = set([Tag.PRESENT_SING3_VERB.value,
                         Tag.PRESENT_OTHER_VERB.value,
                         Tag.INFINITIVE.value])
PAST_VERB_TAGS = set([Tag.PAST_PARTICIPLE_VERB.value,
                      Tag.PAST_PARTICIPLE_VERB.value])
FINITE_VERB_TAGS = set([Tag.PRESENT_OTHER_VERB.value, Tag.PRESENT_SING3_VERB.value,
                        Tag.SIMPLE_PAST_VERB.value, Tag.MODAL_VERB.value])

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
    SUBORD_CONJ = "SCONJ"
    PUNCTUATION = "PUNCT"

POSSIBLE_POS_IN_NOUN_PHRASE = set([POS.NOUN.value, POS.ADJECTIVE.value,
                                   POS.NUMBER.value, POS.ADPOSITION.value,
                                   POS.ADVERB.value, POS.PRONOUN.value,
                                   POS.PROPER_NOUN.value])


class Dependency(Enum):
    SUBJECT = "nsubj"
    PASS_SUBJECT = "nsubjpass"
    DIRECT_OBJECT = "dobj"
    PREPOSITIONAL_OBJECT = 'pobj'
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
    MARKER = "mark"
    RELATIVE_CLAUSE = "relcl"
    NEGATION = "neg"


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
    PUNCTUATION = set("]!()*+,./:;=#?[\\^_{|}~-")
    END_OF_SENTENCE_PUNCTUATION = set([".", "!", "?", '"', '”', "'"])
    CLOSING_QUOTATION_MARKS = set(['"', '”', "'"])
    SINGULAR_DETERMINERS = set(["none", "nothing", "each", "one", "little","much"])  # deleted 'every' and 'another' because they gave bad results
    INDEF_PRONOUNS = set(["every", "none", "all", "nothing", "some", "each", "any", "another",
                          "anybody", "anyone", "anything", "somebody", "other", "enough", "everyone",
                          "everybody", "everything", "something", "one", "less", "little", "much",
                          "nobody", "both", "few", "someone", "neither", "either",
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
                                  "dont", "didnt", "wont", "youd", "hed",
                                  "theyd", "youll", "theyll", "shell", "havent",
                                  "couldve", "thered", "thatd"])
    CONTRACTIONS_SECOND_PART = set(["s", "m", "ll", "d", "ve", "re", "nt"])
    INCORRECT_CONTRACTIONS_WITH_CAPITAL = set(["Shed", "Ill", "Id"])

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
                            "audience", "parliament", "congregation", "chamber", "range",
                            "flight", "gaggle", "colony", "horde", "panel", "guild",
                            "government"])
    MUTUALLY_EXCLUSIVE_BE_FORMS = set(["be", "am", "are", "is", "been"])
    BE_FORMS = set(["be", "am", "are", "is", "been", "was", "were"])
    SINGULAR_COUNT_WORDS = set(["few", "couple"])
    SINGULAR_NOUNS_THAT_LOOK_LIKE_PLURALS = set(["means", "species", "kumquat", "oriele", "series", "selfie",
                                                 "miniseries", "specimen", "BSc", "MSc", "crossroads", "sheep", "people"])
    IRREGULAR_PLURALS = set(["geese", "dice", "stairs", "mice"])


# Error type constants


class GrammarError(Enum):
    AN_AND = 'an_instead_of_and'
    ALOT = 'alot_instead_of_a_lot'
    CAN_NOT = 'can_not_instead_of_cannot'
    I_IT = 'i_instead_of_it'
    HE_THE = 'he_instead_of_the'
    THEY_THE = 'they_instead_of_the'
    INCORRECT_INFINITIVE = 'incorrect_infinitive'
    INCORRECT_INFINITIVE_ING = 'incorrect_infinitive_ing'
    INCORRECT_INFINITIVE_PAST = 'incorrect_infinitive_past'
    RUNON = "runon"
    RUNON_WITH_CONJUNCTIVE_ADVERB = "runon_with_conjunctive_adverb"
    EXTRA_SPACE = "extra_space"
    THERE_NO = "there_no"
    STARTS_WITH_PUNCTUATION = "starts_with_punctuation"
    MISSING_HYPHEN = "missing_hyphen"
    WHOSE_WHOS = "who_s_vs_whose"
    GASSES = "gases"
    PEOPLES = "peoples"
    PEOPLES_APOSTROPHE = "peoples'"
    PERSONS = "persons"
    IN_REGARDS_TO = "in_regards_to"
    MONIES = "monies"
    AFFECT_EFFECT = "affect_vs_effect"
    ACCEPT_EXCEPT = "accept_vs_except"
    ADVISE_ADVICE = "advise_vs_advice"
    APART_A_PART = "apart_vs_a_part"
    CITE_SIGHT_SITE = "cite_vs_sight_vs_site"
    COUNCIL_COUNSEL = "council_vs_counsel"
    FURTHER_FARTHER = "further_vs_farther"
    TO_TOO_TWO = "to_vs_too_vs_two"
    TO_TOO_TWO_TOO_OPTIMAL = "to_vs_too_vs_two_too_optimal"
    TO_TOO_TWO_TO_OPTIMAL = "to_vs_too_vs_two_to_optimal"
    TO_TOO_TWO_TWO_OPTIMAL = "to_vs_too_vs_two_two_optimal"
    LEAD_LED = "lead_vs_led"
    LOOSE_LOSE = "loose_vs_lose"
    THROUGH_THREW_THRU = "through_vs_threw_vs_thru"
    PASSED_PAST = "passed_vs_past"
    THEIR = "their_vs_there_vs_they_re"
    THEIR_THEIR_OPTIMAL = "their_vs_there_vs_they_re_their_optimal"
    THEIR_THERE_OPTIMAL = "their_vs_there_vs_they_re_there_optimal"
    THEIR_THEYRE_OPTIMAL = "their_vs_there_vs_they_re_they_re_optimal"
    DECADES_WITH_APOSTROPHE = "decades_with_apostrophe"
    RESPONSE_STARTS_WITH_VERB = "response_starts_with_verb"
    PLURAL_VERSUS_POSSESSIVE_NOUNS = "plural_versus_possessive_nouns"
    PLURAL_VERSUS_POSSESSIVE_NOUNS_PLURAL_OPTIMAL = "plural_versus_possessive_nouns_plural_noun_optimal"
    PLURAL_VERSUS_POSSESSIVE_NOUNS_POSSESSIVE_OPTIMAL = "plural_versus_possessive_nouns_possessive_noun_optimal"
    SINGULAR_VERSUS_PLURAL_POSSESSIVE = "singular_and_plural_possessive"
    SINGULAR_VERSUS_PLURAL_POSSESSIVE_REGULAR = "singular_and_plural_possessive_regular"
    SINGULAR_VERSUS_PLURAL_POSSESSIVE_IRREGULAR = "singular_and_plural_possessive_irregular"
    QUESTION_MARK = "question_marks"
    ARTICLE = "articles"
    ARTICLE_A_OPTIMAL = "articles_a_optimal"
    ARTICLE_AN_OPTIMAL = "articles_an_optimal"
    THIS_THAT = "this_versus_that"
    THESE_THOSE = "these_versus_those"
    SPACING = "spacing"
    WOMAN_WOMEN = "woman_versus_women"
    MAN_MEN = "man_versus_men"
    CHILD_CHILDREN = "childs_versus_children"
    THAN_THEN = "than_versus_then"
    THAN_THEN_THAN_OPTIMAL = "than_versus_then_than_optimal"
    THAN_THEN_THEN_OPTIMAL = "than_versus_then_then_optimal"
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
    CAPITALIZATION = "capitalization"
    ALLCAPS = "allcaps"
    CONTRACTION = "contractions"
    ITS_IT_S = "its_versus_it_s"
    ITS_IT_S_ITS_OPTIMAL = "its_versus_it_s_its_optimal"
    ITS_IT_S_IT_S_OPTIMAL = "its_versus_it_s_it_s_optimal"
    YOUR_YOU_RE = "you_re_vs_your"
    PUNCTUATION = "punctuation"
    ADVERB = "adverbs_versus_adjectives"
    SUBJECT_VERB_AGREEMENT = "subject_verb_agreement"
    IRREGULAR_PLURAL_NOUN = "irregular_plural_nouns"
    FRAGMENT = "fragment"
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
    PERFECT_WITH_INCORRECT_PARTICIPLE = "perfect_with_incorrect_participle"
    PERFECT_PROGRESSIVE_WITH_INCORRECT_BE_AND_WITHOUT_HAVE = "perfect_progressive_with_incorrect_be_and_without_have"
    SIMPLE_PAST_INSTEAD_OF_PAST_PERFECT = "simple_past_instead_of_past_perfect"
    SIMPLE_PAST_INSTEAD_OF_PRESENT_PERFECT = "simple_past_instead_of_present_perfect"
    FUTURE_IN_SUBCLAUSE = "future_in_subclause"
    INCORRECT_IRREGULAR_PAST_TENSE = "incorrect_irregular_past_tense"
    INCORRECT_PARTICIPLE = "incorrect_participle"
    INCORRECT_NEGATIVE_VERB_WITH_A_SIMPLE_NOUN_SUBJECT = "incorrect_negative_verb_with_a_simple_noun_subject"
    FRAGMENT_NO_SUBJ = "fragment_no_subj"
    FRAGMENT_NO_VERB = "fragment_no_verb"

    # Verb agreement errors

    SVA_SIMPLE_NOUN = "subject_verb_agreement_with_simple_noun"
    SVA_SIMPLE_NOUN_PLURAL_REGULAR = "subject_verb_agreement_with_simple_noun_" \
                                     "plural_noun_with_regular_present_tense_plural_verb_optimal_" \
                                     "and_error_is_regular_present_tense_singular_verb"
    SVA_SIMPLE_NOUN_SINGULAR_REGULAR = "subject_verb_agreement_with_simple_noun_" \
                                       "singular_noun_with_regular_singular_verb_optimal_" \
                                       "and_error_is_regular_plural_verb"
    SVA_SIMPLE_NOUN_PLURAL_BE = "subject_verb_agreement_with_simple_noun_" \
                                "plural_noun_with_plural_to_be_verb_optimal_" \
                                "and_error_is_singular_to_be_verb"
    SVA_SIMPLE_NOUN_SINGULAR_BE = "subject_verb_agreement_with_simple_noun_" \
                                  "singular_noun_with_singular_to_be_verb_optimal_" \
                                  "and_error_is_plural_to_be_verb"
    SVA_SIMPLE_NOUN_PLURAL_HAVE = "subject_verb_agreement_with_simple_noun_" \
                                  "plural_noun_with_plural_to_have_verb_optimal_" \
                                  "and_error_is_singular_to_have_verb"
    SVA_SIMPLE_NOUN_SINGULAR_HAVE = "subject_verb_agreement_with_simple_noun_" \
                                    "singular_noun_with_singular_to_have_verb_optimal_" \
                                    "and_error_is_plural_to_have_verb"

    SVA_PRONOUN = "subject_verb_agreement_with_personal_pronoun"
    SVA_PRONOUN_PLURAL_REGULAR= "subject_verb_agreement_with_personal_pronoun_" \
                                "plural_pronoun_with_regular_present_tense_plural_verb_optimal_" \
                                "and_error_is_regular_present_tense_singular_verb"
    SVA_PRONOUN_SINGULAR_REGULAR = "subject_verb_agreement_with_personal_pronoun_" \
                                   "singular_pronoun_with_regular_singular_verb_optimal_" \
                                   "and_error_is_regular_plural_verb"
    SVA_PRONOUN_PLURAL_BE = "subject_verb_agreement_with_personal_pronoun_" \
                            "plural_pronoun_with_plural_to_be_verb_optimal_" \
                            "and_error_is_singular_to_be_verb"
    SVA_PRONOUN_SINGULAR_BE = "subject_verb_agreement_with_personal_pronoun_" \
                              "singular_pronoun_with_singular_to_be_verb_optimal_" \
                              "and_error_is_plural_to_be_verb"
    SVA_PRONOUN_PLURAL_HAVE = "subject_verb_agreement_with_personal_pronoun_" \
                              "plural_pronoun_with_plural_to_have_verb_optimal_" \
                              "and_error_is_singular_to_have_verb"
    SVA_PRONOUN_SINGULAR_HAVE = "subject_verb_agreement_with_personal_pronoun_" \
                                "singular_pronoun_with_singular_to_have_verb_optimal_" \
                                "and_error_is_plural_to_have_verb"

    SVA_COLLECTIVE_NOUN = "subject_verb_agreement_with_collective_noun"
    SVA_COLLECTIVE_NOUN_SINGULAR_REGULAR = "subject_verb_agreement_with_collective_noun_" \
                                           "singular_regular_present_tense_verb_optimal"
    SVA_COLLECTIVE_NOUN_PLURAL_REGULAR = "subject_verb_agreement_with_collective_noun_" \
                                         "plural_regular_present_tense_verb_optimal"
    SVA_COLLECTIVE_NOUN_SINGULAR_BE = "subject_verb_agreement_with_collective_noun_singular_to_be_verb_optimal"
    SVA_COLLECTIVE_NOUN_PLURAL_BE = "subject_verb_agreement_with_collective_noun_plural_to_be_verb_optimal"
    SVA_COLLECTIVE_NOUN_SINGULAR_HAVE = "subject_verb_agreement_with_collective_noun_" \
                                        "singular_present_tense_to_have_verb_optimal"
    SVA_COLLECTIVE_NOUN_PLURAL_HAVE = "subject_verb_agreement_with_collective_noun_" \
                                      "plural_present_tense_to_have_verb_optimal"

    SVA_INDEFINITE = "subject_verb_agreement_with_indefinite_pronoun"
    SVA_INDEFINITE_PLURAL_REGULAR = "subject_verb_agreement_with_indefinite_pronoun_" \
                                    "plural_indefinite_pronoun_with_regular_present_tense_plural_verb_optimal_" \
                                    "and_error_is_regular_present_tense_singular_verb"
    SVA_INDEFINITE_SINGULAR_REGULAR = "subject_verb_agreement_with_indefinite_pronoun_" \
                                      "singular_indefinite_pronoun_with_regular_singular_verb_optimal_" \
                                      "and_error_is_regular_plural_verb"
    SVA_INDEFINITE_PLURAL_BE = "subject_verb_agreement_with_indefinite_pronoun_" \
                               "plural_indefinite_pronoun_with_plural_to_be_verb_optimal_" \
                               "and_error_is_singular_to_be_verb"
    SVA_INDEFINITE_SINGULAR_BE = "subject_verb_agreement_with_indefinite_pronoun_" \
                                 "singular_indefinite_pronoun_with_singular_to_be_verb_optimal_" \
                                 "and_error_is_plural_to_be_verb"
    SVA_INDEFINITE_PLURAL_HAVE = "subject_verb_agreement_with_indefinite_pronoun_" \
                                 "plural_indefinite_pronoun_with_plural_to_have_verb_" \
                                 "optimal_and_error_is_singular_to_have_verb"
    SVA_INDEFINITE_SINGULAR_HAVE = "subject_verb_agreement_with_indefinite_pronoun_" \
                                   "singular_indefinite_pronoun_with_singular_to_have_verb_optimal_" \
                                   "and_error_is_plural_to_have_verb"

    SVA_SEPARATE = "subject_verb_agreement_with_separate_subject_and_verb"
    SVA_INVERSION = "subject_verb_agreement_with_inversion"
    SVA_NEITHER_NOR = "subject_verb_agreement_with_neither_nor"
    SVA_EITHER_OR = "subject_verb_agreement_with_either_or"
    MISSING_PREPOSITION_AFTER_STAT = "missing_preposition_after_stat"
    INCORRECT_PREPOSITION = "incorrect_preposition"


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

CLAUSE_MARKERS = set(['conj', 'advcl', 'ccomp', 'parataxis'])
COORDINATING_CONJUNCTIONS = set(['for', 'and', 'nor', 'but', 'or', 'yet', 'so'])
QUESTION_WORDS = set(['what', 'which', 'who', 'where', 'why', 'when', 'how', 'whose'])