import pika
import os
import psycopg2
import random
from time import sleep
import json
"""Publish sentences with subject verb agreement errors and correct sentneces to
the fstrings queue"""
RABBIT = os.environ.get('RABBITMQ_LOCATION', 'localhost')
DB_PASSWORD = os.environ.get('SVA_PASSWORD', '')
DB_NAME = os.environ.get('SVA_DB', 'sva')
DB_USER = os.environ.get('SVA_USER', DB_NAME)


# #Steps
#
# 1. Connect to the database
# 2. Start adding sentences to string queue


if __name__ == '__main__':
    print("Subject Verb Agreement SentStr Publisher Started.")
    # Connect to the database
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)

    # Issue select statements
    mangledcur = conn.cursor()
    originalcur = conn.cursor()
    mangledcur.execute("SELECT sentence FROM mangled_sentences ORDER BY "
            "RANDOM() LIMIT 799675;")
    originalcur.execute("SELECT sentence FROM orignal_sentences;")

    # Connect to pika
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT))
    channel = connection.channel()
    
    # Declare queue if doesn't exist, get reference to queue
    q = channel.queue_declare(queue='fstrings')
    q_len = q.method.message_count
    sent_str = True # loop must run at least once!
    label=None # tells whether sentence is mangled or not

    while sent_str:
        while q_len < 500 and sent_str:
            mangled = random.choice([True, False])
            if mangled:
                n = mangledcur.fetchone()
                sent_str = n if n is None else n[0]
                label=1
            if not mangled or not sent_str:
                n = originalcur.fetchone()
                sent_str = n if n is None else n[0]
                label=0
            if not mangled and not sent_str:
                n = mangledcur.fetchone()
                sent_str = n if n is None else n[0]
                if sent_str:
                    label=1
                else:
                    label=None

            # add the labeled sent string to the queue
            labeled_sent_str = json.dumps({'sent_str': sent_str, 'label': label})
            channel.basic_publish(exchange='', routing_key='fstrings',
                    body=labeled_sent_str)
            q = channel.queue_declare(queue='fstrings')
            q_len = q.method.message_count
        sleep(1) # when the q length reaches x, take a little break
        q = channel.queue_declare(queue='fstrings')
        q_len = q.method.message_count

    print("String Q has been fully populated.")
    print("Subject Verb Agreement SentStr Publisher Exiting.")
    cur.close()
    conn.close()
