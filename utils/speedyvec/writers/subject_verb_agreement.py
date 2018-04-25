#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Generate a model capable of detecting subject-verb agreement errors"""
from pattern.en import lexeme, tenses
from pattern.en import pluralize, singularize
import os
import pika
import psycopg2
import json
from psycopg2.extras import execute_values
RABBIT = os.environ.get('RABBITMQ_LOCATION', 'localhost')
DB_PASSWORD = os.environ.get('SVA_PASSWORD', '')
DB_NAME = os.environ.get('SVA_DB', 'sva')
DB_USER = os.environ.get('SVA_USER', DB_NAME)
BULK_INSERT_SIZE = int(os.environ.get('SVA_REDUCTIONS_BATCH_SIZE', '5000'))

# Ensure new table exists
# create table vectors (id serial, vector varchar, label integer);

# Connect to the database
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
cur = conn.cursor()

# #Steps:
# 1. Read vectorized string from Reduction Queue
# 2. Write vectorized string to database 

def handle_message(ch, method, properties, body):
    labeled_sent_vector = json.loads(body) 
    sent_vector = labeled_sent_vector['vector'] 
    label = labeled_sent_vector['label'] 
    # TODO: bulk / batch inserts are faster. This should be changed to to
    # batches
    cur.execute('INSERT INTO vectors (vector, label) VALUES (%s, %s)',
            (sent_vector, label))
    conn.commit()
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT))
    channel = connection.channel()
    channel.queue_declare(queue='vectors') # create queue if doesn't exist

    # NOTE: a high prefetch count is not risky here because there will only ever
    # be one writer (so this guy can't starve anyone out)
    channel.basic_qos(prefetch_count=100) # limit num of unackd msgs on channel
    channel.basic_consume(handle_message, queue='vectors', no_ack=False)
    channel.start_consuming()

    cur.close()
    conn.close()
