import os
import sys
import spacy
nlp = spacy.load('en')

# Constants
OUTPUT_FOLDER = 'fragments'
OUTPUT_TEXT_FILE_BASE = OUTPUT_FOLDER + '/participlePhrasesFrom{}'
CHUNK_SIZE = 1024

def has_subordinate_clause(text):
    '''If this has a subordiate clause return an object with the clause,
    subordinate conjuction, and whether or not it is 'flagged' for review'''
    result = {'clause':'', 'subordinating_conj':'', 'flagged':False}
    # do things here
    return result

def write_sentences_with_subordinate_clauses(input_filename, output_filename):
    '''extract sentences with subordinate clauses and write them'''
    # open a working copy of the file to show its currently being written to
    with open(input_file, 'r') as f:
        # final sentence may not be a complete sentence, save and prepend to next chunk
        leftovers = ''
        sentence_no = 0
        output = open(output_file + '.working', 'w+')
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
                clause = is_subordinate_clause(sent)
                if clause:
                    output.write("{}\n{}\n{}\n" \
                    "{}\n\n\n\n\n".format(sent, clause['clause'],
                        phrase['subordinating_conj'], clause['flagged']))
        output.close()
        # remove the .working extention to show the file is finished
        os.rename(output_file + '.working', output_file)

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
        write_sentences_with_participle_prhases(input_filename, output_filename)
    else:
        print_help()
