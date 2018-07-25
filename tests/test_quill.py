"""How well does Quill do at correctly identifying sentences and fragments?
Supply a file of the fomat,

This is my sentence.
My fragment.
This is also my sentence.
Ur fragments.

"""

import requests
import time

INPUT_FILE = 'participlePhraseSentencesAndTheirFragments.txt'
INPUT_FILE = 'fragmentDetectorTest.txt'
#INPUT_FILE = 'sciFiParticiplePhraseSentencesAndTheirFragments.txt'


with open(INPUT_FILE, 'r') as input_file:
    numcorrect = 0
    false_positives = 0 # we think it's a sentence
    false_negative = 0 # we think it's a fragment
    total = 0
    for i, line in enumerate(input_file):
        payload = {'text':line}
        #time.sleep(.1)
        r = \
                requests.post('http://localhost:5000/sentence_or_not',
                        data=payload)
                # https://cms.quill.org/fragments/is_sentence

        if i % 2 == 0: # sentence
            if round(r.json()['text']) == 1:
                numcorrect += 1
            else:
                false_negative += 1
                print(line.strip())
        elif i % 2 == 1: # fragment
            if round(r.json()['text']) == 0:
                numcorrect += 1
            else:
                false_positives += 1
                
        total += 1

print('false positives {}/{}'.format(false_positives, total))
print('false negatives {}/{}'.format(false_negative, total))
print('number correct {}/{}'.format(numcorrect, total))
print(float(numcorrect) / float(total))

#false positives 106/5302
#false negatives 2110/5302
#number correct 541/5302
#0.1020369671821954
