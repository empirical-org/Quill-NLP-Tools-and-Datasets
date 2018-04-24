#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Generate a model capable of detecting subject-verb agreement errors"""
from pattern.en import lexeme, tenses
from pattern.en import pluralize, singularize
import os
import pika
import psycopg2
from psycopg2.extras import execute_values
RABBIT = os.environ.get('RABBITMQ_LOCATION', 'localhost')
DB_PASSWORD = os.environ.get('SVA_PASSWORD', '')
DB_NAME = os.environ.get('SVA_DB', 'sva')
DB_USER = os.environ.get('SVA_USER', DB_NAME)
BULK_INSERT_SIZE = int(os.environ.get('SVA_REDUCTIONS_BATCH_SIZE', '5000'))

# Connect to the database
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
cur = conn.cursor()

# Values # TODO: consider using copy to/from
#reductions_to_insert = [] # [('xasdasdasd:adadsasd>PL',), ('asdd:SG',), ...]

# #Steps:
# 1. Read reduced strings from Reduction Queue
# 2. Write reduced strings to database 

def handle_message(ch, method, properties, body):
    sent_reduction = body.decode("utf-8") 
    #reductions_to_insert.append([sent_reduction])
    #if len(reductions_to_insert) > BULK_INSERT_SIZE:
    #    # add sent reduction to database
    #    execute_values(cur, "INSERT INTO reductions (reduction) VALUES %s", reductions_to_insert)
    #    reductions_to_insert = []
    cur.execute('INSERT INTO reductions (reduction) VALUES (%s)', (sent_reduction,))
    conn.commit()
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT))
    channel = connection.channel()
    channel.queue_declare(queue='reductions') # create queue if doesn't exist

    # NOTE: a high prefetch count is not risky here because there will only ever
    # be one writer (so this guy can't starve anyone out)
    channel.basic_qos(prefetch_count=100) # limit num of unackd msgs on channel
    channel.basic_consume(handle_message, queue='reductions', no_ack=False)
    channel.start_consuming()

    cur.close()
    conn.close()
