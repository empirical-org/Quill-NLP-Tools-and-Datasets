import os

with open('participlePhraseSentencesAndTheirFragments.txt', 'a+') as \
        output_file:
    for f in os.listdir('fragments'):
        input_filename = os.fsdecode(f)
        if input_filename.startswith('participlePhrasesFrom'):
            with open('fragments/' + input_filename, 'r') as input_file:
                print(input_filename)
                for i, line in enumerate(input_file):
                    if i % 8 == 0 or i % 8 == 1:
                        output_file.write(line)


