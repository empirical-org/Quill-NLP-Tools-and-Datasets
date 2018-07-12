#!/usr/bin/env python
# -*- coding: utf-8 -*-
from vectorizer_helper import get_vector
import json
import logging
import os
import pika
import re
import socket


FNAME=os.path.basename(__file__)
PID=os.getpid()
HOST=socket.gethostname()

# set up logging
log_filename='vectorizer_{}.log'.format(os.getpid())
log_format = '%(levelname)s %(asctime)s {pid} {filename} %(lineno)d %(message)s'.format(
        pid=PID, filename=FNAME)
logging.basicConfig(format=log_format,
    filename='/var/log/vectorizerlogs/{}'.format(log_filename),
    datefmt='%Y-%m-%dT%H:%M:%S%z',
    level=logging.INFO)
logger = logging.getLogger('vectorizer')

try:
    JOB_NAME = os.environ['JOB_NAME']
    PRE_VECTORS_BASE = os.environ['PRE_VECTORS_QUEUE_BASE']
    PRE_VECTORS_QUEUE = PRE_VECTORS_BASE + '_' + JOB_NAME
    RABBIT = os.environ.get('RABBITMQ_LOCATION', 'localhost')
    VECTORIZER_PREFETCH_COUNT = int(os.environ.get('VECTORIZER_PREFETCH_COUNT', 10))
    VECTORS_BASE = os.environ['VECTORS_QUEUE_BASE']
    VECTORS_QUEUE = VECTORS_BASE + '_' + JOB_NAME
except KeyError as e:
    logger.critical('important environment variables were not set')
    raise Exception('Warning: Important environment variables were not set')



def handle_message(ch, method, properties, body):
    body = body.decode('utf-8')
    try:
        vector = get_vector(body)
        channel.basic_publish(exchange='', routing_key=VECTORS_QUEUE,
                body=json.dumps(vector))
        logger.info('queued vector')
    except Exception as e:
        logger.error("problem handling message - {}".format(e))
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT))
    channel = connection.channel()
    channel.queue_declare(queue=PRE_VECTORS_QUEUE) # create queue if doesn't exist
    channel.queue_declare(queue=VECTORS_QUEUE)

    # NOTE: if the prefetch count is too high, some workers could starve. If it
    # is too low, we make an unneccessary amount of requests to rabbitmq server 
    channel.basic_qos(prefetch_count=10) # limit num of unackd msgs on channel
    channel.basic_consume(handle_message, queue=PRE_VECTORS_QUEUE, no_ack=False)
    channel.start_consuming()
