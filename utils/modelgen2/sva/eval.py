#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
"""Generate a model capable of detecting subject-verb agreement errors"""
print("loading libraries...")
import json
import numpy as np
import os
import requests
import tensorflow as tf
from tflearn.data_utils import to_categorical
from test_sents import sentences as ts
import tflearn

# Constants

VECTORIZE_API = os.environ.get('VECTORIZE_API_URI', 'http://localhost:10200')

# TODO: move this into a shared module -- it's shared accross build, eval, and
# others maybe.
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

def text_to_vector(sent_str):
    """Given a string, get it's defalted vector, inflate it, then return the
    inflated vector"""
    r = requests.get("{}/sva/vector".format(VECTORIZE_API), params={'s':sent_str})
    return inflate(r.text)

# Building TF Model #######################################################

print("Setting up tensorflow...")
vector_len = 5555 # TODO: this probably really should not be hardcoded
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

# Loading TF Model #####################################################
print("Loading TF model...")
model.load('../../../models/subject_verb_agreement_model.tfl')

# Testing ##############################################################
print('Running tests against your model...')
# TODO: text_to_vector not currently included so tests can't run
def test_sentence(sentence, ans):
    """Returns true if correct"""
    positive_prob = model.predict([text_to_vector(sentence)])[0][1]
    print('---{}---'.format(sentence))
    print('Does this sentence have a subject-verb agreement error?\n {}'.format(sentence))
    print('P(positive) = {:.3f} :'.format(positive_prob),
          'Yes' if positive_prob > 0.61 else 'No')
    correct = (positive_prob > 0.61) == ans
    print("Is correct?", correct)
    print('-------------------------------------------')
    return correct

total_sents = len(ts)
total_right = 0.0
overly_strict = 0.0
overly_lenient = 0.0
too_strict_sents = []
for sent, ans in ts:
    correct =  test_sentence(sent, ans)
    if correct:
        total_right += 1
    
    if not correct and not ans:
        # There is not an error but one was marked
        overly_strict += 1
        too_strict_sents.append(sent)
        pass
    if not correct and ans:
        # There is an error but none was marked
        overly_lenient += 1
        pass

print("Too strict sents: ")
print("\n")
for too_s in too_strict_sents:
    print(" > " + too_s)

print("Success rate was {}%".format(total_right/total_sents * 100))
print("\n")
print("Error rate {}%".format(100 - total_right/total_sents * 100))
print("Too strict {}%".format(overly_strict/total_sents * 100))
print("Too lenient {}%".format(overly_lenient/total_sents * 100))




print('done. 🎉')
