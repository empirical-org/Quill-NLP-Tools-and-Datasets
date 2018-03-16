import os

# dont allow square brackets or special characters that might make a phrase
# appear oddly. Do not allow semi colons, but allow quotation marks (for now)
acceptable_characters = set(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ \
                -.,!?()\'$ *1234567890:&')

with open('participlePhraseSentencesAndTheirFragments.txt', 'w+') as \
        output_file:
    for f in os.listdir('fragments'):
        input_filename = os.fsdecode(f)
        if input_filename.startswith('participlePhrasesFrom') and \
                input_filename.endswith('.txt'):
            with open('fragments/' + input_filename, 'r') as input_file:
                skip_next_line = False
                for i, line in enumerate(input_file):
                    line = " ".join(line.split()) # replace all whitespace w
                    line = line.replace('_', '') # gutenberg underlines words
                    line = line.strip() # trailing whitespace
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
