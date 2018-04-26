#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
"""Generate a model capable of detecting subject-verb agreement errors"""
print("loading libraries...")
import json
import numpy as np
import os
import psycopg2
import tensorflow as tf
from tflearn.data_utils import to_categorical
import tflearn

# Constants

DB_PASSWORD = os.environ.get('SVA_PASSWORD', '')
DB_NAME = os.environ.get('SVA_DB', 'max')
DB_USER = os.environ.get('SVA_USER', DB_NAME)
DB_PORT = int(os.environ.get('SVA_PORT', '5432'))
DB_HOST = 'localhost'


def inflate(deflated_vector):
    """Given a defalated vector, inflate it into a np array and return it"""
    dv = json.loads(deflated_vector)
    #result = np.zeros(dv['reductions']) # some claim vector length 5555, others
    #5530. this could have occurred doing remote computations? or something.
    # anyhow, we will use 5555.  Let's just hard code it.  Gosh darnit.
    result = np.zeros(5555) # some claim vector length 5555, others
    for n in dv['indices']:
        result[int(n)] = dv['indices'][n]
    #print("Inflated vector. Length", len(result))
    return result


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
if vector_len != 5555:
    vector_len = 5555
print("Vector length, ", vector_len)


# grab deflated vectors
cur.execute('SELECT vector, label FROM vectors') # less than 2 million

# #Iterate through deflated vectors
#
# NOTE: loads 2 million vectors and 2 million labels into memory. Numpy reduces
# the vector size, so each item in the array of vectors and the array of labels
# is small. I think this should work fine and fast on most of the machines we
# run at Quill.org.
word_vectors = np.zeros((records, vector_len), dtype=np.int_)
labels = []
ii = 0
for deflated_vector, label in cur: 
    word_vectors[ii] = inflate(deflated_vector)
    labels.append(label)
    ii+=1

# Chunk data for tensorflow ##############################################
print("Chunking data for tensorflow...")
test_fraction = 0.9

train_split, test_split = int(records*test_fraction), int(records*(1-test_fraction))
print("Train split", train_split)
print("Test split", test_split)
print("...")
trainX, trainY = word_vectors[:train_split], to_categorical(labels[:train_split], 2)
testX, testY = word_vectors[test_split:], to_categorical(labels[test_split:], 2)

# Building TF Model #######################################################

print("Setting up tensorflow...")

def build_model():
    # This resets all parameters and variables, leave this here
    tf.reset_default_graph()
    
    #### Your code ####
    net = tflearn.input_data([None, vector_len])                          # Input
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
print("Saving model...")
model.save("../../../models/subject_verb_agreement_model.tfl")

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
