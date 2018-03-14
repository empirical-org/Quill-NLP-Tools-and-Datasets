import re

# Constants
PRESENT_TENSE_VERBS_FILE = 'sentence_parts/presentTenseVerbs.txt'
OUTPUT_FILE = 'sentence_parts/presentParticipleVerbs.txt'
VOWELS = 'aeiou'
CONSONANTS = 'bcdfghjklmnpqrstvwxz'
CONSONANTS_NO_XW = 'bcdfghjklmnpqrstvz'

double_letter = re.compile('^[{}][{}][{}]$'.format(CONSONANTS, VOWELS,
                                                   CONSONANTS_NO_XW))


with open(PRESENT_TENSE_VERBS_FILE, 'r') as f:
    _of = open(OUTPUT_FILE, 'w')
    for line in f:
        line = line.strip()
        # ending in e: drop e add ing
        if line[-1] == 'e':
            line = line[:-1]
        # one syl words ending in c-v-c: double last letter
        elif len(line) < 5 and double_letter.match(line[-3:]):
            line += line[-1]

        line += 'ing\n'
        _of.write(line)
    _of.close()
