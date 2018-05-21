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
import tflearn


METHOD = 'ML_ONLY'
#METHOD = 'COMBINED' 
#METHOD = 'RULE_BASED' 

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
    result = np.zeros(93540) # some claim vector length 5555, others
    for n in dv['indices']:
        result[int(n)] = dv['indices'][n]
    #print("Inflated vector. Length", len(result))
    return result[:93540]

def text_to_vector(sent_str):
    """Given a string, get it's defalted vector, inflate it, then return the
    inflated vector"""
    r = requests.get("{}/sva/vector".format(VECTORIZE_API), params={'s':sent_str})
    return inflate(r.text)

# Building TF Model #######################################################

print("Setting up tensorflow...")
vector_len = 93540 # TODO: this probably really should not be hardcoded
def build_model():
    # This resets all parameters and variables, leave this here
    tf.reset_default_graph()
    
    #### Your code ####
    net = tflearn.input_data([None, 93540])                          # Input
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
model.load('../../../models/james_sva/james_subject_verb_agreement_model.tfl')

# Testing ##############################################################
print('Running tests against your model...')
# TODO: text_to_vector not currently included so tests can't run
def test_sentence(sentence, ans):
    """Returns true if correct"""
    correct = False


    # see number of verb phrases
    pattern = r'<VERB>?<ADV>*<VERB>+'
    doc = textacy.Doc(sentence, lang='en_core_web_lg')
    vps = textacy.extract.pos_regex_matches(doc, pattern)

    #if len([x for x in vps]) < 2:
    if (METHOD == 'COMBINED' and len([x for x in vps]) < 2) or METHOD == 'RULE_BASED':
        print("Simple sentence, using rule based checker")
        return ans != check_agreement(sentence)
    
    # Use ML on more complex sentences

    positive_prob = model.predict([text_to_vector(sentence)])[0][1]
    print('---{}---'.format(sentence))
    print('Does this sentence have a subject-verb agreement error?\n {}'.format(sentence))
    print('P(positive) = {:.3f} :'.format(positive_prob),
          'Yes' if positive_prob > 0.5 else 'No')
    correct = (positive_prob > 0.5) == ans
    print("Is correct?", correct)
    print('-------------------------------------------')
    return correct


while True:
    s = input('sent: ')
    print('Calculating...')
    positive_prob = model.predict([text_to_vector(s)])[0][1]
    print(positive_prob)
    if positive_prob > .6:
        print('Incorrect')
    else:
        print('Correct')

