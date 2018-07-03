#!/usr/bin/env python
# -*- coding: utf-8 -*-
from vectorizer_helper import get_vector
import json
import os
import pika
import re

try:
    JOB_NAME = os.environ['JOB_NAME']
    PRE_VECTORS_BASE = os.environ['PRE_VECTORS_QUEUE_BASE']
    PRE_VECTORS_QUEUE = PRE_VECTORS_BASE + '_' + JOB_NAME
    RABBIT = os.environ.get('RABBITMQ_LOCATION', 'localhost')
    VECTORIZER_PREFETCH_COUNT = int(os.environ.get('VECTORIZER_PREFETCH_COUNT', 10))
    VECTORS_BASE = os.environ['VECTORS_QUEUE_BASE']
    VECTORS_QUEUE = VECTORS_BASE + '_' + JOB_NAME
except KeyError as e:
    raise Exception('Warning: Important environment variables were not set')



def handle_message(ch, method, properties, body):
    try:
        vector = get_vector(body)
        channel.basic_publish(exchange='', routing_key=VECTORS_QUEUE,
                body=json.dumps(vector))
    except Exception as e:
        print(e) # log exception, but just move on
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
