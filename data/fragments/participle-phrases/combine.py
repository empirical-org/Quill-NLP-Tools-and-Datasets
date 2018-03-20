import os
import sys

# dont allow square brackets or special characters that might make a phrase
# appear oddly. Do not allow semi colons, but allow quotation marks (for now)
acceptable_characters = set(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ \
                -.,!?()\'$ *1234567890:&')

def write_combination_document(input_dir):
    with open(input_dir + '.combined.txt', 'w+') as \
            output_file:
        for f in os.listdir(input_dir):
            input_filename = os.fsdecode(f)
            if input_filename.startswith('participlePhrasesFrom') and \
                    input_filename.endswith('.txt'):
                with open(input_dir + '/' + input_filename, 'r') as input_file:
                    skip_next_line = False
                    for i, line in enumerate(input_file):
                        line = " ".join(line.split()) # replace all whitespace w
                        line = line.replace('_', '') # gutenberg underlines words
                        line = line.strip() # trailing whitespace
                        if line and line[-1] not in list('.!?'): # punctuate 
                            line += '.'
                           
                        if line:
                            line = line[0].capitalize() + line[1:] # capitalize 

                        if skip_next_line:
                            skip_next_line = False
                            continue
                        if i % 8 != 0 and i % 8 != 1:
                            continue
                        if not set(line).issubset(acceptable_characters) and i % 8 \
                                == 0:
                            skip_next_line = True
                            continue
                        # Do some cleanup on the line
                        # sing space
                        output_file.write(line + '\n')

def print_help():
    print('HELP:')
    print('')
    print('./combine.py INPUT_DIR')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1][-1] == '/':
            raise Exception('remove trailing slash from directory name')
        write_combination_document(sys.argv[1])
    else:
        print_help()
