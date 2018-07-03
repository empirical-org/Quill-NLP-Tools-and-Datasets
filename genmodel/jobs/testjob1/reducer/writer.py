#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pika
import psycopg2
from psycopg2.extras import execute_values

try:
    DB_NAME = os.environ.get('DB_NAME', 'nlp')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_USER = os.environ.get('DB_USER', DB_NAME)
    DROPLET_NAME = os.environ['DROPLET_NAME']
    JOB_ID = os.environ['JOB_ID']
    JOB_NAME = os.environ['JOB_NAME']
    RABBIT = os.environ.get('RABBITMQ_LOCATION', 'localhost')
    REDUCTIONS_BASE = os.environ['REDUCTIONS_QUEUE_BASE']
    REDUCTIONS_QUEUE = REDUCTIONS_BASE + '_' + JOB_NAME
    WRITER_PREFETCH_COUNT = int(os.environ.get('WRITER_PREFETCH_COUNT', 100))
except KeyError as e:
    raise Exception('Warning: Important environment variables were not set')

# Connect to the database
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
cur = conn.cursor()

# #Steps:
# 1. Read reduced strings from Reduction Queue
# 2. Write reduced strings to database 

def handle_message(ch, method, properties, body):
    sent_reduction = body
    cur.execute('INSERT INTO reductions (reduction, job_id) VALUES (%s, %s)',
            (body,JOB_ID))
    conn.commit()
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':

    # Check if a writer is already running for this job, if so, exit, if not
    # mark that one is running then continue.
    cur.execute("""UPDATE jobs SET meta=jsonb_set(meta, '{reduction_writer}', %s), updated=DEFAULT
                    WHERE NOT(meta ? 'reduction_writer')
                    AND id=%s
                """, (DROPLET_NAME,JOB_ID))
    conn.commit()
    cur.execute("""SELECT COUNT(*) FROM jobs
                    WHERE meta->'reduction_writer'=%s
                    AND id=%s
                """,
            (DROPLET_NAME,JOB_ID))
    continue_running = cur.fetchone()[0] == 1
    if not continue_running:
        raise Exception('This job already has a dedicated reduction writer. Exiting')

    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT))
    channel = connection.channel()
    channel.queue_declare(queue=REDUCTIONS_QUEUE) # create queue if doesn't exist

    # NOTE: a high prefetch count is not risky here because there will only ever
    # be one writer (so this guy can't starve anyone out)
    channel.basic_qos(prefetch_count=WRITER_PREFETCH_COUNT) # limit num of unackd msgs on channel
    channel.basic_consume(handle_message, queue=REDUCTIONS_QUEUE, no_ack=False)
    channel.start_consuming()

    cur.close()
    conn.close()
