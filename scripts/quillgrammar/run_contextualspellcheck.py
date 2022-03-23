import time

from tqdm import tqdm

import contextualSpellCheck
import spacy

nlp = spacy.load("en")
contextualSpellCheck.add_to_pipe(nlp)


input_file = "/home/yves/projects/Quill-NLP-Tools-and-Datasets/quillgrammar/data/new_turk_data.csv"

with open(input_file) as i:
    lines = i.readlines()

corrected = 0
total = 0

start = time.time()
for line in tqdm(lines):
    input_sentence = line.strip()
    doc = nlp(input_sentence)
    output_sentence = doc._.outcome_spellCheck

    if doc._.performed_spellCheck and input_sentence != output_sentence:
        corrected += 1
        print(input_sentence)
        print(output_sentence)
        input()
    total += 1

end = time.time()
total_time = end - start

print(f"{corrected}/{total}={corrected / total * 100}% sentences corrected")
print(f"{total}/{total_time}={total / total_time} sentences/second")