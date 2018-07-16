from time import sleep
import json
import logging
import os
import pika
import psycopg2
import random
import socket

FNAME=os.path.basename(__file__)
PID=os.getpid()
HOST=socket.gethostname()

# set up logging
log_filename='publisher_{}.log'.format(os.getpid())
log_format = '%(levelname)s %(asctime)s {pid} {filename} %(lineno)d %(message)s'.format(
        pid=PID, filename=FNAME)
logging.basicConfig(format=log_format,
    filename='/var/log/reducerlogs/{}'.format(log_filename),
    datefmt='%Y-%m-%dT%H:%M:%S%z',
    level=logging.INFO)
logger = logging.getLogger('publisher')

try:
    DROPLET_NAME = os.environ['DROPLET_NAME']
    DB_NAME = os.environ.get('DB_NAME', 'nlp')
    DB_PASSWORD = os.environ.get('DB_PASS', '')
    DB_USER = os.environ.get('DB_USER', DB_NAME)
    JOB_ID = os.environ['JOB_ID']
    JOB_NAME = os.environ['JOB_NAME']
    MAX_QUEUE_LEN = int(os.environ.get('MAX_QUEUE_LEN', 500))
    PRE_REDUCTIONS_BASE = os.environ['PRE_REDUCTIONS_QUEUE_BASE']
    PRE_REDUCTIONS_QUEUE = PRE_REDUCTIONS_BASE + '_' + JOB_NAME
    RABBIT = os.environ.get('RABBITMQ_LOCATION', 'localhost')
except KeyError as e:
    logger.critical("important environment variables were not set")
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
    cur.execute("""UPDATE jobs SET meta=jsonb_set(meta, '{reduction_publisher}', %s), updated=DEFAULT
                    WHERE NOT(meta ? 'reduction_publisher')
                    AND id=%s
                """, (json.dumps(DROPLET_NAME),JOB_ID))
    conn.commit()
    cur.execute("""SELECT COUNT(*) FROM jobs WHERE
                    meta->'reduction_publisher'=%s 
                    AND id=%s
                """,
            (json.dumps(DROPLET_NAME), JOB_ID))
    continue_running = cur.fetchone()[0] == 1
    if not continue_running:
        logger.info('job already has dedicated pre-reductions publisher, exiting')
        raise Exception('This job already has a dedicated reduction publisher. Exiting')

    # Issue select statements - cast to json from jsonb
    cur.execute("SELECT data::json from labeled_data WHERE job_id=%s ORDER BY RANDOM()",
            (JOB_ID,))

    # Connect to pika
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT))
    channel = connection.channel()
    
    # Declare queue if doesn't exist, get reference to queue
    q = channel.queue_declare(queue=PRE_REDUCTIONS_QUEUE)
    q_len = q.method.message_count
    sent_str = True # loop must run at least once!

    while sent_str:
        while q_len < MAX_QUEUE_LEN and sent_str:
            messages = []
            for n in cur.fetchmany(MAX_QUEUE_LEN):
                sent_str = n if n is None else n[0]
                # add the sent string to the queue
                # TODO: is this adding a null string to the queue? doesn't seem to
                # cause issues if it is..
                channel.basic_publish(exchange='', routing_key=PRE_REDUCTIONS_QUEUE,
                        body=json.dumps(sent_str))
                messages.append('queued pre-reduction')
            # since writing to a file takes time, publish to the queue then
            # write to a file later
            for message in messages:
                logger.info(message)
            #logger.info('queued pre-reduction') # writ
            q = channel.queue_declare(queue=PRE_REDUCTIONS_QUEUE)
            q_len = q.method.message_count
        sleep(1) # when the q length reaches x, take a little break
        logger.debug('pre reductions queue at capacity, sleeping')
        q = channel.queue_declare(queue=PRE_REDUCTIONS_QUEUE)
        q_len = q.method.message_count

    # update state to pre-reductions-queued
    cur.execute("""UPDATE jobs SET state=%s, updated=DEFAULT
                    WHERE id=%s
                """, ('pre-reductions-queued',JOB_ID))
    conn.commit()
    logger.info('all pre-reductions have been queued. waiting for acks')

    # wait until all messages have been acked
    q = channel.queue_declare(queue=PRE_REDUCTIONS_QUEUE)
    q_len = q.method.message_count
    while q_len > 0:
        sleep(2)
        q = channel.queue_declare(queue=PRE_REDUCTIONS_QUEUE)
        q_len = q.method.message_count

    logger.info('all pre-reductions have been acked. setting state to reduced.')

    # update state to reduced
    cur.execute("""UPDATE jobs SET state=%s, updated=DEFAULT
                    WHERE id=%s
                """, ('reduced',JOB_ID))
    conn.commit()

    logger.info('exiting')
    cur.close()
    conn.close()
