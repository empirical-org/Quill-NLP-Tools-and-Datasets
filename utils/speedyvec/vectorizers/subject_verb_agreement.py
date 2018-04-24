#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Generate a model capable of detecting subject-verb agreement errors"""
from pattern.en import lexeme, tenses
from pattern.en import pluralize, singularize
from textstat.textstat import textstat
from time import sleep
import hashlib
import os
import pika
import psycopg2
import random
import re
import sqlite3
import textacy
RABBIT = os.environ.get('RABBITMQ_LOCATION', 'localhost')
DB_PASSWORD = os.environ.get('SVA_PASSWORD', '')
DB_NAME = os.environ.get('SVA_DB', 'sva')
DB_USER = os.environ.get('SVA_USER', DB_NAME)





## OLD
##########################################################################
# Indexing the sentence keys ################################################
print("Indexing sentence keys...")

# Connect to postgres
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
cur = conn.cursor()

# Select unique reductions in order of regularity, must occur at least thrice
reductions = cur.execute('SELECT reduction, count(*) from reductions group by'
        ' reduction having count(*) > 2 order by count(*) desc;')

# with ~2 million total sentences the number of unique reductions was a little
# over 12k. ~4k had more than 2 occurrences
reduction2idx = {n: i for i, n[1] in enumerate(reductions)} 
num_reductions = len(reduction2idx)

def get_vector(string):
    wordVector = np.zeros(num_reductions)
    for reduction in sentence_to_keys(string):
        index = reduction2idx.get(reduction, None)
        if index != None:
            wordVector[index] += 1
    return wordVector

# TODO: begin here with sentence_to_keys tomorrow. method should be the
# reducer... put into shared module?

# Build word vectors #####################################################
print("Building word vectors...")
#records = len(labels) # NOTE: instead get the counts from the database
records = [x for x in mangled_cursor.execute("SELECT count(*) FROM mangled_sentences LIMIT"
        " 799675")][0][0]
records += [x for x in correct_cursor.execute("SELECT count(*) FROM "
    "orignal_sentences")][0][0]
assert type(records) == int

# NOTE: use number of databse records instead of len of texts list 
#word_vectors = np.zeros((len(texts), len(vocab)), dtype=np.int_)
#for ii, text in enumerate(texts):
#    word_vectors[ii] = text_to_vector(text)


# Vectorize sentences ####################################################
print('Vectorizing sentences...')

# NOTE: this part is obviously still memory intensive, but at least its not
# quite as bad as storting strings.
word_vectors = np.zeros((records, len(vocab)), dtype=np.int_)
labels = []
ii = 0
for text, label in get_correct_or_mangled_sentence():
    word_vectors[ii] = text_to_vector(text)
    labels.append(label)
    ii+=1

# Chunk data for tensorflow ##############################################
print("Chunking data for tensorflow...")
test_fraction = 0.9

train_split, test_split = int(records*test_fraction), int(records*(1-test_fraction))
print("Train split", train_split)
print("Test split", test_split)
print("...")

##########################################################################


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
