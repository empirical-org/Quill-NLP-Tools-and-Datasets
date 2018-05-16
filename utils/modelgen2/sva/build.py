#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
"""Generate a model capable of detecting subject-verb agreement errors"""
print("loading libraries...")
import json
import h5py
import numpy as np
import os
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
# again, this should be 5555 in our case, but some of them have 5530. If it's
# not 5555 lets change it. ug, bad code.
if vector_len != VEC_LEN:
    vector_len = VEC_LEN 
print("Vector length, ", vector_len)

# grab deflated vectors
cur.execute('SELECT vector, label FROM vectors') # less than 2 million
print('Executed vector, label select...')
hdf5_f = h5py.File("/Volumes/ryn/hdf5_files/kyrie_sva_model.hdf5", "w")
print("Created hdf5 file...")
train_fraction = 0.9
train_split = int(records*train_fraction)
test_split = records - train_split
#word_vectors_train = hdf5_f.create_dataset("word_vectors_train", (train_split, VEC_LEN),
#        dtype=np.int_, compression="lzf")
#word_vectors_test = hdf5_f.create_dataset("word_vectors_test", (test_split, VEC_LEN),
#        dtype=np.int_, compression="lzf")
word_vectors_train = hdf5_f.create_dataset("word_vectors_train", (train_split, VEC_LEN),
        dtype=np.int_)
word_vectors_test = hdf5_f.create_dataset("word_vectors_test", (test_split, VEC_LEN),
        dtype=np.int_)
print("Created h5py word vectors...")
labels_train = hdf5_f.create_dataset("labels_train", (records,), dtype=np.int_,
        compression="lzf")
labels_test = hdf5_f.create_dataset("labels_test", (records,), dtype=np.int_,
        compression="lzf")
print("Created h5py labels...")
ii = 0
then = time()
for deflated_vector, label in cur: 
    dv = json.loads(deflated_vector)
    if ii >= train_split: # test
        wvtest_index_clone = word_vectors_test[ii - train_split]
        for n in dv['indices']:
            wvtest_index_clone[int(n)] = dv['indices'][n]
        word_vectors_test[ii - train_split] = wvtest_index_clone 
        labels_test_clone = labels_test
        labels_test_clone[ii - train_split] = label
        labels_test = labels_test_clone
    else: # train
        wvtrain_index_clone = word_vectors_train[ii]
        for n in dv['indices']:
            wvtrain_index_clone[int(n)] = dv['indices'][n]
        word_vectors_train[ii] = wvtrain_index_clone 
        labels_train_clone = labels_train
        labels_train_clone[ii] = label
        labels_train = labels_train_clone
    if ii % 1000 == 0:
        print('iteration: ', ii+1)
        total_time = time() - then  
        records_ps = float(ii) / total_time  
        print('{}s for {} records...'.format(total_time, ii))
        print('{} per second'.format(records_ps))
    ii+=1
total_time = time() - then
hdf5_f.close()
print('Total time for vector updates', total_time)

print('done. 🎉')
