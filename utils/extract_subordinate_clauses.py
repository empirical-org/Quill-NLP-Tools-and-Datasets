import os
import sys
import spacy
nlp = spacy.load('en')

# Constants
OUTPUT_FOLDER = '../data/fragments/subordinate-clauses'
OUTPUT_TEXT_FILE_BASE = OUTPUT_FOLDER + '/subordinateClausesFrom{}'
CHUNK_SIZE = 1024

# TODO: read in chunks is a shared helper method
def _read_in_chunks(file_object, chunk_size=CHUNK_SIZE):
    """Generator to read a file piece by piece."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def _document_has_subordinating_conj(doc):
    """Takes a spacy nlp document and returns a True if the document contains a
    subordinate conjunction; else false"""
    for word in doc:
        if word.tag_ == 'IN':
            return True
    return False


def _extract_subordinate_clause_type1(sentence):
    """Return subordinate clause tuple from sentence with subordinate clause at
    the beginning of the sentence."""
    subordinate_clause = ''
    subordinating_conj = None
    flagged = False
    for clause in sentence.split(','):
        clause = clause.strip()
        doc = nlp(clause)
        if len(doc) < 1:
            break
        if not subordinating_conj and doc[0].tag_ == 'IN':
            subordinating_conj = str(doc[0])
            subordinate_clause += clause
        elif subordinating_conj and doc[0].tag_ not in ['NN', 'NNS', 'NNP', 'NNPS', 'DT',
                'JJ', 'JJR', 'JJS', 'PRP', 'PRP$']:
            subordinate_clause += ', ' + clause
            flagged = True
        elif subordinating_conj:
            break # clause followed by main clause
    return subordinate_clause, subordinating_conj, flagged


def _extract_subordinate_clause_type2(sentence):
    """Return subordinate clause tuple from sentence with subordiante clause at
    the end or middle of sentence. If the subordinating conj is not the first
    word after a comma, the subordinating conjunction returned will be None.  If
    this occurs, _extract_subordinate_clause_type3 should be attempted."""
    subordinate_clause = ''
    subordinating_conj = None
    flagged = False
    for clause in sentence.split(','):
        clause = clause.strip()
        doc = nlp(clause)
        if len(doc) < 1:
            break
        if not subordinating_conj and doc[0].tag_ == 'IN':
            subordinating_conj = str(doc[0])
            subordinate_clause += clause
        elif subordinating_conj and doc[0].tag_ not in ['RB', 'RBR', 'RBS',
                'VB', 'VBG', 'VBS', 'VBN', 'VBP', 'VBZ']:
            subordinate_clause += ', ' + clause
            flagged = True
        elif subordinating_conj:
            break # clause followed by main clause
    return subordinate_clause, subordinating_conj, flagged

def _extract_subordinate_clause_type3(sentence):
    """Return subordinate clause tuple from sentence with subordinate clause in
    the middle of a sentence and not directly after a comma.
    
    Note: using this method on setences that are not sure to have a subordinate
    conj will give you trash results.
    """
    # Diane decided to plant tomatoes in the back of the yard where the sun
    # blazed the longest during the day.
    doc = nlp(sentence)
    for word in doc:
        if word.tag_ == 'IN':
            break # print(word) => where
    result = str(word) + sentence.split(str(word))[1] # print(result) => where
    # the sun blazed the longest during the day.
    result = result.split(',')[0]
    result = result.split('.')[0]
    subordinate_clause, subordinate_conj, flagged = result, word, False
    
    return subordinate_clause, subordinate_conj, flagged  

    

def has_subordinate_clause(sentence):
    '''If this has a subordiate clause return an object with the clause,
    subordinate conjuction, and whether or not it is 'flagged' for review'''
    result = {'clause': '', 'subordinating_conj': '', 'flagged': False}
    sentence = sentence.strip()
    # Short circuit questions
    if len(sentence) == 0 or sentence[-1] == '?':
        return None

    # TODO: does not cover clauses that begin with a relative (WP, WP$) pronoun
    
    # If sentence begins with subordinating conjuction:
    # Start at subordinating conj and end with period or
    # a comma followed by a noun/pronoun/adj/determiner
    # ie. Until the end of time, he would love her.
    #     becomes,
    #     Until the end of time
    # NOTE: With short introductory phrases, a comma is not always used. 
    # For example,
    # > After the holidays the girls went to the Blackheath High School.
    # is a sentence that might be found in a book, still, we believe it would be
    # better with a comma after holidays and would suggest the student add one.
    #
    # If subordinating conj is in the middle of the sentence and after a comma:
    # Start at subordinating conj and end with period or comma followed by
    # adverb/verb/
    # ie. Peter, with heroic unselfishness, did not say anything.
    #     becomes,
    #     with heroic unselfishness
    #
    # If the subordinating conj in the middle of a sentence and not after a
    # comma:
    # Start at the subordinating conjunction and end with the first comma or
    # period.
    # ie. Jonathon spent his class time reading comic books since his average
    #     was a 45 one week before final exams.
    #     becomes,
    #     since his average was a 45 one week before final exams.
    

    doc = nlp(sentence)
    if doc[0].tag_ == 'IN':
        subordinate_clause, subordinating_conj, flagged =  _extract_subordinate_clause_type1(sentence)
    elif _document_has_subordinating_conj(doc):
        subordinate_clause, subordinating_conj, flagged =  _extract_subordinate_clause_type2(sentence)
        if not subordinating_conj:
            _extract_subordinate_clause_type3(sentence)
    else:
        subordinating_conj = None
            
    if subordinating_conj:
        result['clause'] = subordinate_clause
        result['subordinating_conj'] = subordinating_conj
        result['flagged'] = flagged
    else:
        result = None

    return result

def write_sentences_with_subordinate_clauses(input_filename, output_filename):
    '''extract sentences with subordinate clauses and write them'''
    # open a working copy of the file to show its currently being written to
    with open(input_filename, 'r') as f:
        # final sentence may not be a complete sentence, save and prepend to next chunk
        leftovers = ''
        sentence_no = 0
        output = open(output_filename + '.working', 'w+')
        for chunk in _read_in_chunks(f): # lazy way of reading our file in case it's large
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
                clause = has_subordinate_clause(sent)
                if clause:
                    print(clause['clause'])
                    output.write("{}\n{}\n{}\n" \
                    "{}\n\n\n\n\n".format(sent, clause['clause'],
                        clause['subordinating_conj'], clause['flagged']))
        output.close()
        # remove the .working extention to show the file is finished
        os.rename(output_filename + '.working', output_filename)

def print_help():
    print('./extract_subordinate_clauses.py -f filename')
    print('to index a file')
    print('to extract subordinate clauses from a file,')
    print('or')
    print('./extract_subordinate_clauses.py -d directory')
    print('to extract subordinate clauses from each file in a directory')
    print('')

if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == '-d':
        existing_books = [OUTPUT_FOLDER + '/' + os.fsdecode(f1) for f1 in os.listdir(OUTPUT_FOLDER)]
        directory_name = sys.argv[2]
        for f in os.listdir(directory_name):
            # TODO: below line should use a proper path joiner
            input_filename = directory_name + '/' + os.fsdecode(f)
            output_filename = OUTPUT_TEXT_FILE_BASE.format(input_filename.split('/')[-1])
            if output_filename not in existing_books:
                try:
                    write_sentences_with_subordinate_clauses(input_filename,
                       output_filename)
                    print('Done extracting subordinate clauses from \
                            {}'.format(input_filename))
                except Exception as e:
                    print('error on {}'.format(input_filename))
                    print(e)
                    print('closing file and continuing')
                    os.rename(output_filename + '.working', output_filename)
                    print('...')

    elif len(sys.argv) >= 3 and sys.argv[1] == '-f':
        input_filename = sys.argv[2]
        output_filename = OUTPUT_TEXT_FILE_BASE.format(input_filename.split('/')[-1])
        print(input_filename, output_filename)
        write_sentences_with_subordinate_clauses(input_filename, output_filename)
    else:
        print_help()
