import csv
import random

f_without_bing = 'dataset102121_sentences_grammar.csv'
f_with_bing = 'dataset102121_sentences_bing_grammar.csv'


def read_csv(f):
    data = []
    with open(f) as i:
        reader = csv.reader(i, delimiter='\t')
        for line in reader:
            if len(line):
                data.append((line[1], line[2]))       

    return data

data_without_bing = read_csv(f_without_bing)
data_with_bing= read_csv(f_with_bing)

different = []
for item_without_bing, item_with_bing in zip(data_without_bing, data_with_bing):
    error_without_bing = item_without_bing[1]
    error_with_bing = item_with_bing[1]

    error_name_without_bing = error_without_bing.split('(')[0]
    error_name_with_bing = error_with_bing.split('(')[0]

    if error_name_without_bing != error_name_with_bing:
        different.append((item_without_bing[0], error_without_bing, item_with_bing[0], error_with_bing))


random.shuffle(different)

with open('different.csv', 'w') as o:
    writer = csv.writer(o, delimiter='\t')
    for item in different:
        writer.writerow(item)
        