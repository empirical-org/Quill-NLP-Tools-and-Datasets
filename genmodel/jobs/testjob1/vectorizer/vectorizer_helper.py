#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import sleep
import os
import pika
import psycopg2
import random
import re

# Constants

DB_HOST = 'localhost'
DB_NAME = os.environ.get('DB_NAME', 'nlp')
DB_PASSWORD = os.environ.get('DB_PASS', '')
DB_PORT = int(os.environ.get('DB_PORT', 5432))
DB_USER = os.environ.get('DB_USER', DB_NAME)
JOB_ID = os.environ.get('JOB_ID')

print('Connecting to the database... ')

# Connect to postgres
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        port=DB_PORT, host=DB_HOST)
cur = conn.cursor()


# Select unique reductions in order of regularity, must occur at least thrice 
cur.execute('''SELECT reduction,job_id,count(*) from reductions
            WHERE job_id=? 
            GROUP BY reduction
            HAVING count(*) > 2
            ORDER BY count(*) desc, reduction;''',
            (JOB_ID))


# with ~2 million total sentences the number of unique reductions was a little
# over 290k. ~94k had more than 2 occurrences
reduction2idx = {n[0]: i for i, n in enumerate(cur)} 
num_reductions = len(reduction2idx)

# close connections to database
# close connections to database
cur.close()
conn.close()

# Vectorizing sentence keys ################################################
print('Vectorizing sentence keys...')


# vectors must be convertable to  a numpy array. 
# NOTE: storing the number of reductions on each object is not necessary and is
# increasing db size. The advantage is that each row can compute its numpy
# vector with no database calls which is why we choose it.  We might undecide
# this at some point.
# Ex:
# {indices={5:1, 6:2, 500:1, 6003:2} num_reductions=5000}
# {indicies={index:count, index:count, ...} reductions=num_reductions}
def get_vector(string):
    result = {'indices':{}, 'reductions':num_reductions}
    for reduction in get_reduction(string):
        index = reduction2idx.get(reduction)
        if index:
            result['indices'][index] = result['indices'].get(index, 0) + 1
    return result

