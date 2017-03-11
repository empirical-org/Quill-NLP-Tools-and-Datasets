
## TFLearn Fragment Detection

Catherine has prepared datafiles with sentences turned into fragments. I will use as input 60,000 fragments and 60,000 sentences. The fragments will come from the sentences. In the future the fragments will not be descendants of the input sentences. The labels will be either a 1 or 0, where 1 indicates a sentence and 0 indicates a fragment.

#### Install Dependencies


```python
import pandas as pd
import numpy as np
import tensorflow as tf
import tflearn
from tflearn.data_utils import to_categorical
import spacy
nlp = spacy.load('en')
import re
from nltk.util import ngrams, trigrams
```

#### Load Datafiles


```python
texts = []
labels = []

with open("./removingPOS/updatedSentences/conjunctionSentences/detailedRemoval.txt","r") as f:
    for line in f:
        asArray = line.split(" ||| ")
        fragment = asArray[2].strip()
        fragment = re.sub("\ \.", ".", fragment)
        fragment = re.sub("\,\.", ".", fragment)
        texts.append(fragment.capitalize())
        labels.append(0)
        texts.append(asArray[0].strip())
        labels.append(1)
        
with open("./removingPOS/updatedSentences/nounSentences/detailedRemoval.txt","r") as f:
    for line in f:
        asArray = line.split(" ||| ")
        fragment = asArray[2].strip()
        fragment = re.sub("\ \.", ".", fragment)
        fragment = re.sub("\,\.", ".", fragment)
        texts.append(fragment.capitalize())
        labels.append(0)
        texts.append(asArray[0].strip())
        labels.append(1)

with open("./removingPOS/updatedSentences/nounverbSentences/detailedRemoval.txt","r") as f:
    for line in f:
        asArray = line.split(" ||| ")
        fragment = asArray[2].strip()
        fragment = re.sub("\ \.", ".", fragment)
        fragment = re.sub("\,\.", ".", fragment)
        texts.append(fragment.capitalize())
        labels.append(0)
        texts.append(asArray[0].strip())
        labels.append(1)
        
with open("./removingPOS/updatedSentences/verbSentences/detailedRemoval.txt","r") as f:
    for line in f:
        asArray = line.split(" ||| ")
        fragment = asArray[2].strip()
        fragment = re.sub("\ \.", ".", fragment)
        fragment = re.sub("\,\.", ".", fragment)
        texts.append(fragment.capitalize())
        labels.append(0)
        texts.append(asArray[0].strip())
        labels.append(1)
        
print(texts[-10:])
```

    ['With 92% of dawson creek residents canadian-born, and 93% speaking only english, the city has few visible minorities.', 'With 92% of Dawson Creek residents being Canadian-born, and 93% speaking only English, the city has few visible minorities.', 'By the end of the year, the texians all mexican troops from texas.', 'By the end of the year, the Texians had driven all Mexican troops from Texas.', 'In northern manitoba, quartz to make arrowheads.', 'In Northern Manitoba, quartz was mined to make arrowheads.', 'There significant fictionalisation, however.', 'There was significant fictionalisation, however.', "Extremeolation from society and community also apparent in crane's work.", "Extreme isolation from society and community is also apparent in Crane's work."]


##### Shuffle the data


```python
import random

combined = list(zip(texts,labels))
random.shuffle(combined)

texts[:], labels[:] = zip(*combined)
print(texts[-10:])
print(labels[-10:])
```

    ['At other times, his bowling was often erratic but occasionally devastating.', 'The of three main elements.', 'Although made a push to close the gap, pleasure held their lead below barnes bridge but began to tire.', 'Instead harry bush, who not played first-class cricket for five years, led the team.', 'The large in the sawtooth valley, redfish, alturas, pettit, and stanley lakes, have developed boat accesses.', 'At Christmas the pair celebrated with chocolate and bread from their sledging rations.', "The newly national park service took over the park's administration in 1916.", 'He succeeded Roberto Luongo, who had stepped down as team captain the previous month.', "Wagner's role at Ludwig's court became controversial; in particular, Ludwig's habit of referring Wagner's policy ideas to his ministers alarmed the court.", 'The expedition arrived on 22 July 1718, surprising and trapping a ship commanded by pirate Charles Vane.']
    [1, 0, 0, 0, 0, 1, 0, 1, 1, 1]


##### Get parts of speech for text string


```python
def textStringToPOSArray(text):
    doc = nlp(text)
    tags = []
    for word in doc:
        tags.append(word.pos_)
    return tags

textStringToPOSArray(texts[3])
```




    ['ADV',
     'PUNCT',
     'NOUN',
     'ADP',
     'NOUN',
     'PART',
     'ADJ',
     'NOUN',
     'PUNCT',
     'CONJ',
     'VERB',
     'DET',
     'NOUN',
     'ADP',
     'NUM',
     'NUM',
     'NOUN',
     'PUNCT']



##### Get POS trigrams for a text string


```python
def find_ngrams(input_list, n):
  return zip(*[input_list[i:] for i in range(n)])

def getPOSTrigramsForTextString(text):
    tags = textStringToPOSArray(text)
    tgrams = list(trigrams(tags))
    return tgrams

print("Text: ", texts[3], labels[3])
getPOSTrigramsForTextString(texts[3])
```

    Text:  Furthermore, land to napoleon's german allies, and paid an indemnity of 40 million francs. 0





    [('ADV', 'PUNCT', 'NOUN'),
     ('PUNCT', 'NOUN', 'ADP'),
     ('NOUN', 'ADP', 'NOUN'),
     ('ADP', 'NOUN', 'PART'),
     ('NOUN', 'PART', 'ADJ'),
     ('PART', 'ADJ', 'NOUN'),
     ('ADJ', 'NOUN', 'PUNCT'),
     ('NOUN', 'PUNCT', 'CONJ'),
     ('PUNCT', 'CONJ', 'VERB'),
     ('CONJ', 'VERB', 'DET'),
     ('VERB', 'DET', 'NOUN'),
     ('DET', 'NOUN', 'ADP'),
     ('NOUN', 'ADP', 'NUM'),
     ('ADP', 'NUM', 'NUM'),
     ('NUM', 'NUM', 'NOUN'),
     ('NUM', 'NOUN', 'PUNCT')]



##### Turn Trigrams into Dict keys


```python
def trigramsToDictKeys(trigrams):
    keys = []
    for trigram in trigrams:
        keys.append('>'.join(trigram))
    return keys

print(texts[2])
print(trigramsToDictKeys(getPOSTrigramsForTextString(texts[2])))
```

    The Greater Manchester Film Festival was launched in 2012.
    ['DET>PROPN>PROPN', 'PROPN>PROPN>PROPN', 'PROPN>PROPN>PROPN', 'PROPN>PROPN>VERB', 'PROPN>VERB>VERB', 'VERB>VERB>ADP', 'VERB>ADP>NUM', 'ADP>NUM>PUNCT']



```python
from collections import Counter

c = Counter()

for textString in texts:
    c.update(trigramsToDictKeys(getPOSTrigramsForTextString(textString)))

total_counts = c

print("Total words in data set: ", len(total_counts))
```

    Total words in data set:  2097



```python
vocab = sorted(total_counts, key=total_counts.get, reverse=True)[:1200]
print(vocab[:60])
```

    ['ADP>DET>NOUN', 'NOUN>ADP>DET', 'ADJ>NOUN>PUNCT', 'DET>ADJ>NOUN', 'DET>NOUN>ADP', 'ADJ>NOUN>ADP', 'NOUN>ADP>NOUN', 'DET>NOUN>PUNCT', 'ADP>ADJ>NOUN', 'ADP>DET>ADJ', 'VERB>DET>NOUN', 'NOUN>NOUN>PUNCT', 'VERB>ADP>DET', 'DET>NOUN>VERB', 'ADP>NOUN>PUNCT', 'VERB>VERB>ADP', 'NOUN>ADP>ADJ', 'NOUN>VERB>VERB', 'ADJ>NOUN>VERB', 'ADJ>ADJ>NOUN', 'ADJ>NOUN>NOUN', 'NOUN>ADP>PROPN', 'DET>NOUN>NOUN', 'VERB>ADJ>NOUN', 'PROPN>PROPN>PUNCT', 'NOUN>NOUN>ADP', 'VERB>DET>ADJ', 'NOUN>VERB>ADP', 'NOUN>PUNCT>NOUN', 'NOUN>PUNCT>VERB', 'VERB>ADP>NOUN', 'ADP>NOUN>ADP', 'ADP>NUM>PUNCT', 'NOUN>ADP>NUM', 'ADP>DET>PROPN', 'NOUN>PUNCT>CONJ', 'NOUN>CONJ>NOUN', 'ADP>PROPN>PUNCT', 'VERB>NOUN>ADP', 'PROPN>PROPN>PROPN', 'DET>PROPN>PROPN', 'VERB>ADP>PROPN', 'NOUN>NOUN>VERB', 'NUM>NOUN>PUNCT', 'VERB>PART>VERB', 'VERB>ADV>VERB', 'PUNCT>DET>NOUN', 'ADP>PROPN>PROPN', 'VERB>ADP>ADJ', 'NOUN>VERB>DET', 'NOUN>PART>VERB', 'ADP>NUM>NOUN', 'VERB>NOUN>PUNCT', 'NOUN>VERB>ADV', 'ADV>VERB>ADP', 'ADP>NOUN>NOUN', 'NOUN>CONJ>VERB', 'NUM>NOUN>ADP', 'ADJ>NOUN>CONJ', 'NOUN>VERB>ADJ']



