#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Generate a model capable of detecting subject-verb agreement errors"""


# TODO: NOTE: DEPRECATED !!!! THIS FILE IS MARKED FOR REMOVAL

print("loading libraries...")
from collections import Counter
from pattern.en import lexeme, tenses
from pattern.en import pluralize, singularize
from textstat.textstat import textstat
from tflearn.data_utils import to_categorical
import hashlib
import numpy as np
import random
import re
import spacy
import sqlite3
import tensorflow as tf
import textacy
import tflearn

print("loading spacy...")


nlp = spacy.load('en_core_web_lg')
conn = sqlite3.connect('db/mangled_agreement.db')
#cursor = conn.cursor()

# Load the Datafiles ########################################################
print("Loading datafiles...")
# TODO: This is kind of memory intensive don'tcha think?
#texts = []
#labels = []

def get_correct_or_mangled_sentence():
    """Generator function that randomly yields a correct or mangled sentences
    and its label, where 0 is correct and 1 is mangled. If no results are
    available, yields None."""
    mangled_cursor = conn.cursor()
    correct_cursor = conn.cursor()
    mangled_cursor.execute("SELECT sentence FROM mangled_sentences ORDER BY "
            "RANDOM() LIMIT 799675")
    correct_cursor.execute("SELECT sentence FROM orignal_sentences")

    # just a start value that will be changed
    result = True 
    while result:
        mangled = random.choice([True, False])
        if mangled:
            result = mangled_cursor.fetchone()[0]
            if result:
                result = (result, 1)
        if not mangled or not result:
            result = correct_cursor.fetchone()[0]
            if result:
                result = (result, 0)
        if not mangled and not result:
            result = mangled_cursor.fetchone()[0]
            if result:
                result = (result, 1)
        yield result
    


# NOTE: now using a generator, no need to make an array of text and an array of
# labels now
#
# add 0 label to correct sentences
#for row in cursor.execute("SELECT sentence FROM orignal_sentences"):
#    texts.append(row[0].strip())
#    labels.append(0)
#
## add 1 label to sentences with a subject verb agreement error, limit should match the number of original sentences
#for row in cursor.execute("SELECT sentence FROM mangled_sentences ORDER BY RANDOM() LIMIT 799675"):
#    texts.append(row[0].strip())
#    labels.append(1)
#        
#print(texts[-10:])
#assert type(texts[0]) == str 
#conn.close() # done with sqlite connection

# Shuffle The Data ##########################################################
# NOTE: using our generator there is no need to shuffle anymore

#print("Shuffling the data")
#combined = list(zip(texts,labels))
#random.shuffle(combined)
#
#texts[:], labels[:] = zip(*combined)
#print(texts[-10:])
#assert type(texts) == list
#assert type(texts[0]) == str
#assert type(labels) == list
#assert type(labels[0]) == int
#print(labels[-10:])


# Get Verb Phrase Keys for Sentence ##########################################

def get_verb_phrases(sentence_doc):
    """
    Returns an object like,
    
        [(1), (5,6,7)]
        
    where this means 2 verb phrases. a single verb at index 1, another verb phrase 5,6,7.  
    
     - Adverbs are not included.
     - Infinitive phrases (and verb phrases that are subsets of infinitive phrases) are not included
     
    """ 
    pattern =  r'<VERB>*<ADV>*<VERB>+' #  r'<VERB>?<ADV>*<VERB>+' is suggested by textacy site
    verb_phrases = textacy.extract.pos_regex_matches(sentence_doc, pattern)
    #sentence_str = sentence_doc.text
    
    #index_2_word_no = {} # the starting position for each word to its number{0:0, 3:1, 7:2, 12:3}
    #for word in sentence_doc:
    #    index_2_word_no[word.idx] = word.i

    #print(index_2_word_no)
        
    result = [] # [(1), (5,6,7)] => 2 verb phrases. a single verb at index 1, another verb phrase 5,6,7
    for vp in verb_phrases:
        word_numbers = []
        # return the index of 'could have been happily eating' from 'She could have been happily eating chowder'
        first_word = vp.start

        x = first_word
        if len(vp) > 1:
            for verb_or_adverb in vp:
                # filter out adverbs
                if not verb_or_adverb.pos_ == 'ADV':
                    word_numbers.append(x)
                x += 1
        else:
            word_numbers.append(first_word)
        
        # filter out infinitive phrases
        if ( (word_numbers[0] - 1) < 0) or (sentence_doc[word_numbers[0] - 1].text.lower() != 'to'):
            result.append(word_numbers)
    
    return result


def singular_or_plural(word_string):
    if word_string == singularize(word_string):
        return 'SG'
    else:
        return 'PL'

