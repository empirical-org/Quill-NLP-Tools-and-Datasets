#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pattern.en import lexeme, tenses
from utils import read_in_chunks
import spacy
import sqlite3
import argparse
import os
import re
from textstat.textstat import textstat
conn = sqlite3.connect('db/mangled_agreement.db')
cursor = conn.cursor()
nlp = spacy.load('en')


# Private methods

def _verbs_with_subjects(doc):
    """Given a spacy document return the verbs that have subjects"""
    # TODO: UNUSED
    verb_subj = []
    for possible_subject in doc:
        if (possible_subject.dep_ == 'nsubj' and possible_subject.head.pos_ ==
                'VERB'):
            verb_subj.append([possible_subject.head, possible_subject])
    return verb_subj


def _mangle_sentences_from_directory(inputdir):
    for f in os.listdir(inputdir):
        #input_filename = os.path.join(inputdir, os.fsdecode(f))
        input_filename = os.path.join(inputdir, f)
        _mangle_sentences_from_file(input_filename)


def _mangle_sentences_from_file(input_file):
    """Write participle phrase file"""
    try:
        with open(input_file, 'r') as f:
            # final sentence may not be a complete sentence, save and prepend to next chunk
            leftovers = ''
            sentence_no = 0
            for chunk in read_in_chunks(f): # lazy way of reading our file in case it's large
                # prepend leftovers to chunk
                chunk = chunk.decode('utf8')
                chunk = leftovers + chunk
                chunk = chunk.replace(';', '.') # replace semi colons with periods 
                doc = nlp(chunk)

                # last sentence may not be sentence, move to next chunk
                sents = [sent.string.strip() for sent in doc.sents]
                if len(sents) > 1:
                    leftovers = sents[-1] + chunk.rpartition(sents[-1])[-1]
                    sents = sents[:-1]

                for sent in sents:
                    sent = sent.replace('\n', ' ')
                    sent = sent.replace('\r', ' ')
                    sent = re.sub( '\s+', ' ', sent ).strip()
                    if len(sent) < 5:
                        continue # skip tiny sentences
                    # add original sentence to database
                    cursor.execute('''insert into orignal_sentences (sentence,
                    flesch_reading_ease, flesch_kincaid_grade_level) values (?,
                    ?, ?)''', (sent, textstat.flesch_reading_ease(sent),
                        textstat.flesch_kincaid_grade(sent)))
                    og_sent_id = cursor.lastrowid
                    for mangled_sentence in mangle_agreement(sent):
                        # add mangled sentence to database
                        cursor.execute('''insert into mangled_sentences
                        (original_sentence_id, sentence) values (?, ?)''',
                        (og_sent_id, mangled_sentence))
                conn.commit() # commit all sentences in this chunk

    except Exception as e:
        print('error on {}'.format(input_file))
        print(e)


# Public methods

def mangle_agreement(correct_sentence):
    """Given a correct sentence, return a sentence or sentences with a subject
    verb agreement error"""
    # # Examples
    #
    # Back in the 1800s, people were much shorter and much stronger.
    # This sentence begins with the introductory phrase, 'back in the 1800s'
    # which means that it should have the past tense verb. Any other verb would
    # be incorrect. 
    #
    #
    # Jack and jill went up the hill. 
    # This sentence is different; 'go' would also be correct. If it began with
    # 'Yesterday', a single-word introductory phrase requiring no comma, only
    # 'went' would be acceptable.
    #
    #  
    # The man in the checkered shirt danced his warrior dance to show that
    # he was the most dominant male in the room.
    # This sentence has multiple verbs. If the sentence ended at the word dance,
    # changing 'danced' to 'dances' would be acceptable, but since the sentence
    # continues we cannot make this change -- 'was' agrees with 'danced' but not
    # with 'dances'.  This is a shifty tense error, a classic subject verb
    # agreement error.
    # 
    # # Our Method
    # 
    # Right now, we will assume that any change in verb form of a single verb in
    # a sentence is incorrect.  As demonstrated above, this is not always true.
    # We hope that since any model created off of this data will use a
    # confidence interval to determine likelihood of a subject-verb agreement
    # error, that some number can be found for which the model excels.
    # 
    # It would also be possible to use a rule based learner to evaluate single
    # verb sentences, and only evaluating more complex sentences with the
    # tensorflow model.

    bad_sents = []
    doc = nlp(correct_sentence)
    verbs = [(i, v) for (i, v) in enumerate(doc) if v.tag_.startswith('VB')]
    for i, v in verbs:
        for alt_verb in lexeme(doc[i].text):
            if alt_verb == doc[i].text:
                continue # Same as the original, skip it
            if (tenses(alt_verb) == tenses(v.text) or
                    (alt_verb.startswith(v.text) and alt_verb.endswith("n't"))):
                continue # Negated version of the original, skip it
            new_sent = str(doc[:i]) + " {} ".format(alt_verb) + str(doc[i+1:]) 
            new_sent = new_sent.replace(' ,', ',') # fix space before comma
            bad_sents.append(new_sent)
    return bad_sents


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create sentences with mangled'
            'subject verb agreement from text files of correct sentences' 
    )
    parser.add_argument('-i', '--inputfile', help='Extract participle phrases '
            'from here.')
    parser.add_argument('-I', '--inputdir', help='Extract participle phrases '
            'from files in this input directory.')
    args = parser.parse_args()

    if args.inputdir:
        _mangle_sentences_from_directory(args.inputdir) 
    elif args.inputfile:
        _mangle_sentences_from_file(args.inputfile)

