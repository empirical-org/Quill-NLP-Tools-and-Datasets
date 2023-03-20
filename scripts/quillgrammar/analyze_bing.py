import csv
import ast
import random

from collections import Counter


grammar_file_without_bing = 'dataset102121_sentences_grammar.csv'
grammar_file_with_bing = 'dataset102121_sentences_bing_grammar.csv'

fragment_file_without_bing = 'dataset102121_sentences_fragments.csv'
fragment_file_with_bing = 'dataset102121_sentences_bing_fragments_fine_noise_cleaned.csv'

def count_bing_errors():
    num_errors = []
    with open('dataset102121_sentences_bing.csv') as i:
        reader = csv.reader(i, delimiter='\t')

        for line in reader:
            sentence = line[0]
            response = line[-1]

            response_json = ast.literal_eval(response)
            print(response_json)
            current_num_errors = len(response_json.get('flaggedTokens', []))
            num_errors.append(current_num_errors)


    print(Counter(num_errors))


def read_grammar_file(f):
    data = []
    with open(f) as i:
        reader = csv.reader(i, delimiter='\t')
        for line in reader:
            prompt, sentence, error = line[:3]
            error_name = error.split("(")[0]
            data.append((sentence, error_name))

    return data


def read_fragment_file(f):
    data = []
    with open(f) as i:
        reader = csv.reader(i, delimiter='\t')
        for line in reader:
            sentence = line[0]
            label = line[3]
            data.append((sentence, label))

    return data


def count_grammar_differences():

    data_without_bing = read_grammar_file(grammar_file_without_bing)
    data_with_bing = read_grammar_file(grammar_file_with_bing)

    assert len(data_with_bing) == len(data_without_bing)

    same = 0
    differences = []
    num_grammar_errors_without_bing = 0
    num_grammar_errors_with_bing = 0

    for item_without_bing, item_with_bing in zip(data_without_bing, data_with_bing):
        error_without_bing = item_without_bing[1]
        error_with_bing = item_with_bing[1]

        if error_without_bing.strip():
            num_grammar_errors_without_bing += 1
        if error_with_bing.strip():
            num_grammar_errors_with_bing += 1

        if error_without_bing == error_with_bing:
            same += 1
        else:
            differences.append(f'{error_without_bing} => {error_with_bing}')

    print(same)
    print(len(data_without_bing))

    differences_counter = Counter(differences)

    for x in differences_counter.most_common(100):
        print(x)

    print('Grammar errors without Bing', num_grammar_errors_without_bing)
    print('Grammar errors with Bing', num_grammar_errors_with_bing)


def count_fragment_differences():
    data_without_bing = read_fragment_file(fragment_file_without_bing)
    data_with_bing = read_fragment_file(fragment_file_with_bing)

    assert len(data_with_bing) == len(data_without_bing)

    same = 0
    differences = []
    different_outputs = []
    num_fragment_errors_without_bing = 0
    num_fragment_errors_with_bing = 0

    for item_without_bing, item_with_bing in zip(data_without_bing, data_with_bing):
        label_without_bing = item_without_bing[1]
        label_with_bing = item_with_bing[1]

        if label_without_bing == 'Fragment':
            num_fragment_errors_without_bing += 1
        if label_with_bing == 'Fragment':
            num_fragment_errors_with_bing += 1

        if label_without_bing == label_with_bing:
            same += 1
        else:
            differences.append(f'{label_without_bing} => {label_with_bing}')
            different_outputs.append((item_without_bing[0], label_without_bing, item_with_bing[0], label_with_bing))

    print(same)
    print(len(data_without_bing))

    differences_counter = Counter(differences)

    for x in differences_counter.most_common(100):
        print(x)

    print('Fragments without Bing', num_fragment_errors_without_bing)
    print('Fragments with Bing', num_fragment_errors_with_bing)

    random.shuffle(different_outputs)
    
    with open('fragment_differences.csv', 'w') as o:
        writer = csv.writer(o, delimiter='\t')
        for item in different_outputs:
            writer.writerow(item)



count_grammar_differences()
