import time

from tqdm import tqdm

from autocorrect import Speller

checker = Speller("en")

input_file = "/home/yves/projects/Quill-NLP-Tools-and-Datasets/quillgrammar/data/new_turk_data.csv"

with open(input_file) as i:
    lines = i.readlines()

corrected = 0
total = 0

start = time.time()
for line in tqdm(lines):
    input_sentence = line.strip()
    output_sentence = checker(input_sentence).strip()

    if input_sentence != output_sentence:
        print(input_sentence)
        print(output_sentence)
        corrected += 1
        input()
    total += 1
    

end = time.time()
total_time = end-start

print(f"{corrected}/{total}={corrected/total*100}% sentences corrected")
print(f"{total}/{total_time}={total/total_time} sentences/second")