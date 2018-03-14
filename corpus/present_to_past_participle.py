"""Generate list of past participle verbs, mixing in the irregular past
participle verbs"""

import re

# Constants
REGULAR_FORMS_IRREGULAR_PAST_PARTICIPLES_FILE = \
'sentence_parts/presentTenseFormsOfIrregularPastParticipleVerbs.txt'
IRREGULAR_PAST_PARTICIPLES_FILE = \
'sentence_parts/irregularPastParticipleVerbs.txt'
PRESENT_TENSE_VERBS_FILE = 'sentence_parts/presentTenseVerbs.txt'
OUTPUT_FILE = 'sentence_parts/pastParticipleVerbs.txt'
VOWELS = 'aeiou'
CONSONANTS = 'bcdfghjklmnpqrstvwxz'
CONSONANTS_NO_XW = 'bcdfghjklmnpqrstvz'

consonant_then_y = re.compile('^[{}]y$'.format(CONSONANTS))
double_letter = re.compile('^[{}][{}][{}]$'.format(CONSONANTS, VOWELS,
                                                   CONSONANTS_NO_XW))

with open(REGULAR_FORMS_IRREGULAR_PAST_PARTICIPLES_FILE, 'r') as ipp:
    list_of_irregular_verbs = [word for word in ipp]

with open(IRREGULAR_PAST_PARTICIPLES_FILE, 'r') as ipp2:
    past_participle_irregular_verbs = [word2 for word2 in ipp2]

with open(PRESENT_TENSE_VERBS_FILE, 'r') as f:
    _of = open(OUTPUT_FILE, 'w')
    for line in f:
        line = line.strip()
        # irregular: replace
        if line in list_of_irregular_verbs:
            pos = list_of_irregular_verbs.index(line)
            line = past_participle_irregular_verbs[pos]
        # ending in e: add d
        elif line[-1] == 'e':
            line += 'd'
        # consonant followed by y
        elif consonant_then_y.match(line[-2:]):
            line += line[:-1] + 'ied'
        # one syl words ending in c-v-c: double last letter add ed
        elif len(line) < 5 and double_letter.match(line[-3:]):
            line += line[-1]
            line += 'ed'
        else:
            line += 'ed'

        _of.write(line)
    _of.close()
