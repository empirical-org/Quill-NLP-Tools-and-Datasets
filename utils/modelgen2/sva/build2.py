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
#hdf5_f = h5py.File("/Volumes/ryn/hdf5_files/kyrie_sva_model.hdf5", "w")

#######
# TODO: using resize could be faster if we compress - we'd just be appending to
# the end of a file instead of searching for an array in a compressed index

def inflate(deflated_vector):
    """Given a defalated vector, inflate it into a np array and return it"""
    dv = json.loads(deflated_vector)
    result = np.zeros(VEC_LEN)
    for n in dv['indices']:
        result[int(n)] = dv['indices'][n]
    return result



train_fraction = 0.9
train_split = int(records*train_fraction)
test_split = records - train_split

with h5py.File("/Volumes/ryn/hdf5_files/james_sva_model.hdf5", "w") as f:
    

    print("Created hdf5 file...")
    batch_size = 5000
    current_len = 0 
    for wv_name, labels_name, split_size in [('word_vectors_train',
        'labels_train', train_split), ('word_vectors_test', 'labels_test',
            test_split)]: 
        train_split = split_size
        d = f.create_dataset(wv_name, (batch_size,VEC_LEN ),
                maxshape=(train_split,VEC_LEN ), dtype=np.int_, compression='lzf')
        l = f.create_dataset(labels_name, (batch_size, ),
                maxshape=(train_split, ), dtype=np.int_, compression='lzf')
        then = time()
        i = 0
        while current_len < train_split: 
            if train_split - current_len > batch_size:
                defacto_batch_size = batch_size
            else:
                defacto_batch_size = train_split - current_len
            batch = np.zeros((defacto_batch_size, VEC_LEN), dtype=np.int_)
            label_batch = np.zeros((defacto_batch_size,), dtype=np.int_)
            for i_ in range(defacto_batch_size):
                deflated_vector, label = cur.fetchone()
                batch[i_] = inflate(deflated_vector)
                label_batch[i_] = label
            # batch is filled, write to hdf5 slab 
            d.resize((current_len+defacto_batch_size,VEC_LEN))
            l.resize((current_len+defacto_batch_size,))
            d[current_len:current_len + defacto_batch_size] = batch 
            l[current_len:current_len + defacto_batch_size] = label_batch
            current_len += defacto_batch_size
            print('Speed: {}s'.format(float(current_len) / (time() - then ) ) )
            i += 1



#######

print('done. 🎉')
