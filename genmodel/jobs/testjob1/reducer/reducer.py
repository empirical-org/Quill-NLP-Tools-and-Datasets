#!/usr/bin/env python
# -*- coding: utf-8 -*-
from reducer_helper import get_reduction
import os
import pika
import re

try:
    JOB_NAME = os.environ['JOB_NAME']
    PRE_REDUCTIONS_BASE = os.environ['PRE_REDUCTIONS_QUEUE_BASE']
    PRE_REDUCTIONS_QUEUE = PRE_REDUCTIONS_BASE + '_' + JOB_NAME
    RABBIT = os.environ.get('RABBITMQ_LOCATION', 'localhost')
    REDUCER_PREFETCH_COUNT = int(os.environ.get('REDUCER_PREFETCH_COUNT', 10))
    REDUCTIONS_BASE = os.environ['REDUCTIONS_QUEUE_BASE']
    REDUCTIONS_QUEUE = REDUCTIONS_BASE + '_' + JOB_NAME
except KeyError as e:
    raise Exception('Warning: Important environment variables were not set')

def handle_message(ch, method, properties, body):
    body = body.decode('utf-8')
    try:
        for reduction in get_reduction(body):
            channel.basic_publish(exchange='', routing_key=REDUCTIONS_QUEUE,
                    body=reduction)
    except Exception as e:
        print(e) # log exception, but just move on
        raise(e)
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
