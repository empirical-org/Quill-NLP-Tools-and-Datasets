#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Preprocess sentences and reduce them."""
import textacy
import re


def remove_adverbial_clauses(sentence_str):
    """Given a string, drop any adverbial clauses."""
    # should also return updated indexes
    # Sam , worried, asked him.
    # [0, 0, 0, 0, 3, 3, 3]
    tdoc = textacy.Doc(sentence_str, lang='en_core_web_lg')
    advcl_phrases = [] #=> [(start.i, end.i), ...]
    has_advcl = False
    start = None
    for w in tdoc:
        if w.tag_ == ',' and has_advcl: # end phrase, start next
            if start: # end phrase if started
                advcl_phrases.append((start.i, w.i))
            start = w
            has_advcl = False
        elif w.tag_ == ',': # start phrase
            start = w
            has_advcl = False
        if w.dep_ == 'advcl':
            has_advcl = True
    
    new_sent_str = sentence_str 
    unusual_char = '形'
    for advcl in advcl_phrases:
        start = tdoc[advcl[0]].idx
        end = tdoc[advcl[1]].idx + len(tdoc[advcl[1]].text)
        sub = unusual_char * (end - start)
        new_sent_str = new_sent_str[:start] + sub + new_sent_str[end:] 
    new_sent_str = new_sent_str.replace(unusual_char, '')
    return new_sent_str



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


def remove_prepositional_phrases(sentence_str):
    """Given a string, drop the prepositional phrases and return a new string
    without them"""
    sentence_doc = textacy.Doc(sentence_str, lang='en_core_web_lg')
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



def substitute_infinitives_as_subjects(sent_str):
    """If an infinitive is used as a subject, substitute the gerund."""
    sent_doc = textacy.Doc(sent_str, lang='en_core_web_lg')
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

        revised_compound_subjects = []
        for cs in compound_subjects:
            new_cs = cs
            if not [w for w in cs if w.dep_ == 'nsubj']:
                continue # there is no subject here, no need to add
            nsubj = [w for w in cs if w.dep_ == 'nsubj'][0]
            for w3 in cs:

                if (w3 != nsubj and w3.head != nsubj):
                    new_cs = new_cs[w3.i + 1:]
                elif w3.pos_ == 'VERB': 
                    new_cs = new_cs[w3.i + 1:]
                else:
                    break # as soon as we hit a good one, add all remaining
            
            revised_compound_subjects.append(new_cs)
        
        for cs in revised_compound_subjects:
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

    return new_sent_str