```python
print(vocab[-1], ': ', total_counts[vocab[-1]])
```

    CONJ>ADV>PART :  27


Take the trigrams and index them


```python
word2idx = {n: i for i, n in enumerate(vocab)}## create the word-to-index dictionary here
print(word2idx)
```

    {'ADP>DET>NOUN': 0, 'NOUN>ADP>DET': 1, 'ADJ>NOUN>PUNCT': 2, 'DET>ADJ>NOUN': 3, 'DET>NOUN>ADP': 4, 'ADJ>NOUN>ADP': 5, 'NOUN>ADP>NOUN': 6, 'DET>NOUN>PUNCT': 7, 'ADP>ADJ>NOUN': 8, 'ADP>DET>ADJ': 9, 'VERB>DET>NOUN': 10, 'NOUN>NOUN>PUNCT': 11, 'VERB>ADP>DET': 12, 'DET>NOUN>VERB': 13, 'ADP>NOUN>PUNCT': 14, 'VERB>VERB>ADP': 15, 'NOUN>ADP>ADJ': 16, 'NOUN>VERB>VERB': 17, 'ADJ>NOUN>VERB': 18, 'ADJ>ADJ>NOUN': 19, 'ADJ>NOUN>NOUN': 20, 'NOUN>ADP>PROPN': 21, 'DET>NOUN>NOUN': 22, 'VERB>ADJ>NOUN': 23, 'PROPN>PROPN>PUNCT': 24, 'NOUN>NOUN>ADP': 25, 'VERB>DET>ADJ': 26, 'NOUN>VERB>ADP': 27, 'NOUN>PUNCT>NOUN': 28, 'NOUN>PUNCT>VERB': 29, 'VERB>ADP>NOUN': 30, 'ADP>NOUN>ADP': 31, 'ADP>NUM>PUNCT': 32, 'NOUN>ADP>NUM': 33, 'ADP>DET>PROPN': 34, 'NOUN>PUNCT>CONJ': 35, 'NOUN>CONJ>NOUN': 36, 'ADP>PROPN>PUNCT': 37, 'VERB>NOUN>ADP': 38, 'PROPN>PROPN>PROPN': 39, 'DET>PROPN>PROPN': 40, 'VERB>ADP>PROPN': 41, 'NOUN>NOUN>VERB': 42, 'NUM>NOUN>PUNCT': 43, 'VERB>PART>VERB': 44, 'VERB>ADV>VERB': 45, 'PUNCT>DET>NOUN': 46, 'ADP>PROPN>PROPN': 47, 'VERB>ADP>ADJ': 48, 'NOUN>VERB>DET': 49, 'NOUN>PART>VERB': 50, 'ADP>NUM>NOUN': 51, 'VERB>NOUN>PUNCT': 52, 'NOUN>VERB>ADV': 53, 'ADV>VERB>ADP': 54, 'ADP>NOUN>NOUN': 55, 'NOUN>CONJ>VERB': 56, 'NUM>NOUN>ADP': 57, 'ADJ>NOUN>CONJ': 58, 'NOUN>VERB>ADJ': 59, 'NOUN>PUNCT>DET': 60, 'NOUN>NOUN>NOUN': 61, 'CONJ>ADJ>NOUN': 62, 'NOUN>PART>NOUN': 63, 'PROPN>PROPN>VERB': 64, 'PROPN>VERB>DET': 65, 'DET>NOUN>PART': 66, 'PART>VERB>DET': 67, 'NOUN>PUNCT>ADJ': 68, 'PROPN>VERB>VERB': 69, 'PUNCT>NOUN>NOUN': 70, 'PROPN>PART>NOUN': 71, 'PUNCT>PROPN>VERB': 72, 'PROPN>NUM>PUNCT': 73, 'VERB>ADP>NUM': 74, 'PUNCT>NOUN>PUNCT': 75, 'NOUN>PUNCT>ADP': 76, 'ADP>PROPN>NUM': 77, 'PROPN>PUNCT>PROPN': 78, 'PROPN>ADP>PROPN': 79, 'VERB>VERB>PUNCT': 80, 'NOUN>PUNCT>PROPN': 81, 'PUNCT>PRON>VERB': 82, 'ADJ>ADP>DET': 83, 'VERB>NUM>NOUN': 84, 'ADP>ADJ>ADJ': 85, 'DET>ADJ>ADJ': 86, 'PUNCT>ADJ>NOUN': 87, 'PUNCT>CONJ>VERB': 88, 'CONJ>NOUN>PUNCT': 89, 'PROPN>VERB>ADP': 90, 'NOUN>VERB>NOUN': 91, 'DET>NOUN>CONJ': 92, 'ADP>NOUN>CONJ': 93, 'PRON>VERB>VERB': 94, 'PROPN>PROPN>ADP': 95, 'PUNCT>NOUN>VERB': 96, 'NOUN>ADV>VERB': 97, 'ADV>ADP>DET': 98, 'PART>NOUN>PUNCT': 99, 'ADV>VERB>DET': 100, 'VERB>ADV>ADP': 101, 'PUNCT>VERB>ADP': 102, 'NOUN>NOUN>CONJ': 103, 'ADP>NOUN>VERB': 104, 'VERB>ADJ>ADP': 105, 'CONJ>DET>NOUN': 106, 'PROPN>NOUN>PUNCT': 107, 'PROPN>CONJ>PROPN': 108, 'NOUN>PUNCT>ADV': 109, 'PART>ADJ>NOUN': 110, 'PROPN>ADP>DET': 111, 'VERB>NOUN>NOUN': 112, 'PUNCT>VERB>DET': 113, 'NOUN>CONJ>ADJ': 114, 'PUNCT>DET>ADJ': 115, 'PART>VERB>NOUN': 116, 'NOUN>ADP>VERB': 117, 'DET>NOUN>ADV': 118, 'PRON>VERB>DET': 119, 'PART>VERB>ADP': 120, 'VERB>ADV>ADJ': 121, 'PUNCT>VERB>NOUN': 122, 'CONJ>NOUN>NOUN': 123, 'VERB>VERB>VERB': 124, 'PRON>VERB>ADP': 125, 'CONJ>VERB>ADP': 126, 'NOUN>VERB>PUNCT': 127, 'ADP>PROPN>PART': 128, 'ADP>PROPN>ADP': 129, 'ADJ>NOUN>PART': 130, 'ADV>VERB>PUNCT': 131, 'ADV>ADJ>NOUN': 132, 'VERB>VERB>DET': 133, 'VERB>ADJ>PUNCT': 134, 'PROPN>VERB>ADJ': 135, 'CONJ>VERB>DET': 136, 'VERB>ADJ>ADJ': 137, 'ADP>PROPN>VERB': 138, 'PROPN>VERB>ADV': 139, 'ADJ>PUNCT>NOUN': 140, 'PUNCT>PROPN>PROPN': 141, 'PRON>VERB>ADV': 142, 'PART>VERB>ADJ': 143, 'ADJ>NOUN>ADV': 144, 'PUNCT>CONJ>DET': 145, 'ADP>DET>NUM': 146, 'PROPN>PUNCT>VERB': 147, 'VERB>ADV>PUNCT': 148, 'PUNCT>ADP>DET': 149, 'NUM>NOUN>VERB': 150, 'DET>NUM>NOUN': 151, 'NOUN>VERB>PART': 152, 'DET>ADJ>PUNCT': 153, 'PART>NOUN>ADP': 154, 'NOUN>PUNCT>PRON': 155, 'NUM>ADJ>NOUN': 156, 'VERB>VERB>PART': 157, 'DET>VERB>NOUN': 158, 'VERB>DET>PROPN': 159, 'NUM>ADP>DET': 160, 'ADP>NOUN>PART': 161, 'PUNCT>CONJ>NOUN': 162, 'NOUN>ADV>PUNCT': 163, 'CONJ>NOUN>VERB': 164, 'PART>NOUN>VERB': 165, 'ADV>VERB>NOUN': 166, 'NOUN>ADJ>NOUN': 167, 'NOUN>CONJ>DET': 168, 'DET>PROPN>NOUN': 169, 'ADP>NUM>PROPN': 170, 'PUNCT>PROPN>PUNCT': 171, 'ADP>PRON>VERB': 172, 'CONJ>NOUN>ADP': 173, 'PROPN>ADV>VERB': 174, 'ADJ>ADP>NOUN': 175, 'PROPN>PUNCT>DET': 176, 'ADV>VERB>ADJ': 177, 'ADP>NUM>ADP': 178, 'NOUN>NUM>PUNCT': 179, 'PUNCT>ADJ>VERB': 180, 'ADJ>ADP>ADJ': 181, 'NOUN>DET>NOUN': 182, 'PUNCT>NOUN>ADP': 183, 'VERB>VERB>ADV': 184, 'VERB>CONJ>VERB': 185, 'ADP>NOUN>NUM': 186, 'ADJ>CONJ>ADJ': 187, 'PROPN>NOUN>VERB': 188, 'VERB>VERB>ADJ': 189, 'VERB>PROPN>PROPN': 190, 'PRON>VERB>ADJ': 191, 'CONJ>VERB>NOUN': 192, 'PROPN>ADP>NUM': 193, 'ADP>VERB>NOUN': 194, 'ADV>DET>NOUN': 195, 'NUM>PUNCT>NUM': 196, 'CONJ>VERB>ADJ': 197, 'ADV>ADP>NOUN': 198, 'ADV>ADJ>ADP': 199, 'VERB>NOUN>CONJ': 200, 'NOUN>PART>ADJ': 201, 'NOUN>ADV>ADP': 202, 'PROPN>PROPN>CONJ': 203, 'DET>PROPN>PUNCT': 204, 'CONJ>VERB>VERB': 205, 'DET>NOUN>ADJ': 206, 'ADP>DET>VERB': 207, 'ADV>PUNCT>VERB': 208, 'NUM>NOUN>NOUN': 209, 'VERB>ADV>ADV': 210, 'PROPN>PART>ADJ': 211, 'PRON>ADV>VERB': 212, 'DET>PROPN>ADP': 213, 'VERB>VERB>NOUN': 214, 'PUNCT>VERB>ADJ': 215, 'PROPN>PUNCT>CONJ': 216, 'ADP>PROPN>CONJ': 217, 'ADV>ADJ>PUNCT': 218, 'NUM>PUNCT>NOUN': 219, 'PUNCT>VERB>VERB': 220, 'ADJ>NOUN>ADJ': 221, 'DET>ADJ>PROPN': 222, 'CONJ>ADV>VERB': 223, 'DET>ADP>DET': 224, 'ADV>PUNCT>DET': 225, 'PUNCT>NUM>PUNCT': 226, 'PROPN>PROPN>NOUN': 227, 'ADJ>PART>VERB': 228, 'NOUN>ADJ>VERB': 229, 'ADV>NUM>NOUN': 230, 'DET>PROPN>VERB': 231, 'PUNCT>CONJ>ADJ': 232, 'PUNCT>NOUN>CONJ': 233, 'PUNCT>ADP>NOUN': 234, 'CONJ>DET>ADJ': 235, 'CONJ>VERB>ADV': 236, 'PART>VERB>PUNCT': 237, 'NUM>PUNCT>DET': 238, 'ADP>ADJ>PUNCT': 239, 'VERB>NOUN>VERB': 240, 'PUNCT>ADV>VERB': 241, 'CONJ>PROPN>PROPN': 242, 'PUNCT>ADP>ADJ': 243, 'NUM>PUNCT>PROPN': 244, 'VERB>PRON>ADP': 245, 'PROPN>PUNCT>NOUN': 246, 'NOUN>VERB>PROPN': 247, 'PUNCT>DET>PROPN': 248, 'NOUN>PROPN>PROPN': 249, 'DET>ADV>ADJ': 250, 'NUM>NOUN>CONJ': 251, 'PROPN>VERB>NOUN': 252, 'ADP>VERB>DET': 253, 'NOUN>VERB>NUM': 254, 'ADP>NUM>CONJ': 255, 'PROPN>PUNCT>ADP': 256, 'DET>ADJ>ADP': 257, 'PROPN>NOUN>ADP': 258, 'ADJ>NUM>NOUN': 259, 'VERB>PUNCT>CONJ': 260, 'PROPN>VERB>PROPN': 261, 'CONJ>NUM>NOUN': 262, 'VERB>ADP>VERB': 263, 'PART>VERB>VERB': 264, 'PROPN>PROPN>PART': 265, 'VERB>NOUN>PART': 266, 'PROPN>VERB>PART': 267, 'ADV>ADP>ADJ': 268, 'CONJ>PROPN>VERB': 269, 'PART>NOUN>NOUN': 270, 'VERB>PROPN>ADP': 271, 'ADJ>VERB>VERB': 272, 'ADJ>PUNCT>ADJ': 273, 'ADV>VERB>PART': 274, 'ADP>ADP>DET': 275, 'VERB>PROPN>PART': 276, 'NOUN>PRON>VERB': 277, 'PUNCT>ADV>PUNCT': 278, 'NUM>PUNCT>VERB': 279, 'ADP>DET>PUNCT': 280, 'ADP>ADJ>NUM': 281, 'NOUN>NOUN>PART': 282, 'ADV>ADV>PUNCT': 283, 'PUNCT>CONJ>ADV': 284, 'PUNCT>CONJ>PROPN': 285, 'ADJ>PROPN>PROPN': 286, 'ADV>ADP>PROPN': 287, 'NUM>PUNCT>CONJ': 288, 'PROPN>VERB>NUM': 289, 'NOUN>NOUN>ADV': 290, 'NOUN>ADJ>ADP': 291, 'PUNCT>VERB>NUM': 292, 'PROPN>PART>VERB': 293, 'VERB>ADP>PRON': 294, 'NUM>ADP>NUM': 295, 'CONJ>PROPN>PUNCT': 296, 'ADJ>VERB>NOUN': 297, 'ADV>ADV>VERB': 298, 'ADV>VERB>ADV': 299, 'PUNCT>ADV>ADP': 300, 'VERB>NUM>ADP': 301, 'ADP>VERB>ADP': 302, 'ADV>ADV>ADP': 303, 'VERB>PROPN>PUNCT': 304, 'CONJ>PRON>VERB': 305, 'PUNCT>NUM>NOUN': 306, 'VERB>PART>ADP': 307, 'DET>ADP>NOUN': 308, 'ADV>VERB>VERB': 309, 'ADP>PROPN>NOUN': 310, 'ADP>PUNCT>NOUN': 311, 'PROPN>PUNCT>ADV': 312, 'PUNCT>VERB>ADV': 313, 'ADV>DET>ADJ': 314, 'NUM>PROPN>NUM': 315, 'ADJ>ADJ>ADJ': 316, 'PUNCT>ADP>NUM': 317, 'ADV>PRON>VERB': 318, 'NUM>NOUN>ADV': 319, 'NOUN>PUNCT>NUM': 320, 'ADJ>VERB>ADP': 321, 'NOUN>VERB>PRON': 322, 'ADP>ADJ>PROPN': 323, 'PROPN>PUNCT>ADJ': 324, 'NUM>CONJ>NUM': 325, 'NOUN>CONJ>NUM': 326, 'NOUN>DET>ADJ': 327, 'PUNCT>CONJ>ADP': 328, 'ADP>DET>ADP': 329, 'DET>NOUN>DET': 330, 'DET>ADJ>NUM': 331, 'PROPN>CONJ>VERB': 332, 'PRON>VERB>PART': 333, 'PROPN>ADP>ADJ': 334, 'PRON>VERB>NOUN': 335, 'PUNCT>ADP>PROPN': 336, 'NOUN>ADJ>PUNCT': 337, 'VERB>ADP>ADP': 338, 'NOUN>NOUN>ADJ': 339, 'VERB>PUNCT>VERB': 340, 'ADJ>PUNCT>CONJ': 341, 'NOUN>ADP>PRON': 342, 'ADV>PUNCT>ADP': 343, 'PRON>ADP>DET': 344, 'DET>ADJ>VERB': 345, 'ADJ>NOUN>DET': 346, 'ADJ>NOUN>PROPN': 347, 'ADJ>NUM>PUNCT': 348, 'NOUN>ADP>ADV': 349, 'VERB>PRON>PUNCT': 350, 'PUNCT>CONJ>PRON': 351, 'ADJ>ADP>NUM': 352, 'VERB>ADV>DET': 353, 'NUM>PUNCT>PRON': 354, 'PUNCT>ADJ>ADP': 355, 'VERB>NUM>PUNCT': 356, 'PART>VERB>ADV': 357, 'VERB>VERB>CONJ': 358, 'ADJ>ADJ>PUNCT': 359, 'ADV>PUNCT>NOUN': 360, 'NOUN>NUM>NOUN': 361, 'NOUN>CONJ>ADV': 362, 'PROPN>NOUN>NOUN': 363, 'CONJ>ADJ>ADJ': 364, 'DET>VERB>VERB': 365, 'ADJ>PROPN>PUNCT': 366, 'ADJ>VERB>DET': 367, 'NUM>PUNCT>ADP': 368, 'ADJ>ADP>PROPN': 369, 'VERB>ADJ>PART': 370, 'ADP>NUM>ADJ': 371, 'CONJ>VERB>PART': 372, 'ADJ>PUNCT>VERB': 373, 'PRON>VERB>NUM': 374, 'NUM>CONJ>VERB': 375, 'DET>VERB>DET': 376, 'NUM>ADP>NOUN': 377, 'NOUN>ADP>ADP': 378, 'ADP>PRON>PUNCT': 379, 'ADP>ADJ>ADP': 380, 'NUM>PROPN>PUNCT': 381, 'DET>ADJ>CONJ': 382, 'PROPN>ADP>NOUN': 383, 'CONJ>VERB>NUM': 384, 'PROPN>PART>PROPN': 385, 'VERB>DET>VERB': 386, 'VERB>DET>ADV': 387, 'DET>ADV>VERB': 388, 'ADP>DET>ADV': 389, 'ADV>PUNCT>PRON': 390, 'ADP>VERB>ADJ': 391, 'ADV>PUNCT>PROPN': 392, 'ADP>ADP>NOUN': 393, 'PROPN>VERB>PUNCT': 394, 'PRON>VERB>PUNCT': 395, 'PUNCT>ADJ>ADJ': 396, 'ADV>PART>VERB': 397, 'ADV>PUNCT>ADJ': 398, 'PUNCT>PROPN>CONJ': 399, 'ADV>ADP>NUM': 400, 'PART>VERB>PROPN': 401, 'ADP>NOUN>ADJ': 402, 'DET>VERB>ADJ': 403, 'PART>VERB>PRON': 404, 'PUNCT>VERB>PROPN': 405, 'CONJ>VERB>PUNCT': 406, 'ADJ>PROPN>NOUN': 407, 'ADP>NOUN>ADV': 408, 'PROPN>CONJ>DET': 409, 'VERB>ADV>NUM': 410, 'DET>ADP>ADJ': 411, 'NOUN>ADV>ADV': 412, 'DET>NUM>PUNCT': 413, 'NUM>ADP>ADJ': 414, 'ADJ>VERB>ADJ': 415, 'VERB>ADJ>CONJ': 416, 'PUNCT>ADJ>PUNCT': 417, 'DET>VERB>ADP': 418, 'ADV>PUNCT>CONJ': 419, 'ADP>PUNCT>DET': 420, 'ADV>VERB>PROPN': 421, 'CONJ>ADP>DET': 422, 'CONJ>DET>PROPN': 423, 'VERB>ADP>ADV': 424, 'PRON>PART>VERB': 425, 'VERB>PRON>VERB': 426, 'VERB>NUM>ADJ': 427, 'VERB>DET>NUM': 428, 'ADJ>VERB>ADV': 429, 'ADJ>DET>NOUN': 430, 'ADP>ADV>NUM': 431, 'PUNCT>VERB>PUNCT': 432, 'CONJ>NUM>PUNCT': 433, 'ADV>VERB>NUM': 434, 'ADP>ADP>ADJ': 435, 'PROPN>CONJ>ADJ': 436, 'PUNCT>PROPN>PART': 437, 'NOUN>PROPN>VERB': 438, 'ADP>NUM>VERB': 439, 'VERB>PART>DET': 440, 'NOUN>CONJ>ADP': 441, 'PUNCT>NOUN>PART': 442, 'CONJ>VERB>PRON': 443, 'VERB>PUNCT>ADP': 444, 'NUM>ADP>PROPN': 445, 'PART>NOUN>CONJ': 446, 'DET>NOUN>PROPN': 447, 'DET>NOUN>PRON': 448, 'NOUN>ADV>ADJ': 449, 'PUNCT>VERB>PART': 450, 'VERB>PRON>PART': 451, 'PROPN>ADJ>NOUN': 452, 'CONJ>ADJ>PUNCT': 453, 'NOUN>VERB>CONJ': 454, 'DET>PROPN>PART': 455, 'NUM>NOUN>NUM': 456, 'DET>VERB>ADV': 457, 'ADV>PUNCT>ADV': 458, 'ADJ>ADP>VERB': 459, 'ADP>ADP>NUM': 460, 'ADP>ADV>VERB': 461, 'PUNCT>VERB>PRON': 462, 'DET>PUNCT>NOUN': 463, 'SYM>NUM>NUM': 464, 'PRON>ADP>NOUN': 465, 'VERB>NOUN>ADV': 466, 'PRON>VERB>PROPN': 467, 'PART>VERB>PART': 468, 'ADP>ADJ>VERB': 469, 'ADJ>PUNCT>ADP': 470, 'ADV>ADV>ADJ': 471, 'NUM>PUNCT>ADV': 472, 'PART>ADP>DET': 473, 'DET>PROPN>CONJ': 474, 'ADJ>PROPN>VERB': 475, 'NOUN>NOUN>DET': 476, 'PUNCT>CONJ>NUM': 477, 'ADP>ADJ>CONJ': 478, 'VERB>VERB>PROPN': 479, 'ADJ>CONJ>VERB': 480, 'ADP>VERB>PUNCT': 481, 'PROPN>PROPN>ADV': 482, 'NUM>PUNCT>ADJ': 483, 'VERB>PART>PUNCT': 484, 'DET>NOUN>NUM': 485, 'PUNCT>NOUN>ADV': 486, 'ADV>NOUN>ADP': 487, 'PROPN>VERB>PRON': 488, 'PRON>DET>NOUN': 489, 'ADJ>ADV>VERB': 490, 'PUNCT>ADV>ADV': 491, 'NUM>NOUN>ADJ': 492, 'PROPN>NUM>ADP': 493, 'ADV>NOUN>PUNCT': 494, 'NUM>PROPN>PROPN': 495, 'ADV>VERB>CONJ': 496, 'ADV>VERB>PRON': 497, 'PROPN>PUNCT>PRON': 498, 'ADJ>PRON>VERB': 499, 'PUNCT>DET>VERB': 500, 'PUNCT>PROPN>NOUN': 501, 'VERB>PART>NOUN': 502, 'ADV>CONJ>VERB': 503, 'PUNCT>ADV>ADJ': 504, 'VERB>VERB>NUM': 505, 'VERB>PUNCT>DET': 506, 'PART>ADJ>ADJ': 507, 'VERB>DET>ADP': 508, 'ADP>VERB>VERB': 509, 'DET>NUM>ADJ': 510, 'PROPN>DET>NOUN': 511, 'PUNCT>ADV>DET': 512, 'PUNCT>ADP>VERB': 513, 'NOUN>ADV>DET': 514, 'ADP>ADV>ADJ': 515, 'ADV>ADP>VERB': 516, 'NOUN>PROPN>PUNCT': 517, 'DET>ADV>PUNCT': 518, 'VERB>PUNCT>ADV': 519, 'PUNCT>NUM>ADP': 520, 'NOUN>NOUN>PROPN': 521, 'ADP>SYM>NUM': 522, 'PROPN>NOUN>CONJ': 523, 'VERB>PUNCT>NOUN': 524, 'PART>DET>NOUN': 525, 'ADJ>PUNCT>DET': 526, 'NUM>NOUN>PART': 527, 'PUNCT>PART>VERB': 528, 'VERB>ADV>CONJ': 529, 'PUNCT>ADV>PRON': 530, 'CONJ>PROPN>NOUN': 531, 'ADV>ADJ>ADJ': 532, 'VERB>ADP>PUNCT': 533, 'ADP>ADV>PUNCT': 534, 'NOUN>NUM>ADP': 535, 'PRON>DET>ADJ': 536, 'ADV>PROPN>VERB': 537, 'VERB>NOUN>ADJ': 538, 'PART>PROPN>PROPN': 539, 'ADJ>NOUN>PRON': 540, 'ADJ>PROPN>ADP': 541, 'DET>NUM>PROPN': 542, 'PUNCT>NOUN>ADJ': 543, 'ADV>ADJ>CONJ': 544, 'PART>NUM>NOUN': 545, 'DET>ADJ>ADV': 546, 'NUM>NUM>NOUN': 547, 'ADJ>PUNCT>ADV': 548, 'PART>VERB>CONJ': 549, 'PUNCT>ADP>ADP': 550, 'ADJ>ADJ>ADP': 551, 'DET>DET>NOUN': 552, 'DET>PUNCT>DET': 553, 'CONJ>ADV>ADJ': 554, 'PUNCT>ADP>PRON': 555, 'NOUN>CONJ>PROPN': 556, 'PUNCT>DET>ADP': 557, 'PRON>ADP>ADJ': 558, 'NUM>PROPN>VERB': 559, 'VERB>PRON>DET': 560, 'PUNCT>PRON>ADV': 561, 'PROPN>NOUN>PART': 562, 'PUNCT>ADP>PUNCT': 563, 'NUM>PRON>VERB': 564, 'PUNCT>ADV>NOUN': 565, 'CONJ>ADP>ADJ': 566, 'ADP>NOUN>DET': 567, 'CONJ>NOUN>ADV': 568, 'CONJ>ADP>NOUN': 569, 'VERB>PROPN>CONJ': 570, 'NUM>VERB>VERB': 571, 'VERB>PART>ADJ': 572, 'VERB>ADV>NOUN': 573, 'ADP>ADP>PROPN': 574, 'CONJ>NOUN>PART': 575, 'PROPN>NUM>NOUN': 576, 'PART>NOUN>PART': 577, 'ADJ>CONJ>NOUN': 578, 'VERB>PROPN>NOUN': 579, 'ADP>VERB>ADV': 580, 'ADP>PUNCT>PRON': 581, 'ADP>PROPN>ADV': 582, 'ADJ>ADV>PUNCT': 583, 'PROPN>DET>ADJ': 584, 'CONJ>ADJ>ADP': 585, 'ADP>NOUN>PROPN': 586, 'VERB>PUNCT>PROPN': 587, 'ADP>ADJ>DET': 588, 'ADJ>ADJ>CONJ': 589, 'PART>VERB>NUM': 590, 'NUM>VERB>ADP': 591, 'ADP>VERB>PART': 592, 'NUM>NUM>PUNCT': 593, 'CONJ>DET>VERB': 594, 'VERB>PRON>ADV': 595, 'VERB>VERB>PRON': 596, 'CONJ>ADP>NUM': 597, 'ADV>ADJ>PART': 598, 'ADP>PUNCT>VERB': 599, 'PROPN>ADP>VERB': 600, 'PUNCT>PROPN>ADV': 601, 'NUM>VERB>NOUN': 602, 'ADV>NOUN>VERB': 603, 'PUNCT>ADP>ADV': 604, 'VERB>ADV>PART': 605, 'ADJ>PUNCT>PROPN': 606, 'PART>NOUN>ADV': 607, 'CONJ>PROPN>ADP': 608, 'PROPN>CONJ>NOUN': 609, 'CONJ>VERB>PROPN': 610, 'NUM>NOUN>DET': 611, 'VERB>PRON>ADJ': 612, 'DET>ADP>NUM': 613, 'PUNCT>ADV>NUM': 614, 'ADJ>ADP>PRON': 615, 'CONJ>NUM>ADJ': 616, 'NOUN>ADP>PUNCT': 617, 'NUM>PART>VERB': 618, 'ADJ>CONJ>ADV': 619, 'CONJ>ADV>ADP': 620, 'NOUN>PUNCT>PART': 621, 'CONJ>NOUN>CONJ': 622, 'NUM>DET>NOUN': 623, 'PROPN>ADV>ADP': 624, 'ADP>ADV>DET': 625, 'PART>ADP>NOUN': 626, 'ADP>NUM>PRON': 627, 'NOUN>ADJ>ADJ': 628, 'VERB>ADJ>PROPN': 629, 'DET>VERB>NUM': 630, 'PRON>VERB>PRON': 631, 'ADJ>NOUN>NUM': 632, 'ADP>PRON>ADP': 633, 'VERB>PUNCT>ADJ': 634, 'PUNCT>PROPN>ADP': 635, 'NOUN>PROPN>NOUN': 636, 'VERB>ADJ>ADV': 637, 'PROPN>NUM>CONJ': 638, 'ADP>VERB>PROPN': 639, 'VERB>NUM>CONJ': 640, 'PROPN>NOUN>PROPN': 641, 'DET>NUM>VERB': 642, 'PUNCT>DET>ADV': 643, 'VERB>CONJ>NOUN': 644, 'ADP>NUM>DET': 645, 'PROPN>PUNCT>NUM': 646, 'ADP>PART>VERB': 647, 'DET>VERB>PROPN': 648, 'VERB>ADJ>VERB': 649, 'VERB>SYM>NUM': 650, 'ADP>VERB>NUM': 651, 'PUNCT>ADJ>ADV': 652, 'NOUN>ADV>NOUN': 653, 'ADJ>PUNCT>PRON': 654, 'PUNCT>NOUN>PROPN': 655, 'CONJ>NUM>ADP': 656, 'ADJ>ADV>ADP': 657, 'NUM>ADJ>PUNCT': 658, 'PUNCT>VERB>CONJ': 659, 'ADP>NOUN>PRON': 660, 'ADJ>ADJ>PROPN': 661, 'PART>ADV>VERB': 662, 'PUNCT>ADJ>CONJ': 663, 'ADV>NUM>PUNCT': 664, 'PROPN>NOUN>ADV': 665, 'PART>PROPN>PUNCT': 666, 'PUNCT>DET>NUM': 667, 'DET>VERB>PUNCT': 668, 'ADV>CONJ>ADV': 669, 'CONJ>ADV>PUNCT': 670, 'ADP>PUNCT>ADJ': 671, 'ADV>NUM>ADJ': 672, 'VERB>CONJ>DET': 673, 'CONJ>NOUN>ADJ': 674, 'ADV>ADP>ADP': 675, 'ADJ>ADV>ADJ': 676, 'CONJ>ADP>PROPN': 677, 'VERB>PUNCT>PRON': 678, 'NOUN>ADV>CONJ': 679, 'PRON>ADV>ADP': 680, 'PROPN>ADV>PUNCT': 681, 'ADJ>DET>ADJ': 682, 'PUNCT>ADJ>PROPN': 683, 'PRON>ADJ>NOUN': 684, 'NUM>ADJ>ADJ': 685, 'ADV>PROPN>PROPN': 686, 'ADV>ADP>PRON': 687, 'NUM>NUM>ADP': 688, 'VERB>CONJ>ADJ': 689, 'CONJ>ADV>ADV': 690, 'VERB>DET>PUNCT': 691, 'NOUN>PART>NUM': 692, 'NUM>VERB>DET': 693, 'VERB>CONJ>ADV': 694, 'ADV>NOUN>NOUN': 695, 'CONJ>PROPN>PART': 696, 'NOUN>NOUN>NUM': 697, 'NOUN>PART>ADV': 698, 'DET>PROPN>ADV': 699, 'DET>PUNCT>ADJ': 700, 'ADP>ADJ>PRON': 701, 'ADP>NUM>ADV': 702, 'ADP>NUM>PART': 703, 'PROPN>PRON>VERB': 704, 'VERB>PROPN>VERB': 705, 'DET>PROPN>NUM': 706, 'NOUN>ADV>PRON': 707, 'CONJ>NUM>VERB': 708, 'NUM>PROPN>NOUN': 709, 'ADP>ADV>ADP': 710, 'ADJ>ADJ>VERB': 711, 'SYM>NUM>PUNCT': 712, 'PUNCT>PRON>ADP': 713, 'ADP>NUM>NUM': 714, 'PROPN>ADV>ADV': 715, 'CONJ>DET>NUM': 716, 'PART>ADP>ADJ': 717, 'ADJ>VERB>PART': 718, 'PUNCT>CONJ>PUNCT': 719, 'ADJ>NUM>ADP': 720, 'PUNCT>ADV>PROPN': 721, 'PROPN>PART>NUM': 722, 'ADP>PUNCT>NUM': 723, 'PUNCT>PRON>DET': 724, 'PROPN>PROPN>ADJ': 725, 'ADV>ADV>ADV': 726, 'NUM>VERB>PUNCT': 727, 'ADP>ADJ>ADV': 728, 'VERB>PART>ADV': 729, 'NOUN>DET>VERB': 730, 'DET>DET>ADJ': 731, 'NUM>VERB>ADJ': 732, 'NOUN>ADJ>CONJ': 733, 'DET>ADJ>PART': 734, 'PRON>ADP>NUM': 735, 'DET>ADP>PROPN': 736, 'PRON>ADV>PUNCT': 737, 'ADJ>VERB>NUM': 738, 'VERB>ADP>SYM': 739, 'DET>PUNCT>PRON': 740, 'ADV>NUM>ADP': 741, 'NOUN>ADP>CONJ': 742, 'NOUN>NUM>CONJ': 743, 'NUM>CONJ>DET': 744, 'PUNCT>NUM>ADJ': 745, 'ADV>DET>PROPN': 746, 'SYM>NUM>ADP': 747, 'PROPN>VERB>CONJ': 748, 'ADP>PROPN>ADJ': 749, 'PART>ADP>NUM': 750, 'NOUN>CONJ>PUNCT': 751, 'VERB>NUM>VERB': 752, 'PROPN>CONJ>ADV': 753, 'ADV>ADV>DET': 754, 'ADJ>ADP>ADP': 755, 'ADP>VERB>PRON': 756, 'CONJ>ADJ>PROPN': 757, 'PRON>ADP>VERB': 758, 'ADJ>CONJ>DET': 759, 'PART>ADP>PROPN': 760, 'CONJ>ADV>DET': 761, 'PUNCT>ADJ>PRON': 762, 'NUM>CONJ>ADV': 763, 'DET>PART>VERB': 764, 'PART>NOUN>PROPN': 765, 'ADV>ADP>PUNCT': 766, 'ADJ>VERB>PROPN': 767, 'PUNCT>NOUN>DET': 768, 'VERB>PROPN>NUM': 769, 'DET>PUNCT>VERB': 770, 'PART>ADV>ADJ': 771, 'NOUN>ADV>PART': 772, 'ADP>VERB>CONJ': 773, 'PROPN>NUM>PROPN': 774, 'CONJ>PROPN>ADV': 775, 'NOUN>NOUN>PRON': 776, 'ADP>PRON>ADV': 777, 'PART>PROPN>ADP': 778, 'DET>PROPN>ADJ': 779, 'ADJ>PROPN>CONJ': 780, 'CONJ>ADJ>VERB': 781, 'ADP>CONJ>ADP': 782, 'PRON>ADP>PROPN': 783, 'DET>ADV>ADP': 784, 'DET>VERB>PART': 785, 'NOUN>CONJ>PRON': 786, 'VERB>ADV>PROPN': 787, 'NOUN>ADP>SYM': 788, 'VERB>ADP>PART': 789, 'ADP>PUNCT>ADP': 790, 'ADP>ADV>ADV': 791, 'NOUN>ADJ>ADV': 792, 'DET>PUNCT>ADP': 793, 'DET>ADV>ADV': 794, 'PRON>PUNCT>VERB': 795, 'PROPN>ADV>DET': 796, 'PROPN>NUM>VERB': 797, 'NOUN>PROPN>ADP': 798, 'NOUN>DET>PROPN': 799, 'CONJ>PUNCT>ADP': 800, 'ADJ>VERB>PUNCT': 801, 'VERB>PROPN>ADV': 802, 'ADJ>NUM>ADJ': 803, 'PART>DET>ADJ': 804, 'PUNCT>NUM>VERB': 805, 'PROPN>PROPN>NUM': 806, 'PUNCT>NOUN>NUM': 807, 'PRON>CONJ>VERB': 808, 'VERB>PRON>NOUN': 809, 'NOUN>PROPN>CONJ': 810, 'PROPN>ADJ>VERB': 811, 'VERB>NOUN>PROPN': 812, 'VERB>ADJ>NUM': 813, 'ADP>DET>DET': 814, 'ADJ>ADJ>NUM': 815, 'PRON>ADV>ADV': 816, 'NOUN>PRON>PUNCT': 817, 'DET>ADJ>DET': 818, 'CONJ>PART>VERB': 819, 'PRON>NUM>NOUN': 820, 'ADJ>VERB>PRON': 821, 'PRON>PUNCT>CONJ': 822, 'ADV>ADJ>VERB': 823, 'VERB>ADJ>DET': 824, 'PART>PART>VERB': 825, 'VERB>NOUN>DET': 826, 'PUNCT>NUM>PROPN': 827, 'CONJ>PROPN>CONJ': 828, 'PART>NOUN>DET': 829, 'NUM>PROPN>ADP': 830, 'PROPN>ADP>PRON': 831, 'NOUN>ADV>NUM': 832, 'PROPN>CONJ>NUM': 833, 'PUNCT>NUM>CONJ': 834, 'VERB>PART>NUM': 835, 'VERB>PART>PART': 836, 'VERB>CONJ>NUM': 837, 'NOUN>PART>ADP': 838, 'ADV>ADV>CONJ': 839, 'X>PUNCT>NOUN': 840, 'NOUN>PART>PROPN': 841, 'ADJ>ADP>PUNCT': 842, 'NUM>ADP>VERB': 843, 'NUM>CONJ>ADJ': 844, 'ADV>NOUN>CONJ': 845, 'ADP>PROPN>DET': 846, 'PRON>CONJ>ADJ': 847, 'PROPN>CONJ>ADP': 848, 'NUM>ADV>PUNCT': 849, 'NUM>VERB>ADV': 850, 'PRON>ADV>ADJ': 851, 'VERB>PROPN>DET': 852, 'DET>CONJ>NOUN': 853, 'PRON>ADJ>ADP': 854, 'PRON>NOUN>ADP': 855, 'NUM>ADP>PRON': 856, 'DET>PUNCT>ADV': 857, 'ADP>ADP>PUNCT': 858, 'ADP>ADV>NOUN': 859, 'NUM>ADJ>NUM': 860, 'PROPN>NUM>DET': 861, 'ADV>DET>VERB': 862, 'VERB>PART>CONJ': 863, 'ADV>ADV>NUM': 864, 'NOUN>ADJ>PROPN': 865, 'ADJ>ADP>ADV': 866, 'PART>NOUN>ADJ': 867, 'NOUN>ADV>PROPN': 868, 'NUM>VERB>NUM': 869, 'X>PUNCT>ADJ': 870, 'ADV>DET>ADP': 871, 'PROPN>ADP>ADP': 872, 'DET>PUNCT>NUM': 873, 'CONJ>ADV>NOUN': 874, 'PART>NUM>PUNCT': 875, 'DET>ADV>NOUN': 876, 'NUM>PART>NUM': 877, 'ADV>PUNCT>NUM': 878, 'NUM>ADV>ADV': 879, 'ADJ>NUM>VERB': 880, 'NOUN>NUM>VERB': 881, 'PROPN>PROPN>DET': 882, 'PART>ADJ>PUNCT': 883, 'VERB>NOUN>NUM': 884, 'DET>NUM>ADP': 885, 'ADP>PRON>CONJ': 886, 'PART>CONJ>VERB': 887, 'NOUN>PART>PUNCT': 888, 'CONJ>PRON>ADV': 889, 'VERB>ADP>CONJ': 890, 'NOUN>ADJ>PART': 891, 'CONJ>VERB>CONJ': 892, 'ADV>ADP>ADV': 893, 'ADJ>NUM>CONJ': 894, 'PUNCT>PRON>NUM': 895, 'ADP>PROPN>PRON': 896, 'PROPN>NOUN>ADJ': 897, 'ADP>PUNCT>ADV': 898, 'PROPN>PUNCT>PART': 899, 'PRON>VERB>CONJ': 900, 'ADV>SYM>NUM': 901, 'NUM>ADV>VERB': 902, 'ADV>NUM>VERB': 903, 'PROPN>ADJ>ADP': 904, 'PROPN>PART>ADV': 905, 'ADV>ADV>NOUN': 906, 'CONJ>NOUN>PROPN': 907, 'ADP>PUNCT>PROPN': 908, 'CONJ>DET>ADV': 909, 'VERB>PRON>CONJ': 910, 'CONJ>NUM>PROPN': 911, 'ADV>ADJ>DET': 912, 'NUM>PROPN>CONJ': 913, 'NOUN>PRON>ADV': 914, 'ADJ>ADV>ADV': 915, 'ADV>PROPN>PUNCT': 916, 'VERB>NUM>PROPN': 917, 'ADJ>PUNCT>NUM': 918, 'PUNCT>NOUN>PRON': 919, 'ADP>ADP>VERB': 920, 'ADV>ADJ>PROPN': 921, 'PRON>ADV>DET': 922, 'DET>PUNCT>PROPN': 923, 'PUNCT>ADJ>NUM': 924, 'PART>PROPN>NOUN': 925, 'DET>ADV>DET': 926, 'PROPN>ADJ>PUNCT': 927, 'NOUN>VERB>SYM': 928, 'PROPN>NUM>PRON': 929, 'VERB>NOUN>PRON': 930, 'PROPN>ADP>ADV': 931, 'PUNCT>ADJ>DET': 932, 'VERB>PUNCT>NUM': 933, 'NUM>DET>ADJ': 934, 'DET>VERB>PRON': 935, 'CONJ>ADV>NUM': 936, 'CONJ>ADJ>CONJ': 937, 'NOUN>ADJ>DET': 938, 'ADV>ADJ>ADV': 939, 'VERB>PART>PROPN': 940, 'VERB>ADV>PRON': 941, 'NOUN>NUM>ADJ': 942, 'PUNCT>DET>PUNCT': 943, 'NOUN>ADJ>PRON': 944, 'VERB>NUM>NUM': 945, 'NUM>ADJ>VERB': 946, 'PART>PUNCT>VERB': 947, 'ADJ>PROPN>PART': 948, 'PROPN>DET>PROPN': 949, 'PROPN>ADV>ADJ': 950, 'ADV>DET>NUM': 951, 'NOUN>DET>NUM': 952, 'VERB>NUM>ADV': 953, 'NOUN>CONJ>PART': 954, 'ADP>ADJ>PART': 955, 'ADV>DET>ADV': 956, 'PART>PUNCT>CONJ': 957, 'NUM>CONJ>NOUN': 958, 'ADJ>PROPN>NUM': 959, 'PRON>PUNCT>ADP': 960, 'PROPN>PART>PUNCT': 961, 'NUM>VERB>CONJ': 962, 'PRON>CONJ>PROPN': 963, 'PROPN>ADV>PRON': 964, 'VERB>PROPN>ADJ': 965, 'ADV>PUNCT>PART': 966, 'NUM>CONJ>PROPN': 967, 'CONJ>PROPN>NUM': 968, 'PROPN>DET>VERB': 969, 'ADJ>CONJ>ADP': 970, 'PROPN>ADJ>ADJ': 971, 'DET>ADV>NUM': 972, 'NOUN>PROPN>PART': 973, 'NOUN>DET>ADV': 974, 'PUNCT>PRON>ADJ': 975, 'CONJ>NOUN>NUM': 976, 'ADP>CONJ>VERB': 977, 'VERB>PUNCT>PART': 978, 'DET>PUNCT>CONJ': 979, 'NUM>ADP>ADP': 980, 'NOUN>PUNCT>X': 981, 'PRON>ADJ>PUNCT': 982, 'VERB>CONJ>PRON': 983, 'VERB>CONJ>ADP': 984, 'ADP>CONJ>NUM': 985, 'ADP>ADP>PRON': 986, 'ADJ>CONJ>PROPN': 987, 'X>NOUN>PUNCT': 988, 'PRON>ADJ>ADJ': 989, 'NUM>ADP>ADV': 990, 'ADP>CONJ>DET': 991, 'PUNCT>ADJ>PART': 992, 'CONJ>ADP>PUNCT': 993, 'X>X>PUNCT': 994, 'ADV>ADJ>NUM': 995, 'PRON>NOUN>PUNCT': 996, 'NOUN>ADP>X': 997, 'SYM>NUM>NOUN': 998, 'CONJ>ADJ>ADV': 999, 'CONJ>NUM>ADV': 1000, 'CONJ>NOUN>DET': 1001, 'ADP>PRON>PART': 1002, 'PART>ADJ>CONJ': 1003, 'DET>ADP>VERB': 1004, 'PART>ADJ>PROPN': 1005, 'PART>ADV>PUNCT': 1006, 'ADJ>ADV>PART': 1007, 'DET>SYM>NUM': 1008, 'PUNCT>ADV>PART': 1009, 'ADP>DET>CONJ': 1010, 'PUNCT>PRON>CONJ': 1011, 'PRON>PART>PUNCT': 1012, 'PART>NUM>ADJ': 1013, 'NOUN>PRON>ADP': 1014, 'ADV>CONJ>DET': 1015, 'NUM>NOUN>PROPN': 1016, 'DET>CONJ>VERB': 1017, 'PRON>ADJ>PART': 1018, 'DET>X>PUNCT': 1019, 'DET>CONJ>ADJ': 1020, 'NOUN>PUNCT>PUNCT': 1021, 'PART>PROPN>VERB': 1022, 'ADV>PROPN>PART': 1023, 'PRON>ADP>ADP': 1024, 'ADV>CONJ>ADP': 1025, 'CONJ>DET>ADP': 1026, 'CONJ>PUNCT>ADV': 1027, 'PUNCT>PART>NOUN': 1028, 'ADP>CONJ>NOUN': 1029, 'VERB>CONJ>PROPN': 1030, 'PUNCT>PROPN>NUM': 1031, 'ADJ>PART>NOUN': 1032, 'NUM>NOUN>PRON': 1033, 'PRON>PUNCT>ADV': 1034, 'PROPN>PRON>PUNCT': 1035, 'CONJ>ADJ>PART': 1036, 'ADP>PUNCT>CONJ': 1037, 'ADP>ADP>ADV': 1038, 'NOUN>DET>PUNCT': 1039, 'NUM>ADJ>CONJ': 1040, 'NOUN>PRON>DET': 1041, 'ADV>NUM>NUM': 1042, 'PART>ADJ>VERB': 1043, 'NUM>SYM>NUM': 1044, 'PUNCT>PRON>NOUN': 1045, 'ADV>CONJ>ADJ': 1046, 'ADV>NOUN>PART': 1047, 'CONJ>ADP>VERB': 1048, 'CONJ>ADJ>NUM': 1049, 'NUM>PROPN>DET': 1050, 'ADP>X>PUNCT': 1051, 'PUNCT>PRON>PART': 1052, 'PROPN>NOUN>DET': 1053, 'ADV>ADV>PRON': 1054, 'ADJ>NUM>PROPN': 1055, 'CONJ>ADV>PROPN': 1056, 'ADJ>CONJ>NUM': 1057, 'DET>VERB>CONJ': 1058, 'DET>NUM>ADV': 1059, 'ADJ>ADJ>PART': 1060, 'PRON>NUM>ADP': 1061, 'NUM>VERB>PART': 1062, 'ADV>NUM>CONJ': 1063, 'ADJ>PROPN>ADJ': 1064, 'NUM>DET>PROPN': 1065, 'PART>ADV>ADP': 1066, 'DET>ADP>PRON': 1067, 'CONJ>ADP>PRON': 1068, 'NUM>ADV>ADJ': 1069, 'NOUN>DET>ADP': 1070, 'DET>ADP>ADP': 1071, 'PRON>ADP>PRON': 1072, 'NUM>ADJ>ADP': 1073, 'ADJ>PROPN>ADV': 1074, 'ADJ>X>PUNCT': 1075, 'NOUN>PART>CONJ': 1076, 'DET>CONJ>DET': 1077, 'ADJ>ADV>NOUN': 1078, 'PROPN>NUM>PART': 1079, 'PROPN>PROPN>PRON': 1080, 'ADP>ADV>PROPN': 1081, 'NOUN>NUM>DET': 1082, 'PRON>NUM>VERB': 1083, 'VERB>NUM>PART': 1084, 'ADJ>PART>ADJ': 1085, 'CONJ>ADP>ADP': 1086, 'NUM>ADV>ADP': 1087, 'NUM>CONJ>ADP': 1088, 'CONJ>PROPN>DET': 1089, 'PART>DET>PROPN': 1090, 'DET>PRON>VERB': 1091, 'ADJ>ADJ>ADV': 1092, 'PRON>CONJ>DET': 1093, 'ADV>NOUN>ADV': 1094, 'ADV>ADV>PART': 1095, 'PRON>PUNCT>DET': 1096, 'PROPN>NUM>ADJ': 1097, 'CONJ>NUM>CONJ': 1098, 'ADP>ADV>PRON': 1099, 'PROPN>ADJ>PROPN': 1100, 'INTJ>PUNCT>NUM': 1101, 'DET>NUM>CONJ': 1102, 'ADV>PRON>ADV': 1103, 'VERB>PRON>NUM': 1104, 'PRON>PUNCT>PRON': 1105, 'ADP>PRON>ADJ': 1106, 'ADV>CONJ>NOUN': 1107, 'ADJ>DET>PROPN': 1108, 'PRON>ADV>NUM': 1109, 'X>X>X': 1110, 'ADP>CONJ>ADJ': 1111, 'NUM>VERB>PROPN': 1112, 'ADJ>PRON>ADV': 1113, 'PART>NOUN>PRON': 1114, 'PRON>PUNCT>ADJ': 1115, 'NUM>PROPN>PART': 1116, 'ADJ>DET>NUM': 1117, 'ADP>ADV>SYM': 1118, 'NOUN>PROPN>ADV': 1119, 'ADJ>SYM>NUM': 1120, 'ADP>CONJ>PROPN': 1121, 'ADP>PRON>DET': 1122, 'CONJ>PUNCT>NOUN': 1123, 'ADJ>VERB>CONJ': 1124, 'ADP>DET>X': 1125, 'CONJ>ADP>ADV': 1126, 'PRON>PUNCT>NOUN': 1127, 'NOUN>NUM>PRON': 1128, 'NUM>ADJ>PROPN': 1129, 'ADJ>ADJ>DET': 1130, 'VERB>ADV>SYM': 1131, 'PRON>PUNCT>PROPN': 1132, 'NUM>NUM>ADJ': 1133, 'PROPN>PUNCT>PUNCT': 1134, 'ADP>ADP>ADP': 1135, 'DET>DET>PUNCT': 1136, 'NOUN>SYM>NUM': 1137, 'ADV>ADP>CONJ': 1138, 'PRON>DET>ADV': 1139, 'PRON>ADP>ADV': 1140, 'ADP>DET>PART': 1141, 'ADV>ADV>PROPN': 1142, 'CONJ>PRON>CONJ': 1143, 'ADP>ADV>PART': 1144, 'PART>ADJ>NUM': 1145, 'PART>PROPN>CONJ': 1146, 'ADJ>PART>ADV': 1147, 'PRON>NOUN>CONJ': 1148, 'NOUN>ADP>PART': 1149, 'PUNCT>PROPN>ADJ': 1150, 'PUNCT>X>PUNCT': 1151, 'PROPN>ADV>NUM': 1152, 'CONJ>ADV>PRON': 1153, 'NOUN>PART>DET': 1154, 'NOUN>X>NOUN': 1155, 'NOUN>NUM>PART': 1156, 'NUM>VERB>PRON': 1157, 'DET>NUM>NUM': 1158, 'PUNCT>INTJ>PUNCT': 1159, 'PART>PUNCT>DET': 1160, 'X>X>NOUN': 1161, 'PART>NOUN>NUM': 1162, 'PART>NUM>ADP': 1163, 'CONJ>PUNCT>VERB': 1164, 'PROPN>PART>CONJ': 1165, 'ADJ>DET>VERB': 1166, 'NUM>PUNCT>PART': 1167, 'PUNCT>NUM>ADV': 1168, 'PUNCT>VERB>SYM': 1169, 'PROPN>PART>ADP': 1170, 'PART>PUNCT>PROPN': 1171, 'CONJ>PROPN>ADJ': 1172, 'PUNCT>CONJ>PART': 1173, 'ADJ>DET>PUNCT': 1174, 'ADV>NOUN>ADJ': 1175, 'PART>ADJ>ADP': 1176, 'PUNCT>PART>PUNCT': 1177, 'ADV>NUM>PROPN': 1178, 'SYM>NUM>CONJ': 1179, 'NOUN>ADJ>NUM': 1180, 'PRON>PRON>VERB': 1181, 'DET>ADP>ADV': 1182, 'PROPN>ADJ>CONJ': 1183, 'ADP>DET>PRON': 1184, 'PRON>DET>VERB': 1185, 'PROPN>ADV>PART': 1186, 'PROPN>ADV>NOUN': 1187, 'PART>ADP>VERB': 1188, 'NUM>ADV>DET': 1189, 'DET>DET>ADP': 1190, 'PROPN>NOUN>NUM': 1191, 'PROPN>CONJ>PUNCT': 1192, 'ADJ>CONJ>PRON': 1193, 'PROPN>CONJ>PRON': 1194, 'NOUN>PROPN>ADJ': 1195, 'CONJ>ADJ>DET': 1196, 'ADV>DET>PUNCT': 1197, 'PRON>ADV>NOUN': 1198, 'CONJ>ADV>PART': 1199}



