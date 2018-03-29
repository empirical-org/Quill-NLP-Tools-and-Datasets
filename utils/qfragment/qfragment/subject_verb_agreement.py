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
]


def _to_be_agreement(subject_text, subject_structure, verb_text,
        have_precedes=False):
    if subject_text.upper() == 'I':
        return verb_text in ['AM', 'WAS'] or (have_precedes and verb_text ==
                'BEEN')
    elif (subject_text.upper() in ['WE', 'YOU', 'THEY'] or subject_structure in
            ['NNS', 'NNPS']):
        return verb_text in ['ARE', 'WERE'] or (have_precedes and verb_text ==
                'BEEN')
    return verb_text in ['IS', 'WAS'] or (have_precedes and verb_text ==
            'BEEN')


def _to_do_agreement(subject_text, verb_text):
    if subject_text.upper() in ['I', 'YOU', 'WE', 'THEY']:
        return verb_text in ['DO', 'DID'] 
    return verb_text in ['DOES', 'DID']


def _to_have_agreement(subject_text, verb_text):
    if subject_text.upper() in ['I', 'YOU', 'THEY', 'WE']:
        return verb_text in ['HAVE', 'HAD']
    return verb_text in ['HAS', 'HAD']


def check_agreement(sentence):
    """Singular subject takes a singular verb, plural subject takes a plural
    verb"""
    doc = nlp(sentence)
    subject_structure, verb_structure, auxilary_structure = '', '', ''
    auxilary_text, subject_text, verb_text = '', '', ''
    verb_base, auxilary_base = '', ''
    auxilaries = []
    prev_dep = ''
    has_direct_object = True
    for w in doc:
        if prev_dep.startswith('nsubj') and w.text.upper() == 'AND':
            subject_structure = 'COMPOUND_SUBJ'
        elif w.dep_ == 'nsubj' and w.tag_ != 'PRP':
            subject_structure = w.tag_ 
            subject_text = w.text.upper()
        elif w.dep_.startswith('nsubj') and w.tag_ == 'PRP':
            subject_structure = 'I/YOU/WE/THEY'
            subject_text = w.text.upper()
            if subject_text in ['HE', 'SHE', 'IT']:
                subject_structure = 'HE/SHE/IT'
        elif w.dep_ == 'ROOT':
            verb_structure = w.tag_
            verb_base = w.lemma_
            verb_text = w.text.upper()
        elif w.dep_ == 'aux':
            auxilary_structure = w.tag_ # VBPVBN
            auxilary_base = w.lemma_ # havebe
            auxilary_text = w.text.upper() # HAVEBEEN
            auxilaries.append([auxilary_text, auxilary_structure,
                auxilary_base])
        elif w.dep_ == 'dobj':
            has_direct_object = True
        prev_dep = w.dep_
    
    # Ensure auxilaries have correct number (modal auxilaries never change form)
    have_precedes = False
    previous_aux = (None, None, None)
    for aux in auxilaries:
        if aux[2] == 'be':
            # if be form is preceded by modal auxilary it should be base form
            if previous_aux[2] not in ['be', 'do', 'have']:
                if aux[0] != 'BE':
                    return False 

            # be form is not preceded by modal auxilary
            elif not _to_be_agreement(subject_text, subject_structure, aux[0],
                        have_precedes):
                return False

        elif aux[2] == 'do' and not _to_do_agreement(subject_text, aux[0]):
            return False
        elif aux[2] == 'have' and not _to_have_agreement(subject_text, aux[0]):
            return False
        elif aux[2] == 'have':
            have_precedes = True

        if aux[2] != 'have':
            have_precedes = False

        previous_aux = aux

    # Deal with main verb edge cases
    if verb_base == 'have':
        return _to_have_agreement(subject_text, verb_text)
    elif verb_base == 'be':
        # be following modal auxilary does not change form
        if auxilaries and auxilaries[-1][2] not in ['be', 'do', 'have']:
            # we should be
            return verb_text == 'be'
        # if be doesn't follow a modal auxilary,
        return _to_be_agreement(subject_text, subject_structure, verb_text,
                have_precedes)
    elif verb_base == 'do':
        return _to_do_agreement(subject_text, verb_text)

    # If auxilaries are used, main verb should be participle, else, check
    # structure
    if auxilaries:
        if auxilaries[-1][2] in ['have', 'be']: 

            # Gerund never follows a form of have
            if have_precedes:
                # we have stirred the potion
                # she has cooked dinner
                return verb_structure in ['VBN']
            elif has_direct_object: 
                # we have been stirring [the potion](D.O.)
                # she has been cooking dinner
                return verb_structure == 'VBG'
            
            # we should have been worried [about you](object of the prep.)
            # we should have been worrying about you 
            return verb_structure in ['VBG', 'VBN']
        else: # did or modal auxilary
            return verb_structure == 'VB'
           
    structure = '{}--{}'.format(subject_structure, verb_structure)
    return structure in ACCEPTABLE_STRUCTURES

