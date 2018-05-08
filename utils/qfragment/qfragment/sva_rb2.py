#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Rule based system for  detecting subject-verb agreement errors (V2)"""
import textacy
import re
from pattern.en import conjugate


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


Strategy
    0. Unpack contractions
    1. Drop modifiers 
    2. Simplify compound subjectects
    3. Extract verb phrases and the noun they refer to

'''

def raise_be_error(verb_phrase_doc):
    pass

def raise_be_not_followed_by_participle(verb_phrase_doc):
    """If the mood is indicative, a participle (past or present) should follow
    a form of be if any verb does"""
    # TODO: implement

def raise_participle_not_preceded_by_be(verb_phrase_doc):
    """If a past or present participle verb has a subject it must be preceded by
    a form of be"""
    # TODO: implement
    pass

def raise_no_infinitive_after_modal(verb_phrase_doc):
    # TODO: implement
    pass



def raise_auxilary_error(verb_phrase_doc):
    """be (am,
    are,
    is,
    was,
    were,
    being,
    been),
    can,
    could,
    dare,
    do (does,
    did),
    have (has,
    had,
    having),
    may,
    might,
    must,
    need,
    ought,
    shall,
    should,
    will,
    would"""

def raise_double_modal_error(verb_phrase_doc):
    """A modal auxilary verb should not follow another modal auxilary verb"""
    prev_word = None
    for word in verb_phrase:
        if word.tag_ == 'MD' and prev_word.tag == 'MD':
            raise('DoubleModalError')
        prev_word = word


def raise_modal_error(verb_phrase_doc):
    """Given a verb phrase, raise an error if the modal auxilary has an issue
    with it"""
    verb_phrase = verb_phrase_doc.text.lower()
    bad_strings = ['should had', 'should has', 'could had', 'could has', 'would '
            'had', 'would has'] ["should", "could", "would"]
    for bs in bad_strings:
        if bs in verb_phrase:
            raise('ShouldCouldWouldError')


def raise_verb_phrase_error(verb_phrases):
    """Given a list of verb phrases, raise an error on a verb phrase that is
    unacceptable. ie,

    - 'could be swimming' is ok
    - 'love is run' is not
    """

    





def substitute_infinitives_as_subjects(sent_str):
    """If an infinitive is used as a subject, substitute the gerund."""
    sent_doc = textacy.Doc(sent_str, lang='en_core_web_lg')
    #inf_pattern = r'<PART><VERB>+' # To aux/auxpass* csubj
    inf_pattern = r'<PART><VERB>' # To aux/auxpass* csubj
    infinitives = textacy.extract.pos_regex_matches(sent_doc, inf_pattern)
    inf_subjs = [] # => [[0,1],...]
    for inf in infinitives:
        if inf[0].text.lower() != 'to':
            continue
        if ('csubj' not in [w.dep_ for w in inf] and sent_doc[inf[-1].i + 1].dep_
                != 'csubj'):
            continue
        if inf[-1].tag_ != 'VB':
            continue
        inf_subj = []
        for v in inf:
            inf_subj.append(v.i)
        inf_subjs.append(inf_subj) 
    new_sent_str = sent_str
    unusual_char = '形'
    for inf_subj in inf_subjs:
        start_inf = sent_doc[inf_subj[0]].idx 
        end_inf = sent_doc[inf_subj[-1]].idx + len(sent_doc[inf_subj[-1]])
        inf_len = end_inf - start_inf
        sub = (unusual_char * inf_len)
        new_sent_str = new_sent_str[:start_inf] + sub + new_sent_str[end_inf:]
    new_sent_str = re.sub('形+', '{}', new_sent_str)
    repl = [conjugate(sent_doc[i_s[-1]].text, tense='presentparticiple') for i_s in inf_subjs]
    return new_sent_str.format(*repl)
    

def remove_prepositional_phrases(sentence_str):
    sentence_doc = textacy.Doc(sentence_str, lang='en_core_web_lg')
    # possessive pronouns labled as ADJ
    pp_pattern = r'<ADP><ADJ|DET>?(<NOUN>+<ADP>)*<NOUN>+'
    prep_phrases = textacy.extract.pos_regex_matches(sentence_doc,
            pp_pattern)
    new_sent_str = sentence_str
    unusual_char = '形'
    for pp in prep_phrases:
        sub = unusual_char * len(pp.text)
        new_sent_str = new_sent_str[:pp[0].idx] + sub + new_sent_str[pp[0].idx +
                len(pp.text):]
    new_sent_str = new_sent_str.replace(unusual_char, '')
    return new_sent_str

# private
def simplify_compound_subjects(sentence_str):
    """Given a sentence doc, return a new sentence doc with compound subjects
    reduced to their simplest forms.

    'The man, the boy, and the girl went to school.'

    would reduce to 'They went to school'

    'The man, the boy, or the girls are frauds.'

    would reduce to 'The girls are frauds.'

    Sentences without a compund subject will not be changed at all."""

    sentence_doc = textacy.Doc(sentence_str, lang='en_core_web_lg')
    
    cs_patterns = \
            [r'((<DET>?(<NOUN|PROPN>|<PRON>)+<PUNCT>)+<DET>?(<NOUN|PROPN>|<PRON>)+<PUNCT>?<CCONJ><DET>?(<NOUN|PROPN>|<PRON>)+)|'\
            '(<DET>?(<NOUN|PROPN>|<PRON>)<CCONJ><DET>?(<NOUN|PROPN>|<PRON>))']

    for cs_pattern in cs_patterns:
    
        compound_subjects = textacy.extract.pos_regex_matches(sentence_doc,
                cs_pattern)

        chars_to_repl = [] # [(start_repl, end_repl, replacement), (start_repl,
        # end_repl, replacement), ...] 
        
        for cs in compound_subjects:
            for w in cs:
                if w.pos_ == 'CCONJ' and w.text.lower() == 'and':
                    # replace with they
                    repl = 'they'.ljust(len(cs.text), '文') # pad w unexpected char 
                    chars_to_repl.append([cs[0].idx, cs[-1].idx + len(cs[-1].text), repl])

                elif w.pos_ == 'CCONJ' and w.text.lower() != 'and':
                    # replace with final <DET>?(<NOUN|PROPN>|<PRON>)
                    repl = cs[-1:].text
                    if cs[-2].pos_ == 'DET':
                        repl = cs[-2:].text
                    repl = repl.ljust(len(cs.text), '文') # pad w unexpected char 
                    
                    chars_to_repl.append([cs[0].idx, cs[-1].idx + len(cs[-1].text), repl])
        
        new_sent_str = sentence_doc.text
        for replacement in chars_to_repl:
            new_sent_str = new_sent_str[:replacement[0]] + replacement[2] + \
                    new_sent_str[replacement[1]:]
        new_sent_str = new_sent_str.replace('文', '')
        new_sent_str = re.sub( '\s+', ' ', new_sent_str ).strip()

    sentence_doc = textacy.Doc(new_sent_str, lang='en_core_web_lg')
    return sentence_doc


def split_infinitive_warning(sentence_str):
    """Return a warning for a split infinitive, else, None"""
    sent_doc = textacy.Doc(sentence_str, lang='en_core_web_lg')
    inf_pattern = r'<PART><ADV><VERB>' # To aux/auxpass* csubj
    infinitives = textacy.extract.pos_regex_matches(sent_doc, inf_pattern)
    for inf in infinitives:
        if inf[0].text.lower() != 'to':
            continue
        if inf[-1].tag_ != 'VB':
           continue 
        return 'SplitInfinitiveWarning'

def raise_infinitive_error(sentence_str):
    """Given a string, check that all infinitives are properly formatted"""
    sent_doc = textacy.Doc(sentence_str, lang='en_core_web_lg')
    inf_pattern = r'<PART|ADP><VERB>' # To aux/auxpass* csubj
    infinitives = textacy.extract.pos_regex_matches(sent_doc, inf_pattern)
    for inf in infinitives:
        if inf[0].text.lower() != 'to':
            continue
        if inf[-1].tag_ != 'VB':
            raise Exception('InfinitivePhraseError')

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

def check_agreement(doc, verb_phrase, noun_phrase):
    pass

def remove_double_commas(sent_str):
    return re.sub('\s*,[\s,]*', ', ', sent_str)


def check(sentence_str):
    warnings = []
    sentence_str = textacy.preprocess.normalize_whitespace(sentence_str)
    sentence_str = textacy.preprocess.unpack_contractions(sentence_str)
    sentence_str = drop_modifiers(sentence_str)
    sentence_str = remove_prepositional_phrases(sentence_str)
    sentence_str = textacy.preprocess.normalize_whitespace(sentence_str)
    sentence_str = remove_double_commas(sentence_str)
    sentence_str = substitute_infinitives_as_subjects(sentence_str)
    doc = simplify_compound_subjects(sentence_str)
    verb_phrases_with_subjects = get_verb_phrase_subject_pairs(doc)


    # raise errors
    raise_infinitive_error(sentence_str)
    raise_verb_phrase_error(verb_phrases_with_subject)

    # add warnings
    w1 = split_infinitive_warning(sent_str)
    warnings += [w1] if w1 is not None else []



    print_verb_phrases_with_subject(doc, verb_phrases_with_subjects)




# tests
def test_drop_modifiers():
    s = "This is a very descriptive sentence."
    a = "This is a sentence."
    s2 = drop_modifiers(s)
    assert s2 == a


def run_tests():
    test_drop_modifiers()






    





