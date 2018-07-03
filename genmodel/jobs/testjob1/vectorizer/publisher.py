from time import sleep
import json
import os
import pika
import psycopg2

try:
    DB_NAME = os.environ.get('DB_NAME', 'nlp')
    DB_PASSWORD = os.environ.get('DB_PASS', '')
    DB_USER = os.environ.get('DB_USER', DB_NAME)
    DROPLET_NAME = os.environ['DROPLET_NAME']
    JOB_ID = os.environ['JOB_ID']
    JOB_NAME = os.environ['JOB_NAME']
    MAX_QUEUE_LEN = int(os.environ.get('MAX_QUEUE_LEN', 500))
    PRE_VECTORS_BASE = os.environ['PRE_VECTORS_QUEUE_BASE']
    PRE_VECTORS_QUEUE = PRE_VECTORS_BASE + '_' + JOB_NAME
    RABBIT = os.environ.get('RABBITMQ_LOCATION', 'localhost')
except KeyError as e:
    raise Exception('Warning: Important environment variables were not set')


# #Steps
#
# 1. Connect to the database
# 2. Start adding sentences to PRE_REDUCTIONS_QUEUE


if __name__ == '__main__':
    # Connect to the database
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
            host='localhost')
    cur = conn.cursor()

    # Check if a publisher is already running for this job, if so exit, if not
    # mark that one is running then continue.
    cur.execute("""UPDATE jobs SET meta=jsonb_set(meta, '{vector_publisher}', %s), updated=DEFAULT
                    WHERE NOT(meta ? 'vector_publisher')
                    AND id=%s
                """, (json.dumps(DROPLET_NAME),JOB_ID))
    conn.commit()
    cur.execute("""SELECT COUNT(*) FROM jobs
                    WHERE meta->'vector_publisher'=%s
                    AND id=%s
                """,
            (json.dumps(DROPLET_NAME),JOB_ID))
    continue_running = cur.fetchone()[0] == 1
    if not continue_running:
        raise Exception('This job already has a dedicated vector publisher. Exiting')

    # Issue select statements
    cur.execute("SELECT data,label from labeled_data WHERE job_id=%s ORDER BY RANDOM()",
            (JOB_ID,))

    # Connect to pika
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT))
    channel = connection.channel()
    
    # Declare queue if doesn't exist, get reference to queue
    q = channel.queue_declare(queue=PRE_VECTORS_QUEUE)
    q_len = q.method.message_count
    sent_str = True # loop must run at least once!
    label = None

    while sent_str:
        while q_len < MAX_QUEUE_LEN and sent_str:
            n = cur.fetchone()
            sent_str = n if n is None else json.dumps({'sent_str': n[0],
                'label': n[1]})
            # add the sent string to the queue
            channel.basic_publish(exchange='', routing_key=PRE_VECTORS_QUEUE,
                    body=json.dumps(sent_str))
            q = channel.queue_declare(queue=PRE_VECTORS_QUEUE)
            q_len = q.method.message_count
        sleep(1) # when the q length reaches x, take a little break
        q = channel.queue_declare(queue=PRE_VECTORS_QUEUE)
        q_len = q.method.message_count

    # update state to pre-vectors-queued
    cur.execute("""UPDATE jobs SET state=%s, updated=DEFAULT
                    WHERE id=%s
                """, ('pre-vectors-queued',JOB_ID))
    conn.commit()

    # wait until all messages have been acked
    q = channel.queue_declare(queue=PRE_VECTORS_QUEUE)
    q_len = q.method.message_count
    while q_len > 0:
        sleep(2)
        q = channel.queue_declare(queue=PRE_VECTORS_QUEUE)
        q_len = q.method.message_count

    # update state to vectorized
    cur.execute("""UPDATE jobs SET state=%s, updated=DEFAULT
                    WHERE id=%s
                """, ('vectorized',JOB_ID))
    conn.commit()

    print("{} has been fully populated.".format(PRE_VECTORS_QUEUE))
    print("Publisher Exiting.")
    cur.close()
    conn.close()
