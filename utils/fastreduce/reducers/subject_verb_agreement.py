#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Generate a model capable of detecting subject-verb agreement errors"""
from pattern.en import lexeme, tenses
from pattern.en import pluralize, singularize
from textstat.textstat import textstat
import hashlib
import os
import re
import pika
import sqlite3
import textacy
RABBIT = os.environ.get('RABBITMQ_LOCATION', 'localhost')

# NOTE:
#
# This module can be used as a package.  Just import get_reduction.
# from subject_verb_agreement import get_reduction
# get_reduction("She was tired")


# Compound noun extraction
#
# textacy.extract.pos_regex_matches(doc,
# r'(<DET>?(<NOUN|PROPN>|<PRON>)<PUNCT>)+<DET>?(<NOUN|PROPN>|<PRON>)<PUNCT>?<CCONJ><DET>?(<NOUN|PROPN>|<PRON>)')
# => matches 3 or more subjects joined by commas - oxford comma not enforced
# => NOTE: will fail on possessives : He, Louis's mom, and the dog, are dead. 
# if the coordinating conjunction is and, number should match 'they'.  We can
# use the pronoun they in our hash to replace the noun.
#
# else, if the coordinating conjunction is not and, the number should match the
# subject closest to the verb. 'The dogs, the birds, or the mailman' would get
# its number from the mailman (SINGULAR).


# #Steps:
# 1. Read strings from String Queue
# 2. Reduce strings.
# 3. Add reductions to Reduction Queue 

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


def singular_or_plural(word_string):
    if word_string == singularize(word_string):
        return 'SG'
    return 'PL'

def simplify_sentence_doc(sentence_doc):
    """Given a sentence doc, return a sentence doc based on the input with
    adjectives and adverbs removed."""
    chars_to_repl = []
    for w in sentence_doc:
        if w.pos_ == 'ADJ' or w.pos_ == 'ADV':
            # remove adverbs and adjectives
            repl = ''.ljust(len(w.text), '文') # pad w unexpected char 
            chars_to_repl.append([w.idx, w.idx + len(w.text), repl])
    
    new_sent_str = sentence_doc.text
    for replacement in chars_to_repl:
        new_sent_str = new_sent_str[:replacement[0]] + replacement[2] + \
                new_sent_str[replacement[1]:]
    new_sent_str = new_sent_str.replace('文', '')
    new_sent_str = re.sub( '\s+', ' ', new_sent_str ).strip()
    return textacy.Doc(new_sent_str, lang='en_core_web_lg')

def simplify_compound_subjects(sentence_doc):
    """Given a sentence doc, return a new sentence doc with compound subjects
    reduced to their simplest forms.

    'The man, the boy, and the girl went to school.'

    would reduce to 'They went to school'

    'The man, the boy, or the girls are frauds.'

    would reduce to 'The girls are frauds.'

    Sentences without a compund subject will not be changed at all."""
    
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



def sentence_to_keys(sentence):
    doc = textacy.Doc(sentence, lang='en_core_web_lg')
    doc = simplify_sentence_doc(doc) # remove adverbs and adj
    doc = simplify_compound_subjects(doc) # treat compound subjects right
    
    verb_phrases = get_verb_phrases(doc)
    
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
        else:
            doc_list.append(word.text)
    # Get final keys
    final_keys = []
    for vp in verb_phrases:
        vp_key_list = []
        for word_no in vp:
            vp_key_list.append(doc_list[word_no])
        vp_key = ':'.join(vp_key_list)
        final_keys.append(vp_key)
    return final_keys


def get_reduction(sent_str):
    return sentence_to_keys(sent_str)


def handle_message(ch, method, properties, body):
    sent_str = body.decode("utf-8") 
    for reduction in get_reduction(sent_str):
        channel.basic_publish(exchange='', routing_key='reductions',
                body=reduction)
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT))
    channel = connection.channel()
    channel.queue_declare(queue='strings') # create queue if doesn't exist
    channel.queue_declare(queue='reductions')

    # NOTE: if the prefetch count is too high, some workers could starve. If it
    # is too low, we make an unneccessary amount of requests to rabbitmq server 
    channel.basic_qos(prefetch_count=10) # limit num of unackd msgs on channel
    channel.basic_consume(handle_message, queue='strings', no_ack=False)
    channel.start_consuming()
