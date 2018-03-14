# Constants
PRESENT_TENSE_VERBS_FILE = 'sentence_parts/presentTenseVerbs.txt'
OUTPUT_FILE = 'sentence_parts/presentParticipleVerbs.txt'


with open(PRESENT_TENSE_VERBS_FILE, 'r') as f:
    _of = open(OUTPUT_FILE, 'w')
    for line in f:
        line = line.strip()
        if line[-1] == 'e':
            line = line[:-1]
        line += 'ing\n'
        _of.write(line)
    _of.close()
