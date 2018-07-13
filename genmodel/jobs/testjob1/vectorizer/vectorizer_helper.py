#!/usr/bin/env python
# -*- coding: utf-8 -*-
from reducer_helper import get_reduction
from time import sleep
import json
import logging
import os
import pika
import psycopg2
import random
import re
import socket


FNAME=os.path.basename(__file__)
PID=os.getpid()
HOST=socket.gethostname()

# set up logging
log_filename='vectorizer_helper_{}.log'.format(os.getpid())
log_format = '%(levelname)s %(asctime)s {pid} {filename} %(lineno)d %(message)s'.format(
        pid=PID, filename=FNAME)
logging.basicConfig(format=log_format,
    filename='/var/log/vectorizerlogs/{}'.format(log_filename),
    datefmt='%Y-%m-%dT%H:%M:%S%z',
    level=logging.INFO)
logger = logging.getLogger('vectorizer_helper')

# Constants

DB_HOST = 'localhost'
DB_NAME = os.environ.get('DB_NAME', 'nlp')
DB_PASSWORD = os.environ.get('DB_PASS', '')
DB_PORT = int(os.environ.get('DB_PORT', 5432))
DB_USER = os.environ.get('DB_USER', DB_NAME)
JOB_ID = os.environ.get('JOB_ID')

# Connect to postgres
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        port=DB_PORT, host=DB_HOST)
cur = conn.cursor()

# Select unique reductions in order of regularity, must occur at least thrice 
cur.execute('''SELECT reduction,count(*) from reductions
            WHERE job_id=%s 
            GROUP BY reduction
            HAVING count(*) > 2
            ORDER BY count(*) desc, reduction;''',
            (JOB_ID,))


# with ~2 million total sentences the number of unique reductions was a little
# over 290k. ~94k had more than 2 occurrences
reduction2idx = {n[0]: i for i, n in enumerate(cur)} 
num_reductions = len(reduction2idx)

# close connections to database
# close connections to database
cur.close()
conn.close()

# vectors must be convertable to  a numpy array. 
# NOTE: storing the number of reductions on each object is not necessary and is
# increasing db size. The advantage is that each row can compute its numpy
# vector with no database calls which is why we choose it.  We might undecide
# this at some point.
# Ex:
# {indices={5:1, 6:2, 500:1, 6003:2} num_reductions=5000}
# {indicies={index:count, index:count, ...} reductions=num_reductions}
def get_vector(pre_vector):
    pre_vector_dict = json.loads(pre_vector)
    result = {'indices':{}, 'reductions':num_reductions}
    pre_reduction = json.dumps(pre_vector_dict['sent_str'])
    for reduction in get_reduction(pre_reduction):
        index = reduction2idx.get(reduction)
        if index != None:
            result['indices'][index] = result['indices'].get(index, 0) + 1
    return result

