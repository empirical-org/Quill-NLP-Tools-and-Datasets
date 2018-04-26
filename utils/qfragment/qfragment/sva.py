#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
"""Generate a model capable of detecting subject-verb agreement errors"""
print("loading libraries...")
import json
import numpy as np
import os
import requests
import textacy
import tensorflow as tf
from tflearn.data_utils import to_categorical
import tflearn
from .sva_rule_based import check_agreement

METHOD = 'COMBINED' 
VECTORIZE_API = os.environ.get('VECTORIZE_API_URI', 'http://localhost:10200')

# Constants


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
model.load('./models/subject_verb_agreement_model.tfl')

def check_agreement2(sentence):
    """Returns False when subject and verb disagree (or probably disagree)"""
    correct = False
    METHOD = 'COMBINED'

    # see number of verb phrases
    pattern = r'<VERB>?<ADV>*<VERB>+'
    doc = textacy.Doc(sentence, lang='en_core_web_lg')
    vps = textacy.extract.pos_regex_matches(doc, pattern)

    #if len([x for x in vps]) < 2:
    if (METHOD == 'COMBINED' and len([x for x in vps]) < 2) or METHOD == 'RULE_BASED':
        print("Simple sentence, using rule based checker")
        return check_agreement(sentence)
    
    # Use ML on more complex sentences
    positive_prob = model.predict([text_to_vector(sentence)])[0][1]
    return positive_prob <= 0.61 
