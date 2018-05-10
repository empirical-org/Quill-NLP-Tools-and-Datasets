#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Generate a model capable of detecting subject-verb agreement errors"""
from pattern.en import lexeme, tenses
from pattern.en import pluralize, singularize
from textstat.textstat import textstat
import hashlib
import os
import re
import pika
import sqlite3
import textacy
from sva_reducer import sentence_to_keys
RABBIT = os.environ.get('RABBITMQ_LOCATION', 'localhost')


def get_reduction(sent_str):
    return sentence_to_keys(sent_str)


def handle_message(ch, method, properties, body):
    sent_str = body.decode("utf-8") 
    for reduction in get_reduction(sent_str):
        channel.basic_publish(exchange='', routing_key='reductions',
                body=reduction)
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
