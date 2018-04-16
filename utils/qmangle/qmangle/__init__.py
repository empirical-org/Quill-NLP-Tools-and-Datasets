#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pattern.en import conjugate, lexeme, lemma, tenses
import spacy
nlp = spacy.load('en')

#from spacy.symbols import nsubj, VERB
#
## Finding a verb with a subject from below — good
#verbs = set()
#for possible_subject in doc:
#    if possible_subject.dep == nsubj and possible_subject.head.pos == VERB:
#        verbs.add(possible_subject.head)

def verbs_with_subjects(doc):
    """Given a spacy document return the verbs that have subjects"""
    verb_subj = []
    for possible_subject in doc:
        if (possible_subject.dep_ == 'nsubj' and possible_subject.head.pos_ ==
                'VERB'):
            verb_subj.append([possible_subject.head, possible_subject])
    return verb_subj


def mangle_agreement(correct_sentence):
    """Given a correct sentence, return a sentence with a subject verb agreement
    error"""
    bad_sents = []
    good_sents = []
    doc = nlp(correct_sentence)
    verbs_with_subjects = verbs_with_subjects(doc)
    verbs = [(i, v) for (i, v) in enumerate(doc) if v.tag_.startswith('VB')]
    for i, v in verbs:
        for alt_verb in lexeme(doc[i].text):
            if alt_verb == doc[i].text:
                continue
            new_sent = str(doc[:i]) + " {} ".format(alt_verb) + str(doc[i+1:]) 
            #print(new_sent)
        #print(doc[i])
    
    return correct_sentence

    

if __name__ == '__main__':
    sentences = [
        u"Jack and jill went up the hill",
        u"She was amazing",
        u"Back in the 1800s, people were much shorter and much stronger.",
        u"""The man in the checkered shirt danced his warrior dance to show that
         he was the most dominant male in the room, a dining room as it were,
         with a picture window and a view of the sea.""",
        u"Until the end of time, he would love that little red car."
    ]

    for s in sentences:
        mangle_agreement(s)


