def sentence_to_keys(sentence):
    doc = textacy.Doc(sentence, lang='en_core_web_lg')
    
    # [(1), (5,6,7)] => 2 verb phrases. a single verb at index 1, another verb phrase 5,6,7
    verb_phrases = get_verb_phrases(doc)
    
    # doc = this could be my sentence
    # doc_list = [this, -595002753822348241, 15488046584>THIS, my sentence]
    # final_keys = [-595002753822348241:15488046584>THIS]
    #
    # doc = Jane is only here for tonight
    # doc_list = [Jane, 13440080745121162>SG, only, here, for, tonight ]
    # final_keys = [13440080745121162>SG]
    doc_list = []
    for word in doc:
            
        if word.pos_ == 'VERB':
            tense_hash = hashlib.sha256((str(tenses(word.text)))).hexdigest()
            verb_number_or_pronoun = ''
            for child in word.children:
                if child.dep_ == 'nsubj':
                    if child.pos == 'PRON':
                        verb_number_or_pronoun = child.text.upper()
                    else:
                        verb_number_or_pronoun = singular_or_plural(child.text)
                    break
        
            doc_list.append(tense_hash + '>' + verb_number_or_pronoun)
        else:
            doc_list.append(word.text)
    
    # Get final keys
    final_keys = []
    for vp in verb_phrases:
        vp_key_list = []
        for word_no in vp:
            vp_key_list.append(doc_list[word_no])
        vp_key = ':'.join(vp_key_list)
        final_keys.append(vp_key)
    
    return final_keys
    
assert (sentence_to_keys(u"Jane is only here for tonight.") ==
        [hashlib.sha256((str(tenses("is")))).hexdigest() + '>' + 'SG']) 



# Perform key counts ########################################################
print("Performing key counts")

c = Counter()

# NOTE: now pulling texts from the generator instead
#for textString in texts:
#    c.update(sentence_to_keys(textString))


for textString, _ in get_correct_or_mangled_sentence():
    # NOTE: this COULD be memory intensive.  Since we expect (and hope) that the
    # keys will repeat pretty often, even with large number of correct and
    # mangled sentences our counter should be keeping track of a smaller number
    # of those keys.  If keys rarely repeat, we could be in trouble. 
    # 
    # Right now, a warning is printed if the number of keys is over a million;
    # we can adjust this number as we go to make it sensible.
    #print(textString)
    
    c.update(sentence_to_keys(textString))

total_counts = c

print("Total keys in data set: ", len(total_counts))
print("Most common keys: ")
for k, ct in c.most_common(10):
    print("{}:{}".format(k, ct))
if len(total_counts) > 1000000:
    print("WARNING: there are over a million keys being tracked. This could be"
            "memory intensive and not productive.")

vocab = sorted(total_counts, key=total_counts.get, reverse=True)
assert type(vocab) == list

# Indexing the sentence keys ################################################
print("Indexing sentence keys...")
 
word2idx = {n: i for i, n in enumerate(vocab)}

def text_to_vector(text):
    wordVector = np.zeros(len(vocab))
    for word in sentence_to_keys(text):
        index = word2idx.get(word, None)
        if index != None:
            wordVector[index] += 1
    return wordVector


# Build word vectors #####################################################
print("Building word vectors...")
#records = len(labels) # NOTE: instead get the counts from the database
records = [x for x in mangled_cursor.execute("SELECT count(*) FROM mangled_sentences LIMIT"
        " 799675")][0][0]
records += [x for x in correct_cursor.execute("SELECT count(*) FROM "
    "orignal_sentences")][0][0]
assert type(records) == int

# NOTE: use number of databse records instead of len of texts list 
#word_vectors = np.zeros((len(texts), len(vocab)), dtype=np.int_)
#for ii, text in enumerate(texts):
#    word_vectors[ii] = text_to_vector(text)


# Vectorize sentences ####################################################
print('Vectorizing sentences...')

# NOTE: this part is obviously still memory intensive, but at least its not
# quite as bad as storting strings.
word_vectors = np.zeros((records, len(vocab)), dtype=np.int_)
labels = []
ii = 0
for text, label in get_correct_or_mangled_sentence():
    word_vectors[ii] = text_to_vector(text)
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


# Set up TensorFlow #######################################################
# Building TF Model #######################################################

print("Setting up tensorflow...")

def build_model():
    # This resets all parameters and variables, leave this here
    tf.reset_default_graph()
    
    #### Your code ####
    net = tflearn.input_data([None, len(vocab)])                          # Input
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

# Write CSV index file ##################################################
print("Writing CSV index file...")
w = csv.writer(open("../models/subjectverbagreementindex.csv", "w"))
for key, val in word2idx.items():
    w.writerow([key, val])

# Save model ############################################################
print("Saving model...")
model.save("../../models/subject_verb_agreement_model.tfl")

print('\n'*10)
print('-----')
print('Success! Your model was built and saved.')
print('\n'*10)





# Testing ##############################################################
print('Running tests against your model...')

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


print('done.')
