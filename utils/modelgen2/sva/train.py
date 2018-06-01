#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
"""Generate a model capable of detecting subject-verb agreement errors"""
print("loading libraries...")
import json
import numpy as np
import os
import gc
import psycopg2
import tensorflow as tf
from tflearn.data_utils import to_categorical
import tflearn
from time import time

# Constants

DB_PASSWORD = os.environ.get('SVA_PASSWORD', '')
DB_NAME = os.environ.get('SVA_DB', 'max')
DB_USER = os.environ.get('SVA_USER', DB_NAME)
DB_PORT = int(os.environ.get('SVA_PORT', '5432'))
DB_HOST = 'localhost'
VEC_LEN = 93540 

# New stuff 
# connect to database
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        port=DB_PORT, host=DB_HOST)
cur = conn.cursor()

# get records count
cur.execute('SELECT count(*) FROM vectors')
records = cur.fetchone()[0]
print("Records count, ", records)

# get vector length
cur.execute('SELECT vector FROM vectors LIMIT 1')
vector_len = json.loads(cur.fetchone()[0])['reductions']
if vector_len != VEC_LEN:
    raise Exception('WRONG VECTOR LENGTH!')
    vector_len = VEC_LEN 
print("Vector length, ", vector_len)


def inflate(deflated_vector):
    """Given a defalated vector, inflate it into a np array and return it"""
    dv = json.loads(deflated_vector)
    result = np.zeros(VEC_LEN) # some claim vector length 5555, others
    for n in dv['indices']:
        result[int(n)] = dv['indices'][n]
    return result


def get_word_vectors(offset, limit):
    cur.execute('SELECT vector,label FROM vectors OFFSET %s LIMIT %s',
            (offset, limit))
    return [(v,l) for v,l in cur]

# Building TF Model #######################################################


def build_model():
    # This resets all parameters and variables, leave this here
    tf.reset_default_graph() # num cpu cores is all by default
    
    #### Your code ####
    net = tflearn.input_data([None, VEC_LEN])                          # Input
    net = tflearn.fully_connected(net, 200, activation='ReLU')      # Hidden
    net = tflearn.fully_connected(net, 25, activation='ReLU')      # Hidden
    net = tflearn.fully_connected(net, 2, activation='softmax')   # Output
    net = tflearn.regression(net, optimizer='sgd', learning_rate=0.1, loss='categorical_crossentropy')
    model = tflearn.DNN(net)

    return model


print("Setting up tensorflow...")
print("Building TF model...")
model = build_model()

# Train TF Model ########################################################
print("Training TF model...")

train_len = records 
start_pos = 0
slab_size = 5000 # large slab minimizes time finding the slab
end_pos = start_pos + slab_size
while start_pos < train_len:
    end_pos = start_pos + slab_size
    if end_pos > train_len:
        end_pos = train_len 
    # start_pos, 0
    # end_pos, 5000
    vec_and_labs = get_word_vectors(start_pos, slab_size)
    print('Fitting model with start: {}, end: {}'.format(start_pos, end_pos))
    assert len(vec_and_labs) == slab_size
    model.fit(np.asarray([inflate(vec) for vec,lab in vec_and_labs]),
            to_categorical(np.asarray([lab for vec,lab in vec_and_labs]), 2),
            validation_set=0.1, show_metric=True, batch_size=128, n_epoch=50)
    del vec_and_labs
    gc.collect() # force Garbage Collector to release unreferenced memory  

    start_pos = end_pos
    if end_pos % 100000 == 0: # save a copy of the model every 90k times
        print('Saving model in current state... still training.')
        model.save("../../../models/thompson_subject_verb_agreement_model.tfl")


print("Saving model...(final save)")
model.save("../../../models/thompson_subject_verb_agreement_model.tfl")


print('\n'*10)
print('-----')
print('Success! Your model was built and saved.')
print('\n'*10)


print('done. 🎉')