```python
def textToTrigrams(text): 
    return trigramsToDictKeys(getPOSTrigramsForTextString(text))

def text_to_vector(text):
    wordVector = np.zeros(len(vocab))
    for word in textToTrigrams(text):
        index = word2idx.get(word, None)
        if index != None:
            wordVector[index] += 1
    return wordVector
```


```python
text_to_vector('The tea is for a party to celebrate '
               'the movie so she has no time for a cake')[:65]
```




    array([ 2.,  1.,  0.,  0.,  2.,  0.,  0.,  0.,  0.,  0.,  2.,  0.,  1.,
            1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,
            0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,
            0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  1.,  0.,
            0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.])




```python
word_vectors = np.zeros((len(texts), len(vocab)), dtype=np.int_)
for ii, text in enumerate(texts):
    word_vectors[ii] = text_to_vector(text)
```


```python
# Printing out the first 5 word vectors
word_vectors[:5, :23]
```




    array([[0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]])



### Chunking the data for TF


```python
records = len(labels)
test_fraction = 0.9

train_split, test_split = int(records*test_fraction), int(records*test_fraction)
print(train_split, test_split)
trainX, trainY = word_vectors[:train_split], to_categorical(labels[:train_split], 2)
testX, testY = word_vectors[test_split:], to_categorical(labels[test_split:], 2)
```

    106133 106133



