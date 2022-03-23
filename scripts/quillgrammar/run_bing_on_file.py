import csv
import time

from tqdm import tqdm

from quillnlp.spelling.bing import correct_sentence_with_bing

input_file = "quillgrammar/data/new_turk_data.txt"
output_file = "new_turk_data_bing.csv"

with open(input_file) as i:
    sentences = [line.strip() for line in i]

with open(output_file, "w") as csv_out:
    writer = csv.writer(csv_out, delimiter="\t")
    for row in tqdm(sentences):

        sentence = row.strip()
        correct_sentence, response, output = correct_sentence_with_bing(sentence)
        writer.writerow([correct_sentence, str(response), output])
