#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
"""Generate a model capable of detecting subject-verb agreement errors"""
print("loading libraries...")
import json
import h5py import numpy as np
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

train_fraction = 0.9
train_split = int(records*train_fraction)
test_split = records - train_split

hdf5_f = h5py.File('/Volumes/ryn/hdf5_files/james_sva_model.hdf5', 'r') 
print("Opened hdf5 file...")
word_vectors_train = f['word_vectors_train']
word_vectors_test = f['word_vectors_train']
print("Opened h5py word vectors...")
labels_train = f['labels_train']
labels_test = f['labels_test']
print("opened h5py labels...")


print("Chunking data for tensorflow...")

print("Splitting train x, train y...")
# This method is memory intensive, doesn't actually work on huge datasets
#trainX, trainY = word_vectors[:train_split], to_categorical(labels[:train_split], 2)
trainX, trainY = word_vectors_train, to_categorical(labels_train, 2)
print("Splitting test x, test y...")
# This method is memory intensive, doesn't actually work on huge datasets
#testX, testY = word_vectors[test_split:], to_categorical(labels[test_split:], 2)
testX, testY = word_vectors_test, to_categorical(labels_test, 2)


# Building TF Model #######################################################

print("Setting up tensorflow...")

def build_model():
    # This resets all parameters and variables, leave this here
    tf.reset_default_graph()
    
    #### Your code ####
    net = tflearn.input_data([None, VEC_LEN])                          # Input
    net = tflearn.fully_connected(net, 200, activation='ReLU')      # Hidden
    net = tflearn.fully_connected(net, 25, activation='ReLU')      # Hidden
    net = tflearn.fully_connected(net, 2, activation='softmax')   # Output
    net = tflearn.regression(net, optimizer='sgd', learning_rate=0.1, loss='categorical_crossentropy')
    model = tflearn.DNN(net)

    return model

print("Building TF model...")
model = build_model()

# Train TF Model ########################################################
print("Training TF model...")
model.fit(trainX, trainY, validation_set=0.1, show_metric=True, batch_size=128, n_epoch=50)


print("Saving model...")
model.save("../../../models/maya_subject_verb_agreement_model.tfl")

## predictions, testing
predictions = (np.array(model.predict(testX))[:,0] >= 0.5).astype(np.int_)
test_accuracy = np.mean(predictions == testY[:,0], axis=0)
print("Test accuracy: ", test_accuracy)


# NOTE: removed writing to csv when building the model since the database
# already has this information
# Write CSV index file ##################################################
#print("Writing CSV index file...")
#w = csv.writer(open("../models/subjectverbagreementindex.csv", "w"))
#for key, val in word2idx.items():
#    w.writerow([key, val])

# Save model ############################################################
#print("Saving model...")
#model.save("../../../models/subject_verb_agreement_model2.tfl")

print('\n'*10)
print('-----')
print('Success! Your model was built and saved.')
print('\n'*10)


# Testing ##############################################################
print('Running tests against your model...')
# TODO: text_to_vector not currently included so tests can't run
def test_sentence(sentence, ans):
    positive_prob = model.predict([text_to_vector(sentence)])[0][1]
    print('---{}---'.format(sentence))
    print('Does this sentence have a subject-verb agreement error?\n {}'.format(sentence))
    print('P(positive) = {:.3f} :'.format(positive_prob),
          'Yes' if positive_prob > 0.5 else 'No')
    print("Is correct?", positive_prob > 0.5 == ans)
    print('-------------------------------------------')

test_sentence("Katherine was a silly girl.", False)
test_sentence("Katherine be a silly girl.", True)
test_sentence("Katherine, who was only twelve, already considered herself to be"
        " a silly girl.", False)
test_sentence("Katherine, who be only twelve, already considered herself to be"
        " a silly girl.", True)
test_sentence("Katherine, who was only twelve, already consider herself to be"
        " a silly girl.", True)
test_sentence("Katherine, who was only twelve, already considering herself to be"
        " a silly girl.", True)


print('done. 🎉')
