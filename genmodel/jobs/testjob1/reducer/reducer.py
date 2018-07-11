#!/usr/bin/env python
# -*- coding: utf-8 -*-
from reducer_helper import get_reduction
import logging
import os
import pika
import re
import socket

FNAME=os.path.basename(__file__)
PID=os.getpid()
HOST=socket.gethostname()

# set up logging
log_filename='reducer_{}.log'.format(os.getpid())
log_format = '%(levelname)s %(asctime)s {pid} {filename} %(lineno)d %(message)s'.format(
        pid=PID, filename=FNAME)
logging.basicConfig(format=log_format,
    filename='/var/log/reducerlogs/{}'.format(log_filename),
    datefmt='%Y-%m-%dT%H:%M:%S%z',
    level=logging.INFO)
logger = logging.getLogger('reducer')

try:
    JOB_NAME = os.environ['JOB_NAME']
    PRE_REDUCTIONS_BASE = os.environ['PRE_REDUCTIONS_QUEUE_BASE']
    PRE_REDUCTIONS_QUEUE = PRE_REDUCTIONS_BASE + '_' + JOB_NAME
    RABBIT = os.environ.get('RABBITMQ_LOCATION', 'localhost')
    REDUCER_PREFETCH_COUNT = int(os.environ.get('REDUCER_PREFETCH_COUNT', 10))
    REDUCTIONS_BASE = os.environ['REDUCTIONS_QUEUE_BASE']
    REDUCTIONS_QUEUE = REDUCTIONS_BASE + '_' + JOB_NAME
except KeyError as e:
    logger.critical("important environment variables were not set.")
    raise Exception('important environment variables were not set')

def handle_message(ch, method, properties, body):
    body = body.decode('utf-8')
    try:
        for reduction in get_reduction(body):
            channel.basic_publish(exchange='', routing_key=REDUCTIONS_QUEUE,
                    body=reduction)
        logger.debug("queued reduction")
    except Exception as e:
        logger.error("problem handling message - {}".format(e))
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT))
    channel = connection.channel()
    channel.queue_declare(queue=PRE_REDUCTIONS_QUEUE) # create queue if doesn't exist
    channel.queue_declare(queue=REDUCTIONS_QUEUE)

    # NOTE: if the prefetch count is too high, some workers could starve. If it
    # is too low, we make an unneccessary amount of requests to rabbitmq server 
    channel.basic_qos(prefetch_count=REDUCER_PREFETCH_COUNT) # limit num of unackd msgs on channel
    channel.basic_consume(handle_message, queue=PRE_REDUCTIONS_QUEUE, no_ack=False)
    channel.start_consuming()
