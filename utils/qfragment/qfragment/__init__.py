import numpy as np
import tensorflow as tf
import tflearn
import spacy
nlp = spacy.load('en')
import re
from nltk.util import ngrams, trigrams
import csv
from .feedback import *

#_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
#_PARTICIPLE_TRIGRAM_INDEX = os.path.join(_DIRECTORY, 'participlevocabindex.csv')
#_PARTICIPLE_MODEL = os.path.join(_DIRECTORY, 'models/participle_model.tft')
_PARTICIPLE_MODEL = 'qfragment/models/participle_model.tfl'
_PARTICIPLE_TRIGRAM_INDEX = 'qfragment/participlevocabindex.csv'

class Feedback(object):
    """Result feedback class"""
    def __init__(self):
        self.human_readable = '' # human readable advice
        self.matches = {}        # possible errors

    def to_dict(self):
        return self.__dict__
    
    def __repr__(self):
        return self.human_readable

# Private methods

def _build_trigram_indices():
    """Build a dictionary of trigrams and their indices from a csv"""
    result = {}
    trigram_count = 0
    for key, val in csv.reader(open(_PARTICIPLE_TRIGRAM_INDEX)):
        result[key] = int(val)
        trigram_count += 1
    return result, trigram_count

def _build_model(trigram_count):
    # This resets all parameters and variables, leave this here
    tf.reset_default_graph()
    
    net = tflearn.input_data([None, trigram_count])
    net = tflearn.fully_connected(net, 200, activation='ReLU')      # Hidden
    net = tflearn.fully_connected(net, 25, activation='ReLU')      # Hidden
    net = tflearn.fully_connected(net, 2, activation='softmax')   # Output
    net = tflearn.regression(net, optimizer='sgd', learning_rate=0.1, loss='categorical_crossentropy')
    model = tflearn.DNN(net)
    return model

def _textStringToPOSArray(text):
    doc = nlp(text)
    tags = []
    for word in doc:
        tags.append(word.tag_)
    return tags

def _find_ngrams(input_list, n):
    """TODO: this method appears unused. Deprecate it?"""
    return zip(*[input_list[i:] for i in range(n)])

def _getPOSTrigramsForTextString(text):
    tags = _textStringToPOSArray(text)
    tgrams = list(trigrams(tags))
    return tgrams

def _trigramsToDictKeys(trigrams):
    keys = []
    for trigram in trigrams:
        keys.append('>'.join(trigram))
    return keys

def _textToTrigrams(text): 
    return _trigramsToDictKeys(_getPOSTrigramsForTextString(text))

def _text_to_vector(text, trigram_count):
    wordVector = np.zeros(trigram_count)
    for word in _textToTrigrams(text):
        index = word2idx.get(word, None)
        if index != None:
            wordVector[index] += 1
    return wordVector

# Public methods

## initializations
word2idx, trigram_count = _build_trigram_indices()
model = _build_model(trigram_count)
model.load(_PARTICIPLE_MODEL)


def check(sentence):
    """Supply a sentence or fragment and recieve feedback"""
    positive_prob = model.predict([_text_to_vector(sentence, trigram_count)])[0][1]
    result = Feedback()
    if float(positive_prob) < .5:
        result.human_readable = PARTICIPLE_FRAGMENT_ADVICE.replace('\n', '')
        result.matches['participle_phrase'] = float(positive_prob)
    else:
        result.human_readable = STRONG_SENTENCE_ADVICE.replace('\n', '')

    return result 


