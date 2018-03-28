"""Check if subject and verb agree in a simple sentence"""

import spacy
nlp = spacy.load('en')

ACCEPTABLE_STRUCTURES = [
        'I/YOU/WE/THEY--VBP',
        'HE/SHE/IT--VBZ',
        'NNP--VBZ',
        'NN--VBZ',
        'NNS--VBP',
        'COMPOUND_SUBJ--VBP'
        'I/YOU/WE/THEY-VBP-VB',
        'HE/SHE/IT-VBZ-VB',
        'NNP-VBZ-VB',
        'NN-VBZ-VB',
        'NNS-VBP-VB',
        'COMPOUND_SUBJ-VBP-VB'

]

def check_agreement(sentence):
    """Singular subject takes a singular verb, plural subject takes a plural
    verb"""
    doc = nlp(sentence)
    subject, verb, auxilary = '', '', ''
    prev_dep = ''
    for w in doc:
        if prev_dep.startswith('nsubj') and w.text.upper() == 'AND':
            subject = 'COMPOUND_SUBJ'
        elif w.dep_ == 'nsubj' and w.tag_ != 'PRP':
            subject = w.tag_ 
        elif w.dep_.startswith('nsubj') and w.tag_ == 'PRP':
            subject = 'I/YOU/WE/THEY'
            if w.text.upper() in ['HE', 'SHE', 'IT']:
                subject = 'HE/SHE/IT'
        elif w.dep_ == 'ROOT':
            verb = w.tag_
        elif w.dep_ == 'aux':
            auxilary = w.tag_
        prev_dep = w.dep_
    
    structure = '{}-{}-{}'.format(subject,auxilary, verb)
    if structure not in ACCEPTABLE_STRUCTURES:
        return False
    return True


# Present tense
# I take  
#   - PRP(I/You/We/They) VBP
# You take
#   - PRP(I/You/We/We) VBP
# He/She takes
#   - PRP(not I/You/We) VBZ
# John takes
#   - NNP VBZ
# Man takes
#   - NN VBZ

# I/You/We/They/He/She took
#   - PRP VBD
# John took
#   - NNP VBD
# Men took
#   - NNS VBD
