#!/usr/bin/env python
# -*- coding: utf-8 -*-
from vectorizer_helper import get_vector
import os
import pika
import re


RABBIT = os.environ.get('RABBITMQ_LOCATION', 'localhost')

def handle_message(ch, method, properties, body):
    try:
        vector = get_vector(body)
        channel.basic_publish(exchange='', routing_key='vectors',
                body=vector)
    except Exception as e:
        print(e) # log exception, but just move on
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT))
    channel = connection.channel()
    channel.queue_declare(queue='strings') # create queue if doesn't exist
    channel.queue_declare(queue='reductions')

    # NOTE: if the prefetch count is too high, some workers could starve. If it
    # is too low, we make an unneccessary amount of requests to rabbitmq server 
    channel.basic_qos(prefetch_count=10) # limit num of unackd msgs on channel
    channel.basic_consume(handle_message, queue='strings', no_ack=False)
    channel.start_consuming()
