"""Given a text, find sentences that might have a participle phrase in them and
write them to a new file."""
import os
import spacy

# Constants
IRREGULAR_PAST_PARTICIPLES_FILE = \
'sentence_parts/irregularPastParticipleVerbs.txt'
INPUT_TEXT_FILE = 'books/around-the-world-in-80-days.txt'
INPUT_TEXT_FILE = 'books/the-black-arrow.txt'
INPUT_TEXT_FILE = 'books/the-princess-of-the-school.txt'
# INPUT_TEXT_FILE = 'books/test.txt'
OUTPUT_TEXT_FILE_BASE = 'fragments/participlePhrasesFrom{}'
OUTPUT_TEXT_FILE = OUTPUT_TEXT_FILE_BASE.format(INPUT_TEXT_FILE.split('/')[-1])
CHUNK_SIZE = 1024
nlp = spacy.load('en')

with open(IRREGULAR_PAST_PARTICIPLES_FILE, 'r') as ipp2:
    past_participle_irregular_verbs = [word2.strip() for word2 in ipp2]

def read_in_chunks(file_object, chunk_size=CHUNK_SIZE):
    """Generator to read a file piece by piece."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def is_participle(word):
    """Return True or False"""
    result = False
    if word.suffix_ == 'ing':
        result = True
    elif word.suffix_.endswith('ed'):
        result = True
    elif str(word) in past_participle_irregular_verbs:
        result = True
    return result

def participle_phrase_conditions_apply(possible_participle_phrase, participle,
        sentence):
    """Return True if this phrase might be a participle phrase"""
    doc = nlp(possible_participle_phrase)

    # introduces a main clause
    if possible_participle_phrase[0].isupper():
        # followed by preposition or subordinating conjunction
        if len(doc) > 1 and doc[1].tag_ == 'IN':
            # participles ending with 'ed' require more attention
            if participle.endswith('ing'):
                return True

    # concludes a main clause modifying a word farther up the sentence
    elif sentence.split(participle)[0].endswith(', '):
        # ie. Cooper enjoyed dinner at Audrey's house, agreeing to a large slice of
        # cherry pie even though he was full to the point of bursting.
        if len(doc) > 1 and doc[1].tag_ == 'IN':
            # participles ending with 'ed' require more attention
            if participle.endswith('ing'):
                return True

    # concludes a main clause modifying word directly in front of it
    else:
        # ie. Mariah risked petting the pit bull wagging its stub tail.
        # NOTE: we ignore these because they are rarely participle clauses
        pass
    return False

def split_text_at_verb_or_adverb_follwing_comma(sentence, participle):
    """Given a sentence that might include a paticiple phrase in the middle,
    determine where the participle phrase ends, and return the phrase"""
    full = participle + sentence.split(participle, 1)[1]
    result = participle + sentence.split(participle, 1)[1].split(',')[0]
    if len(full.split(',')) < 2:
        return result # this one is easy

    for part in full.split(',')[1:]:
        doc = nlp(part.strip())
        # do not include vbg verbs 
        if (doc and len(doc) > 0 and doc[0].tag_ in ['RB', 'RBR', 'RBS', 'VB',
            'VBD', 'VBN', 'VBP', 'VBZ', 'NN', 'NNPS', 'NNS', 'NNP', 'PRP',
            'PRP$', 'DET', 'JJ']):
            break
        else:
            # append more to the phrase
            result += ',' + part

    return result


def split_text_at_noun_pronoun_determiner_following_comma(sentence):
    """Given a sentence that might begin with a participle phrase,
    determine where the participle phrase ends, and return the phrase"""
    result = sentence.split(',')[0]
    if len(sentence.split(',')) < 2:
        return result

    for part in sentence.split(',')[1:]:
        doc = nlp(part.strip())
        if (doc and len(doc) > 0 and doc[0].tag_ in ['NN', 'NNPS', 'NNS', 'NNP',
            'PRP', 'PRP$', 'DET', 'JJ']) or (doc and len(doc) > 0 and
                    str(doc[0])[0].isupper()):
            break
        else:
            # append more to the phrase
            result += ',' + part

    return result



def has_participle_phrase(sentence):
    """Return participle phrase object or None
    participle phrase object
    {'phrase': 'spoiling her', 'flagged': False, 'participle': 'spoiling'}

    an object can be flagged if it may need further review
    """
    phrase = None
    flagged = False
    participle = ''
    doc = nlp(sentence)
    has_participle = False
    for i, word in enumerate(doc):
        if is_participle(word):
            participle = str(word)
            has_participle = True
            break
    if has_participle:
        # if participle is first word, stop the phrase at the first noun,
        # pronoun, or determiner that directly follows a comma
        if i == 0:
            phrase = split_text_at_noun_pronoun_determiner_following_comma(sentence)
            # phrase = sentence.split(',')[0]
            # this method risks splitting partial participle phrases so
            # sentencese with multiple commas are automatically flagged.
            # see test sentence 4
            if len(sentence.split(',')) > 2:
                flagged = True
        else:
            """" All included," returned Phileas Fogg, continuing to play despite
            the discussion."""
            phrase = split_text_at_verb_or_adverb_follwing_comma(sentence,
                    participle)
            # phrase = participle + sentence.split(participle, 1)[1]
            # this method risks including too much when a participle phrase
            # stretches on for a while so these are flagged
            # see test sentence 1
            if len(sentence.split(',')) > 2:
                flagged = True

    if phrase and participle_phrase_conditions_apply(phrase, participle,
            sentence):
        return {'phrase': phrase, 'participle':participle, 'flagged': flagged}
    return None

def write_sentences_with_participle_prhases():
    """Write participle phrase file"""
    with open(INPUT_TEXT_FILE, 'r') as f:
        # final sentence may not be a complete sentence, save and prepend to next chunk
        leftovers = ''
        sentence_no = 0
        output = open(OUTPUT_TEXT_FILE.format(INPUT_TEXT_FILE), 'w+')
        for chunk in read_in_chunks(f): # lazy way of reading our file in case it's large
            # prepend leftovers to chunk
            chunk = leftovers + chunk
            doc = nlp(chunk)

            # last sentence may not be sentence, move to next chunk
            sents = [sent.string.strip() for sent in doc.sents]
            if len(sents) > 1:
                sents = sents[:-1]
                leftovers = sents[-1]
            for sent in sents:
                sent = sent.replace('\n', ' ')
                phrase = has_participle_phrase(sent)
                if phrase:
                    output.write("{}\n{}\n{}\n" \
                    "{}\n\n\n\n\n".format(sent, phrase['phrase'],
                        phrase['participle'], phrase['flagged']))
        output.close()


if __name__ == '__main__':
    write_sentences_with_participle_prhases()
