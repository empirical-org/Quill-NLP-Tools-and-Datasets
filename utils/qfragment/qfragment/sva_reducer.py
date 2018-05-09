#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Preprocess sentences and reduce them."""
from sva_utils import drop_modifiers, remove_prepositional_phrases
from sva_utils import substitute_infinitives_as_subjects
from sva_utils import simplify_compound_subjects, remove_adverbial_clauses 
from preprocess_utils import remove_double_commas, remove_leading_noise
from pattern.en import mood
import textacy


def print_verb_phrases_with_subject(doc, verb_phrases_with_subjects):
    print(doc.text)
    for vps,sps in verb_phrases_with_subjects:
        result = ''
        for vp in vps:
            result += doc[vp].text + ' '
        result = result.strip()
        result += ':'
        for sp in sps:
            result += doc[sp].text + ' '
        result = result.strip()
        print(' ' + result)


def get_verb_phrases(sentence_doc):
    """
    Returns an object like,
    
        [(1), (5,6,7)]
        
    where this means 2 verb phrases. a single verb at index 1, another verb phrase 5,6,7.  
    
     - Adverbs are not included.
     - Infinitive phrases (and verb phrases that are subsets of infinitive phrases) are not included
     
    """ 
    pattern =  r'<VERB>*<ADV>*<VERB>+' #  r'<VERB>?<ADV>*<VERB>+' is suggested by textacy site
    verb_phrases = textacy.extract.pos_regex_matches(sentence_doc, pattern)

    result = [] # [(1), (5,6,7)] => 2 verb phrases. a single verb at index 1, another verb phrase 5,6,7
    for vp in verb_phrases:
        word_numbers = []
        # return the index of 'could have been happily eating' from 'She could have been happily eating chowder'
        first_word = vp.start

        x = first_word
        if len(vp) > 1:
            for verb_or_adverb in vp:
                # filter out adverbs
                if not verb_or_adverb.pos_ == 'ADV':
                    word_numbers.append(x)
                x += 1
        else:
            word_numbers.append(first_word)
        
        # filter out infinitive phrases
        if ( (word_numbers[0] - 1) < 0) or (sentence_doc[word_numbers[0] - 1].text.lower() != 'to'):
            result.append(word_numbers)
    
    return result



def get_verb_phrase_subject_pairs(doc):
    verb_phrases = get_verb_phrases(doc)
    verb_phrases_with_subject = []
    for vp in verb_phrases:
        subject_of_vp = []
        for word_i in vp:
            subject_of_vp += [c.i for c in doc[word_i].children if
                    c.dep_.endswith('subj')]
        verb_phrases_with_subject.append([vp, subject_of_vp])   
    return verb_phrases_with_subject 


def determine_sentence_mood(sentence_str):
    conditional_words = ["assuming", "if", "in case", "no matter how",
            "supposing", "unless"]
    result = mood(sentence_str)
    if result != 'indicative':
        return result # takes care of imperative
    for cw in conditional_words:
        if cw in sentence_str.lower():
            return 'possible_conditional'
    return result # indicative


def create_keys(verb_phrases_with_subjects, mood):
    pass

# John, working dilligently, was worried he'd be late for dinner and, tired of
# being scolded by his spouse, decided to go home. 

# verbs with no discernable subject don't need a subject if their dependency is
# advcl. Otherwise, they should be paired with the last mentioned nsubj

# John, working, was worried and Sam, worried that John was worried, began to
# cry.



def check(sentence_str):
    warnings = []
    sentence_str = textacy.preprocess.normalize_whitespace(sentence_str)
    print(sentence_str)
    sentence_str = textacy.preprocess.unpack_contractions(sentence_str)
    print(sentence_str)
    sentence_str = drop_modifiers(sentence_str)
    sentence_str = remove_double_commas(sentence_str)
    print(sentence_str)
    sentence_str = remove_prepositional_phrases(sentence_str)
    sentence_str = remove_double_commas(sentence_str)
    print(sentence_str)
    sentence_str = remove_leading_noise(sentence_str)
    print(sentence_str)
    sentence_str = substitute_infinitives_as_subjects(sentence_str)
    print(sentence_str)
    sentence_str = simplify_compound_subjects(sentence_str)
    sentence_str = remove_double_commas(sentence_str)
    sentence_str = textacy.preprocess.normalize_whitespace(sentence_str)
    print(sentence_str)
    sentence_str = sentence_str[0].upper() + sentence_str[1:]
    sentence_mood = determine_sentence_mood(sentence_str)
    doc = textacy.Doc(sentence_str, lang='en_core_web_lg')
    verb_phrases_with_subjects = get_verb_phrase_subject_pairs(doc)
    print_verb_phrases_with_subject(doc, verb_phrases_with_subjects)
    print(sentence_str)

