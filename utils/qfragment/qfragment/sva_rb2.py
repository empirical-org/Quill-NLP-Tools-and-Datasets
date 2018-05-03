#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Rule based system for  detecting subject-verb agreement errors (V2)"""
import textacy


'''
# Strategy

1. Drop adjectives, adverbs, determiners
2. Extract verb phrases and the noun they refer to
3. For each noun-verb pair, check that the noun and verb agree.

Hypothesis:
    We should be able to accurately determine SVA errors in past and present
    imperfective and present progressive indicative mood sentences. 

Baseline:
    - We can't detect that 'We seen some fish' is wrong.
    - We CAN detect 'I is a bad boy.'
    - '"While we were swimming at the lake, we seen some fish." flies under the
      radar
    - "While we were swimming at the lake, we begun the ceremony." does too.
    - We can't detect "While we were swimming at the lake, we bitten a cracker."
    - Or, "While we were swimming at the lake, we been chilling."
    - "He agreed me." is marked right.
    - "A fish bit me." is marked wrong.
    - "He walked store." is marked right.

Why do these errors exist?
    - We don't record if the verb is transitive or intransitive
        * most act as both, but only can pair with certain other verbs, "walk it
          back" is ok "walk the dog" is fine. "walk the store" is wrong. "Dance
          the potion" is wrong, "Dance the night away" is fine. 
    - We don't record the mood of the sentence subjunctive / conditional /
      imperative / indicative?
    - No special treatment for posessive pronouns / nouns


Limitations:
    1. 

Strategy
    0. Unpack contractions
    1. Drop adjectives, adverbs [JJ, JJR, JJS, RB, RBR, RBS] 
    2. Extract verb phrases and the noun they refer to

'''

# private


# public
def drop_modifiers(sentence_str):
    """Given a string, drop the modifiers and return a string 
    without them"""
    tdoc = textacy.Doc(sentence_str, lang='en_core_web_lg')
    new_sent = tdoc.text 
    unusual_char = '形'
    for tag in tdoc:
        if tag.dep_.endswith('mod'): 
            # Replace the tag
            new_sent = new_sent[:tag.idx] + unusual_char * len(tag.text) +\
                    new_sent[tag.idx + len(tag.text):]
    new_sent = new_sent.replace(unusual_char, '')
    new_sent = textacy.preprocess.normalize_whitespace(new_sent)
    return new_sent

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



    doc_list = []
    for word in doc:
        if word.pos_ == 'VERB':
            tense_hash = hashlib.sha256((str(tenses(word.text)))).hexdigest()
            verb_number_or_pronoun = ''
            for child in word.children:
                if child.dep_ == 'nsubj':
                    if child.pos_ == 'PRON':
                        verb_number_or_pronoun = child.text.upper()
                    else:
                        verb_number_or_pronoun = singular_or_plural(child.text)
                    break
        
            doc_list.append(tense_hash + '>' + verb_number_or_pronoun)

def check(sentence_str):
    sentence_str = textacy.preprocess.normalize_whitespace(sentence_str)
    sentence_str = textacy.preprocess.unpack_contractions(sentence_str)
    sentence_str = drop_modifiers(sentence_str)
    doc = textacy.Doc(sentence_str, lang='en_core_web_lg')
    verb_phrases = get_verb_phrases(doc)
    for vp in verb_phrases:
        for word_i in vp:
            child.dep_.endswith('subj'): # nsubj, csubj



# tests
def test_drop_modifiers():
    s = "This is a very descriptive sentence."
    a = "This is a sentence."
    s2 = drop_modifiers(s)
    assert s2 == a


def run_tests():
    test_drop_modifiers()






    





