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
import json
import pika
import psycopg2
import random
import re
import sqlite3
import textacy
from sva_reducer import get_reduction
print("You just imported get_reduction from sva_reducer. This reduction"
        "algorithm should be the same as the one used to create your previous"
        "reducutions.")
RABBIT = os.environ.get('RABBITMQ_LOCATION', 'localhost')
DB_PASSWORD = os.environ.get('SVA_PASSWORD', '')
DB_NAME = os.environ.get('SVA_DB', 'sva')
DB_USER = os.environ.get('SVA_USER', DB_NAME)

# Indexing the sentence keys ################################################
print("Indexing sentence keys...")

# Connect to postgres
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
cur = conn.cursor()


# Select unique reductions in order of regularity, must occur at least thrice
cur.execute('SELECT reduction, count(*) from reductions group by'
        ' reduction having count(*) > 2 order by count(*) desc;')

# with ~2 million total sentences the number of unique reductions was a little
# over 12k. ~5k had more than 2 occurrences
reduction2idx = {n[0]: i for i, n in enumerate(cur)} 
num_reductions = len(reduction2idx)


# close connections to database
cur.close()
conn.close()

# Vectorizing sentence keys ################################################
print('Vectorizing sentence keys...')


# vectors must be convertable to  a numpy array. 
# NOTE: storing the number of reductions on each object is not necessary and is
# increasing db size. The advantage is that each row can compute its numpy
# vector with no database calls which is why we choose it.  We might undecide
# this at some point.
# Ex:
# {indices={5:1, 6:2, 500:1, 6003:2} num_reductions=5000}
# {indicies={index:count, index:count, ...} reductions=num_reductions}
def get_vector(string):
    result = {'indices':{}, 'reductions':num_reductions}
    for reduction in get_reduction(string):
        index = reduction2idx.get(reduction)
        if index:
            result['indices'][index] = result['indices'].get(index, 0) + 1
    return result


def handle_message(ch, method, properties, body):
    labeled_sent_dict = json.loads(body)
    sent_str = labeled_sent_dict['sent_str'] 
    label = labeled_sent_dict['label']
    for vector in get_vector(sent_str):
        labeled_vector = json.dumps({'vector':vector, 'label':label})
        channel.basic_publish(exchange='', routing_key='vectors',
                body=labeled_vector)
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT))
    channel = connection.channel()
    channel.queue_declare(queue='fstrings') # create queue if doesn't exist
    channel.queue_declare(queue='vectors')

    # NOTE: if the prefetch count is too high, some workers could starve. If it
    # is too low, we make an unneccessary amount of requests to rabbitmq server 
    channel.basic_qos(prefetch_count=10) # limit num of unackd msgs on channel
    channel.basic_consume(handle_message, queue='fstrings', no_ack=False)
    channel.start_consuming()
