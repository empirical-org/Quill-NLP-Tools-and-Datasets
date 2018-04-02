"""Check if subject and verb agree in a simple sentence"""

import spacy
import os
nlp =  spacy.load(os.environ.get('QUILL_SPACY_MODEL', 'en_core_web_lg'))

ACCEPTABLE_STRUCTURES = [
    'I/YOU/WE/THEY--VBP',
    'HE/SHE/IT--VBZ',
    'NNP--VBZ',
    'NN--VBZ',
    'NNS--VBP',
    'COMPOUND_SUBJ--VBP',
    'COMPOUND_SUBJ--VB',
    'I/YOU/WE/THEY--VBD',
    'HE/SHE/IT--VBD',
    'NNP--VBD',
    'NN--VBD',
    'NNS--VBD',
    'COMPOUND_SUBJ--VBD'
]

# Grammatical, but not complete sentences
NON_SENTENCE_STRUCTURE = [
    'I/YOU/WE/THEY--MD',
    'HE/SHE/IT--MD',
    'NNP--MD',
    'NN--MD',
    'NNS--MD',
    'COMPOUND_SUBJ--MD',
    'I/YOU/WE/THEY--VBG',
    'HE/SHE/IT--VBG',
    'NNP--VBG',
    'NN--VBG',
    'NNS--VBG',
    'COMPOUND_SUBJ--VBG'
]


def _to_be_agreement(subject_text, subject_structure, verb_text,
        have_precedes=False):
    if subject_text.upper() == 'I':
        return verb_text in ['AM', 'WAS'] or (have_precedes and verb_text ==
                'BEEN')
    elif (subject_text.upper() in ['WE', 'YOU', 'THEY'] or subject_structure in
            ['NNS', 'NNPS', 'COMPOUND_SUBJ']):
        return verb_text in ['ARE', 'WERE'] or (have_precedes and verb_text ==
                'BEEN')
    return verb_text in ['IS', 'WAS'] or (have_precedes and verb_text ==
            'BEEN')


def _to_do_agreement(subject_text,subject_structure, verb_text):
    if (subject_text.upper() in ['I', 'YOU', 'WE', 'THEY'] or subject_structure
            in ['NNS', 'NNPS', 'COMPOUND_SUBJ']):
        return verb_text in ['DO', 'DID'] 
    return verb_text in ['DOES', 'DID']


def _to_have_agreement(subject_text, subject_structure, verb_text):
    if (subject_text.upper() in ['I', 'YOU', 'THEY', 'WE'] or subject_structure
            in ['NNS', 'NNPS', 'COMPOUND_SUBJ']):
        return verb_text in ['HAVE', 'HAD']
    return verb_text in ['HAS', 'HAD']


def check_agreement(sentence):
    """Singular subject takes a singular verb, plural subject takes a plural
    verb"""
    feedback = ''
    feedback += sentence + '\n'
    doc = nlp(sentence)
    feedback += "{}\n".format( [(d.text, d.dep_, d.tag_) for d in doc] )
    subject_structure, verb_structure, auxilary_structure = '', '', ''
    auxilary_text, subject_text, verb_text = '', '', ''
    verb_base, auxilary_base = '', ''
    auxilaries = []
    prev_dep = ''
    has_direct_object = False
    acomp_following_root = False
    for w in doc:
        if prev_dep.startswith('nsubj') and w.text.upper() == 'AND':
            subject_structure = 'COMPOUND_SUBJ'
        elif w.dep_.startswith('nsubj') and w.tag_ != 'PRP':
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
        elif w.dep_.startswith('aux') and not verb_text:
            # auxilaries before main verb
            auxilary_structure = w.tag_
            auxilary_base = w.lemma_
            auxilary_text = w.text.upper()
            auxilaries.append([auxilary_text, auxilary_structure,
                auxilary_base])
        elif w.dep_ == 'dobj':
            has_direct_object = True
        elif prev_dep == 'ROOT' and w.dep_ == 'acomp':
            acomp_following_root = True
            acomp_structure = w.tag_
            # The scientists will be stir
            # The scientists have been stir
            if acomp_structure == 'VB':
                return False

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

        elif (aux[2] == 'do' and not
                _to_do_agreement(subject_text,subject_structure, aux[0])):
            return False
        elif (aux[2] == 'have' and not _to_have_agreement(subject_text,
            subject_structure, aux[0])):
            return False
        elif aux[2] == 'have':
            have_precedes = True

        if aux[2] != 'have':
            have_precedes = False

        previous_aux = aux

    # Deal with main verb edge cases
    if verb_base == 'have':
        if not _to_have_agreement(subject_text,subject_structure, verb_text):
            return False
    elif verb_base == 'be':
        # be following modal auxilary does not change form
        if auxilaries and auxilaries[-1][2] not in ['be', 'do', 'have']:
            if verb_text != 'BE':
                return False
        # if be doesn't follow a modal auxilary,
        elif not _to_be_agreement(subject_text, subject_structure, verb_text,
                have_precedes):
            return False
    elif verb_base == 'do':
        if not _to_do_agreement(subject_text, subject_structure, verb_text):
            return False

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
                # the scientist and the boy stir the potion
                # we have been stirring [the potion](D.O.)
                # she has been cooking dinner
                # we should be cooking dinner
                # we should be worried
                return verb_structure == 'VBG'
            
            # we should have been worried [about you](object of the prep.)
            # we should have been worrying about you 
            # The races have been run
            return verb_structure in ['VBG', 'VBN']
        else: # did or modal auxilary
            return verb_structure == 'VB'
            
    if verb_base in ['have', 'be', 'do']:
        return True
    
    structure = '{}--{}'.format(subject_structure, verb_structure)
    return (structure in ACCEPTABLE_STRUCTURES or structure in
            NON_SENTENCE_STRUCTURE)
