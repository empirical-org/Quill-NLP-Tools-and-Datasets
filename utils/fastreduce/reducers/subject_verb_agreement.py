#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Generate a model capable of detecting subject-verb agreement errors"""
from pattern.en import lexeme, tenses
from pattern.en import pluralize, singularize
from textstat.textstat import textstat
import hashlib
import os
import pika
import sqlite3
import textacy
RABBIT = os.environ.get('RABBITMQ_LOCATION', 'localhost')

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


def sentence_to_keys(sentence):
    doc = textacy.Doc(sentence, lang='en_core_web_lg')
    
    verb_phrases = get_verb_phrases(doc)
    
    doc_list = []
    for word in doc:
        if word.pos_ == 'VERB':
            tense_hash = hashlib.sha256((str(tenses(word.text)))).hexdigest()
            verb_number_or_pronoun = ''
            for child in word.children:
                if child.dep_ == 'nsubj':
                    if child.pos == 'PRON':
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