```python
trainX[-1], trainY[-1]
```




    (array([0, 0, 0, ..., 0, 0, 0]), array([ 1.,  0.]))




```python
len(trainY), len(testY), len(trainY) + len(testY)
```




    (106133, 11793, 117926)



# Setting up TF


```python
# Network building
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
```

### Initialize


```python
model = build_model()
```

### Training


```python
# Training
model.fit(trainX, trainY, validation_set=0.1, show_metric=True, batch_size=128, n_epoch=50)
```

    Training Step: 37349  | total loss: [1m[32m0.06514[0m[0m | time: 4.271s
    | SGD | epoch: 050 | loss: 0.06514 - acc: 0.9771 -- iter: 95488/95519
    Training Step: 37350  | total loss: [1m[32m0.06288[0m[0m | time: 5.318s
    | SGD | epoch: 050 | loss: 0.06288 - acc: 0.9770 | val_loss: 0.67039 - val_acc: 0.8444 -- iter: 95519/95519
    --



```python
# Testing
predictions = (np.array(model.predict(testX))[:,0] >= 0.5).astype(np.int_)
test_accuracy = np.mean(predictions == testY[:,0], axis=0)
print("Test accuracy: ", test_accuracy)
```

    Test accuracy:  0.845331976596


### Playground


```python
def test_sentence(sentence):
    positive_prob = model.predict([text_to_vector(sentence)])[0][1]
    print('Sentence: {}'.format(sentence))
    print('P(positive) = {:.3f} :'.format(positive_prob), 
          'Positive' if positive_prob > 0.5 else 'Negative')
```


```python
test_sentence("Even though he had the better arguments and was by far the more powerful speaker.")
```

    Sentence: Even though he had the better arguments and was by far the more powerful speaker.
    P(positive) = 0.000 : Negative



```python
test_sentence("Even though he had the better arguments and was by far the more powerful speaker, Peter lost the debate.")
```

    Sentence: Even though he had the better arguments and was by far the more powerful speaker, Peter lost the debate.
    P(positive) = 1.000 : Positive



```python
test_sentence("Working far into the night in an effort to salvage her little boat.")
```

    Sentence: Working far into the night in an effort to salvage her little boat.
    P(positive) = 0.000 : Negative



```python
test_sentence("She was working far into the night in an effort to salvage her little boat.")
```

    Sentence: She was working far into the night in an effort to salvage her little boat.
    P(positive) = 0.024 : Negative



```python
test_sentence("The man eating pizza.")
```

    Sentence: The man eating pizza.
    P(positive) = 0.324 : Negative



```python
test_sentence("The man eating pizza is overwieght.")
```

    Sentence: The man eating pizza is overwieght.
    P(positive) = 0.133 : Negative



```python
test_sentence("While we were swimming at the lake.")
```

    Sentence: While we were swimming at the lake.
    P(positive) = 0.023 : Negative



```python
test_sentence("While we were swimming at the lake, we saw a fish.")
```

    Sentence: While we were swimming at the lake, we saw a fish.
    P(positive) = 0.970 : Positive



```python
test_sentence("Keep going.")
```

    Sentence: Keep going.
    P(positive) = 0.000 : Negative



```python
test_sentence("A time of wonder and amazement")
```

    Sentence: A time of wonder and amazement
    P(positive) = 0.002 : Negative



```python
test_sentence("That was a time of wonder and amazement")
```

    Sentence: That was a time of wonder and amazement
    P(positive) = 0.050 : Negative



```python
test_sentence("Since she never saw that movie.") 
```

    Sentence: Since she never saw that movie.
    P(positive) = 0.048 : Negative



```python
test_sentence("We should invite her, since she never saw that movie.")
```

    Sentence: We should invite her, since she never saw that movie.
    P(positive) = 0.976 : Positive



```python
test_sentence("Affecting the lives of many students in New York City.")
```

    Sentence: Affecting the lives of many students in New York City.
    P(positive) = 0.038 : Negative



```python
test_sentence("Quill is affecting the lives of many students in New York City.")
```

    Sentence: Quill is affecting the lives of many students in New York City.
    P(positive) = 0.993 : Positive



```python
test_sentence("Standing on the edge of the cliff looking down.")
```

    Sentence: Standing on the edge of the cliff looking down.
    P(positive) = 0.003 : Negative



```python
test_sentence("I'm standing on the edge of the cliff and looking down.")
```

    Sentence: I'm standing on the edge of the cliff and looking down.
    P(positive) = 0.889 : Positive



```python
test_sentence("The storm raging outside my window.")
```

    Sentence: The storm raging outside my window.
    P(positive) = 0.025 : Negative



```python

```


```python

```
